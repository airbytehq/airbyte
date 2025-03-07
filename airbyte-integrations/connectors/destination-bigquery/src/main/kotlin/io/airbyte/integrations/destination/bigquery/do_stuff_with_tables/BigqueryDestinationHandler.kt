/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.do_stuff_with_tables

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryException
import com.google.cloud.bigquery.Job
import com.google.cloud.bigquery.JobConfiguration
import com.google.cloud.bigquery.JobId
import com.google.cloud.bigquery.JobInfo
import com.google.cloud.bigquery.JobStatistics
import com.google.cloud.bigquery.JobStatus
import com.google.cloud.bigquery.QueryJobConfiguration
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.integrations.destination.bigquery.probably_core_stuff.ConnectorExceptionUtil
import io.airbyte.integrations.destination.bigquery.probably_core_stuff.Sql
import io.airbyte.integrations.destination.bigquery.util.BigQueryUtils
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.UUID

private val logger = KotlinLogging.logger {}

class BigqueryDestinationHandler(private val bq: BigQuery, private val datasetLocation: String) {
    fun execute(sql: Sql) {
        val transactions = sql.asSqlStrings("BEGIN TRANSACTION", "COMMIT TRANSACTION")
        if (transactions.isEmpty()) {
            return
        }
        val queryId = UUID.randomUUID()
        val statement = java.lang.String.join("\n", transactions)
        logger.debug { "Executing sql $queryId}: $statement" }

        /*
         * If you run a query like CREATE SCHEMA ... OPTIONS(location=foo); CREATE TABLE ...;, bigquery
         * doesn't do a good job of inferring the query location. Pass it in explicitly.
         */
        var job =
            bq.create(
                JobInfo.of(
                    JobId.newBuilder().setLocation(datasetLocation).build(),
                    QueryJobConfiguration.newBuilder(statement).build()
                )
            )
        //        AirbyteExceptionHandler.addStringForDeinterpolation(job.etag)
        // job.waitFor() gets stuck forever in some failure cases, so manually poll the job instead.
        while (JobStatus.State.DONE != job.status.state) {
            Thread.sleep(1000L)
            job = job.reload()
        }
        if (job.status.error != null) {
            throw BigQueryException(listOf(job.status.error) + job.status.executionErrors)
        }

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
                .streamAll()
                .sorted(
                    Comparator.comparing { childJob: Job ->
                        childJob.getStatistics<JobStatistics>().endTime
                    }
                )
                .forEach { childJob: Job ->
                    val configuration = childJob.getConfiguration<JobConfiguration>()
                    if (configuration is QueryJobConfiguration) {
                        val childQueryStats =
                            childJob.getStatistics<JobStatistics.QueryStatistics>()
                        var truncatedQuery: String =
                            configuration.query
                                .replace("\n".toRegex(), " ")
                                .replace(" +".toRegex(), " ")
                                .substring(0, 100.coerceAtMost(configuration.query.length))
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

    fun createNamespaces(schemas: Set<String>) {
        schemas.forEach { dataset: String -> createDataset(dataset) }
    }

    // TODO ... why is this not just done in BigQueryUtils?
    //   and/or can we kill BigQueryUtils.getOrCreateDataset?
    private fun createDataset(dataset: String) {
        logger.info { "Creating dataset if not present $dataset" }
        try {
            BigQueryUtils.getOrCreateDataset(bq, dataset, datasetLocation)
        } catch (e: BigQueryException) {
            if (ConnectorExceptionUtil.HTTP_AUTHENTICATION_ERROR_CODES.contains(e.code)) {
                throw ConfigErrorException(e.message!!, e)
            } else {
                throw e
            }
        }
    }
}
