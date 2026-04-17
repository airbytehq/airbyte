/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.write.typing_deduping

import com.google.cloud.bigquery.BigQuery
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

        /*
         * If you run a query like CREATE SCHEMA ... OPTIONS(location=foo); CREATE TABLE ...;, bigquery
         * doesn't do a good job of inferring the query location. Pass it in explicitly.
         */
        val job = runQueryWithConcurrentUpdateRetries(queryId, statement)

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

    /**
     * Submit [statement] as a BigQuery query job, poll to completion, and retry on transient
     * concurrent-update aborts.
     *
     * BigQuery uses optimistic concurrency control for DML. When two transactions touch the same
     * table in overlapping windows, BigQuery aborts one of them with the message `Transaction is
     * aborted due to concurrent update`. The canonical mitigation per BigQuery docs is to retry
     * the aborted transaction. The typing+deduping operations we run here (MERGE, CREATE OR
     * REPLACE TABLE) are idempotent, so retrying is safe.
     */
    private fun runQueryWithConcurrentUpdateRetries(queryId: UUID, statement: String): Job {
        var attemptDelayMs = CONCURRENT_UPDATE_INITIAL_DELAY_MS
        var lastException: BigQueryException? = null
        for (attemptNumber in 1..CONCURRENT_UPDATE_MAX_ATTEMPTS) {
            var job =
                bq.create(
                    JobInfo.of(
                        JobId.newBuilder().setLocation(datasetLocation).build(),
                        QueryJobConfiguration.of(statement)
                    )
                )
            // job.waitFor() gets stuck forever in some failure cases, so manually poll the job
            // instead.
            while (JobStatus.State.DONE != job.status.state) {
                Thread.sleep(1000L)
                job = job.reload()
            }
            val jobError = job.status.error
            if (jobError == null) {
                return job
            }
            val bqException =
                BigQueryException(listOf(jobError) + job.status.executionErrors)
            if (
                isConcurrentUpdateError(bqException) &&
                    attemptNumber < CONCURRENT_UPDATE_MAX_ATTEMPTS
            ) {
                lastException = bqException
                logger.warn(bqException) {
                    "BigQuery aborted sql $queryId due to concurrent update " +
                        "(attempt $attemptNumber/$CONCURRENT_UPDATE_MAX_ATTEMPTS). " +
                        "Sleeping ${attemptDelayMs}ms and retrying."
                }
                val withJitter = attemptDelayMs + (1000 * Math.random()).toLong()
                Thread.sleep(withJitter)
                attemptDelayMs = min(attemptDelayMs * 2, CONCURRENT_UPDATE_MAX_DELAY_MS)
                continue
            }
            throw wrapWithConfigExceptionIfNeeded(bqException)
        }
        // Should be unreachable: the loop either returns on success or throws on failure. Only
        // way to exit is if every attempt was a concurrent-update abort AND we exhausted the
        // retry budget, in which case the final attempt's exception is thrown above. This branch
        // is defensive to satisfy the compiler.
        throw wrapWithConfigExceptionIfNeeded(
            lastException
                ?: BigQueryException(
                    500,
                    "BigQuery job exhausted concurrent-update retry budget without a recorded error."
                )
        )
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

    companion object {
        private const val BILLING_CONFIG_ERROR = "Billing has not been enabled for this project"

        /**
         * Text fragment BigQuery includes in the error message when it aborts a transaction due
         * to optimistic concurrency control. See
         * https://cloud.google.com/bigquery/docs/data-manipulation-language#concurrent_dml_statements.
         */
        private const val CONCURRENT_UPDATE_ERROR_FRAGMENT =
            "Transaction is aborted due to concurrent update"

        private const val CONCURRENT_UPDATE_MAX_ATTEMPTS = 5
        private const val CONCURRENT_UPDATE_INITIAL_DELAY_MS = 1000L
        private const val CONCURRENT_UPDATE_MAX_DELAY_MS = 60_000L

        internal fun isConcurrentUpdateError(e: BigQueryException): Boolean {
            if (e.message?.contains(CONCURRENT_UPDATE_ERROR_FRAGMENT) == true) {
                return true
            }
            return e.errors.orEmpty().any {
                it.message?.contains(CONCURRENT_UPDATE_ERROR_FRAGMENT) == true
            }
        }
    }
}
