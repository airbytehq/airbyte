/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.write.typing_deduping

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryError
import com.google.cloud.bigquery.BigQueryException
import com.google.cloud.bigquery.Job
import com.google.cloud.bigquery.JobConfiguration
import com.google.cloud.bigquery.JobId
import com.google.cloud.bigquery.JobInfo
import com.google.cloud.bigquery.JobStatistics
import com.google.cloud.bigquery.JobStatus
import com.google.cloud.bigquery.QueryJobConfiguration
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.orchestration.db.DatabaseHandler
import io.airbyte.cdk.load.orchestration.db.Sql
import io.airbyte.cdk.util.ConnectorExceptionUtil
import io.airbyte.integrations.destination.bigquery.BigQueryUtils
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.UUID
import kotlin.math.min
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

private val logger = KotlinLogging.logger {}

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin is hard")
class BigQueryDatabaseHandler(private val bq: BigQuery, private val datasetLocation: String) :
    DatabaseHandler {
    /**
     * Some statements (e.g. ALTER TABLE) have strict rate limits. Bigquery recommends retrying
     * these statements with exponential backoff, and the SDK doesn't do it automatically. So this
     * function implements a basic retry loop.
     *
     * Technically, [statement] can contain multiple semicolon-separated statements. That's probably
     * not a great idea (it's hard to reason about retrying partially-successful statements), so
     * maybe don't do that. Just call this function multiple times.
     */
    suspend fun executeWithRetries(
        statement: String,
        initialDelay: Long = 1000,
        numAttempts: Int = 5,
        maxDelay: Long = 60,
    ) {
        var delay = initialDelay
        for (attemptNumber in 1..numAttempts) {
            try {
                execute(Sql.of(statement))
                return
            } catch (e: Exception) {
                // you might think that `e.isRetryable` would be useful here,
                // and you would be wrong - presumably the SDK treats all 403 errors as
                // nonretryable.
                // instead, we hardcode handling for the rate-limit error... which requires matching
                // against a specific magic string >.>
                if (
                    e is BigQueryException && e.code == 403 && e.error.reason == "rateLimitExceeded"
                ) {
                    logger.warn(e) {
                        "Rate limit exceeded while executing SQL (attempt $attemptNumber/$numAttempts). Sleeping ${delay}ms and retrying."
                    }
                    val withJitter = delay + 1000 * Math.random()
                    delay(withJitter.toLong())
                    delay = min(delay * 2, maxDelay)
                } else {
                    logger.error(e) {
                        "Caught exception while executing SQL (attempt $attemptNumber/$numAttempts). Not retrying."
                    }
                    throw wrapWithConfigExceptionIfNeeded(e)
                }
            }
        }
    }

    @Throws(InterruptedException::class)
    override fun execute(sql: Sql) {
        val transactions = sql.asSqlStrings("BEGIN TRANSACTION", "COMMIT TRANSACTION")
        if (transactions.isEmpty()) {
            return
        }
        val queryId = UUID.randomUUID()
        val statement = java.lang.String.join("\n", transactions)
        logger.debug { "Executing sql $queryId: $statement" }

        val job = runQueryWithTransientRetries(queryId, statement)

        val statistics = job.getStatistics<JobStatistics.QueryStatistics>()
        logger.debug {
            "Root-level job $queryId completed in ${statistics.endTime - statistics.startTime} ms; processed ${statistics.totalBytesProcessed} bytes; billed for ${statistics.totalBytesBilled} bytes"
        }

        // SQL transactions can spawn child jobs, which are billed individually. Log their stats
        // too.
        if (statistics.numChildJobs != null) {
            // There isn't (afaict) anything resembling job.getChildJobs(), so we have to ask bq for
            // them
            bq.listJobs(BigQuery.JobListOption.parentJobId(job.jobId.job))
                .iterateAll()
                .sortedBy { it.getStatistics<JobStatistics>().endTime }
                .forEach { childJob: Job ->
                    val configuration = childJob.getConfiguration<JobConfiguration>()
                    if (configuration is QueryJobConfiguration) {
                        val childQueryStats =
                            childJob.getStatistics<JobStatistics.QueryStatistics>()
                        var truncatedQuery: String =
                            configuration.query
                                .replace("\\s+".toRegex(), " ")
                                .substring(
                                    0,
                                    min(100.0, configuration.query.length.toDouble()).toInt()
                                )
                        if (truncatedQuery != configuration.query) {
                            truncatedQuery += "..."
                        }
                        logger.debug {
                            "Child sql $truncatedQuery completed in ${childQueryStats.endTime - childQueryStats.startTime} ms; processed ${childQueryStats.totalBytesProcessed} bytes; billed for ${childQueryStats.totalBytesBilled} bytes"
                        }
                    } else {
                        // other job types are extract/copy/load
                        // we're probably not using them, but handle just in case?
                        val childJobStats = childJob.getStatistics<JobStatistics>()
                        logger.debug {
                            "Non-query child job (${configuration.type}) completed in ${childJobStats.endTime - childJobStats.startTime} ms"
                        }
                    }
                }
        }
    }

    override suspend fun createNamespaces(namespaces: Collection<String>) {
        coroutineScope {
            namespaces.forEach { dataset ->
                launch {
                    logger.info { "Creating dataset if not present $dataset" }
                    try {
                        BigQueryUtils.getOrCreateDataset(bq, dataset, datasetLocation)
                    } catch (e: BigQueryException) {
                        if (
                            ConnectorExceptionUtil.HTTP_AUTHENTICATION_ERROR_CODES.contains(e.code)
                        ) {
                            throw ConfigErrorException(e.message!!, e)
                        } else {
                            throw e
                        }
                    }
                }
            }
        }
    }

    private fun wrapWithConfigExceptionIfNeeded(e: Exception): Exception {
        when (e) {
            is BigQueryException -> {
                if (e.errors.any { it.message.contains(BILLING_CONFIG_ERROR) }) {
                    return ConfigErrorException(e.reason, e)
                }
            }
        }
        return e
    }

    /**
     * Submits [statement] as a BigQuery job and polls it to completion, retrying transient failures
     * with exponential backoff and jitter.
     *
     * Two classes of transient failure are retried:
     * 1. Client-side errors during job creation or polling — a [BigQueryException] thrown by
     * ```
     *    [BigQuery.create] or [Job.reload]. We classify as transient when the exception is
     *    marked [BigQueryException.isRetryable], when its message matches a known transient
     *    signature (request timeout, concurrent-update abort), or when its HTTP code is in the
     *    5xx range.
     * ```
     * 2. Server-side errors reported in [JobStatus.error] after the job reaches terminal
     * ```
     *    state — e.g. `Request timed out. Please try again.` (BigQuery's transient timeout) or
     *    `Transaction is aborted due to concurrent update ...` (optimistic-concurrency abort on
     *    transactional DML). These are retried by resubmitting the job from scratch.
     * ```
     * Non-transient errors (syntax, schema, billing, etc.) are re-thrown immediately.
     *
     * Returns the completed [Job] once it reaches [JobStatus.State.DONE] without a transient error,
     * or after [TRANSIENT_RETRY_MAX_ATTEMPTS] attempts. Caller is responsible for inspecting
     * [Job.getStatus] for any non-transient terminal error.
     */
    private fun runQueryWithTransientRetries(queryId: UUID, statement: String): Job {
        var currentDelayMs = TRANSIENT_RETRY_INITIAL_DELAY_MS
        var lastException: BigQueryException? = null
        for (attemptNumber in 1..TRANSIENT_RETRY_MAX_ATTEMPTS) {
            val transientException: BigQueryException? =
                try {
                    val job = submitAndPoll(statement)
                    val terminalError = job.status.error
                    if (terminalError == null) {
                        return job
                    }
                    val allErrors = listOf(terminalError) + job.status.executionErrors
                    if (!isTransientError(allErrors)) {
                        throw wrapWithConfigExceptionIfNeeded(BigQueryException(allErrors))
                    }
                    logger.warn {
                        "Transient BigQuery error in job.status for query $queryId (attempt $attemptNumber/$TRANSIENT_RETRY_MAX_ATTEMPTS): ${terminalError.message}"
                    }
                    BigQueryException(allErrors)
                } catch (e: BigQueryException) {
                    if (!isTransientException(e)) {
                        throw wrapWithConfigExceptionIfNeeded(e)
                    }
                    logger.warn(e) {
                        "Transient BigQueryException while running query $queryId (attempt $attemptNumber/$TRANSIENT_RETRY_MAX_ATTEMPTS): ${e.message}"
                    }
                    e
                }
            lastException = transientException

            if (attemptNumber < TRANSIENT_RETRY_MAX_ATTEMPTS) {
                val jitter = (Math.random() * 1000).toLong()
                val sleepMs = currentDelayMs + jitter
                logger.info {
                    "Sleeping ${sleepMs}ms before retrying query $queryId (attempt ${attemptNumber + 1}/$TRANSIENT_RETRY_MAX_ATTEMPTS)"
                }
                Thread.sleep(sleepMs)
                currentDelayMs = min(currentDelayMs * 2, TRANSIENT_RETRY_MAX_DELAY_MS)
            }
        }

        val finalException =
            lastException
                ?: BigQueryException(
                    0,
                    "Query $queryId exhausted $TRANSIENT_RETRY_MAX_ATTEMPTS transient-retry attempts with no captured exception"
                )
        logger.error(finalException) {
            "Exhausted $TRANSIENT_RETRY_MAX_ATTEMPTS transient-retry attempts for query $queryId"
        }
        throw wrapWithConfigExceptionIfNeeded(finalException)
    }

    private fun submitAndPoll(statement: String): Job {
        /*
         * If you run a query like CREATE SCHEMA ... OPTIONS(location=foo); CREATE TABLE ...;, bigquery
         * doesn't do a good job of inferring the query location. Pass it in explicitly.
         */
        var job =
            bq.create(
                JobInfo.of(
                    JobId.newBuilder().setLocation(datasetLocation).build(),
                    QueryJobConfiguration.of(statement)
                )
            )
        // job.waitFor() gets stuck forever in some failure cases, so manually poll the job instead.
        while (JobStatus.State.DONE != job.status.state) {
            Thread.sleep(1000L)
            job = job.reload()
        }
        return job
    }

    companion object {
        private const val BILLING_CONFIG_ERROR = "Billing has not been enabled for this project"

        // Substrings that identify known transient BigQuery errors. Matched against both
        // `BigQueryException.message` (client-side) and `BigQueryError.message` (server-side).
        internal const val TRANSIENT_TIMEOUT_ERROR_SUBSTRING =
            "Request timed out. Please try again."
        internal const val CONCURRENT_UPDATE_ERROR_SUBSTRING =
            "Transaction is aborted due to concurrent update"

        internal const val TRANSIENT_RETRY_MAX_ATTEMPTS = 5
        internal const val TRANSIENT_RETRY_INITIAL_DELAY_MS: Long = 1000
        internal const val TRANSIENT_RETRY_MAX_DELAY_MS: Long = 60_000

        internal fun isTransientError(errors: List<BigQueryError>): Boolean {
            return errors.any { err ->
                val msg = err.message ?: ""
                msg.contains(TRANSIENT_TIMEOUT_ERROR_SUBSTRING) ||
                    msg.contains(CONCURRENT_UPDATE_ERROR_SUBSTRING)
            }
        }

        internal fun isTransientException(e: BigQueryException): Boolean {
            if (e.isRetryable) {
                return true
            }
            val code = e.code
            if (code in 500..599) {
                return true
            }
            val msg = e.message ?: ""
            if (
                msg.contains(TRANSIENT_TIMEOUT_ERROR_SUBSTRING) ||
                    msg.contains(CONCURRENT_UPDATE_ERROR_SUBSTRING)
            ) {
                return true
            }
            val errors: List<BigQueryError> = e.errors ?: emptyList()
            return errors.isNotEmpty() && isTransientError(errors)
        }
    }
}
