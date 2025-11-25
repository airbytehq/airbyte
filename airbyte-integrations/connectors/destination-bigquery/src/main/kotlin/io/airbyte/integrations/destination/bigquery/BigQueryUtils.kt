/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery

import com.fasterxml.jackson.databind.JsonNode
import com.google.api.gax.rpc.HeaderProvider
import com.google.cloud.RetryOption
import com.google.cloud.bigquery.*
import com.google.common.collect.ImmutableList
import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.message.Meta
import java.util.*
import java.util.stream.Collectors
import org.apache.commons.lang3.StringUtils
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import org.threeten.bp.Duration

object BigQueryUtils {
    private val LOGGER: Logger = LoggerFactory.getLogger(BigQueryUtils::class.java)
    private const val USER_AGENT_FORMAT = "%s (GPN: Airbyte)"

    @JvmStatic
    fun getOrCreateDataset(
        bigquery: BigQuery,
        datasetId: String?,
        datasetLocation: String?
    ): Dataset {
        var dataset = bigquery.getDataset(datasetId)
        if (dataset == null || !dataset.exists()) {
            val datasetInfo = DatasetInfo.newBuilder(datasetId).setLocation(datasetLocation).build()
            dataset = bigquery.create(datasetInfo)
        }
        if (dataset.location != datasetLocation) {
            throw ConfigErrorException(
                "Expected dataset $datasetId to be in location $datasetLocation, but it was in ${dataset.location}. You should either recreate the dataset manually in $datasetLocation, update your destination settings to use location ${dataset.location}, or configure this connection to use a different dataset."
            )
        }
        return dataset
    }

    /**
     * Creates a partitioned table with clustering based on time
     *
     * https://cloud.google.com/bigquery/docs/creating-partitioned-tables#java
     *
     * @param bigquery BigQuery interface
     * @param tableId equivalent to table name
     * @param schema representation for table schema
     * @return Table BigQuery table object to be referenced for deleting, otherwise empty meaning
     * table was not successfully created
     */
    @JvmStatic
    fun createPartitionedTableIfNotExists(bigquery: BigQuery, tableId: TableId?, schema: Schema?) {
        try {
            val partitioning =
                TimePartitioning.newBuilder(TimePartitioning.Type.DAY)
                    .setField(Meta.COLUMN_NAME_AB_EXTRACTED_AT)
                    .build()

            val clustering =
                Clustering.newBuilder()
                    .setFields(ImmutableList.of(Meta.COLUMN_NAME_AB_EXTRACTED_AT))
                    .build()

            val tableDefinition =
                StandardTableDefinition.newBuilder()
                    .setSchema(schema)
                    .setTimePartitioning(partitioning)
                    .setClustering(clustering)
                    .build()
            val tableInfo = TableInfo.newBuilder(tableId, tableDefinition).build()

            val table = bigquery.getTable(tableInfo.tableId)
            if (table != null && table.exists()) {
                LOGGER.info("Partitioned table ALREADY EXISTS: {}", tableId)
            } else {
                bigquery.create(tableInfo)
                LOGGER.info("Partitioned table created successfully: {}", tableId)
            }
        } catch (e: BigQueryException) {
            LOGGER.error("Partitioned table was not created: {}", tableId, e)
            throw e
        }
    }

    /** @return a default schema name based on the config. */
    @JvmStatic
    fun getDatasetId(config: JsonNode): String {
        val datasetId = config[BigQueryConsts.CONFIG_DATASET_ID].asText()

        val colonIndex = datasetId.indexOf(":")
        if (colonIndex != -1) {
            val projectIdPart = datasetId.substring(0, colonIndex)
            val projectId = config[BigQueryConsts.CONFIG_PROJECT_ID].asText()
            require(projectId == projectIdPart) {
                String.format(
                    "Project ID included in Dataset ID must match Project ID field's value: Project ID is `%s`, but you specified `%s` in Dataset ID",
                    projectId,
                    projectIdPart
                )
            }
        }
        // if colonIndex is -1, then this returns the entire string
        // otherwise it returns everything after the colon
        return datasetId.substring(colonIndex + 1)
    }

    @Throws(InterruptedException::class)
    fun waitForJobFinish(job: Job?) {
        if (job != null) {
            try {
                LOGGER.info("Waiting for Job {} to finish. Status: {}", job.jobId, job.status)
                // Default totalTimeout is 12 Hours, 30 minutes seems reasonable
                val completedJob = job.waitFor(RetryOption.totalTimeout(Duration.ofMinutes(30)))
                if (completedJob == null) {
                    // job no longer exists
                    LOGGER.warn("Job {} No longer exists", job.jobId)
                } else if (completedJob.status.error != null) {
                    // job failed, handle error
                    LOGGER.error(
                        "Job {} failed with errors {}",
                        completedJob.jobId,
                        completedJob.status.error.toString()
                    )
                    throw RuntimeException(
                        "Fail to complete a load job in big query, Job id: " +
                            completedJob.jobId +
                            ", with error: " +
                            completedJob.status.error
                    )
                } else {
                    // job completed successfully
                    LOGGER.info(
                        "Job {} completed successfully, job info {}",
                        completedJob.jobId,
                        completedJob
                    )
                }
            } catch (e: BigQueryException) {
                val errorMessage = getJobErrorMessage(e.errors, job)
                LOGGER.error(errorMessage)
                throw BigQueryException(e.code, errorMessage, e)
            }
        } else {
            LOGGER.warn("Received null value for Job, nothing to waitFor")
        }
    }

    private fun getJobErrorMessage(errors: List<BigQueryError>?, job: Job): String {
        if (errors == null || errors.isEmpty()) {
            return StringUtils.EMPTY
        }
        return String.format(
            "An error occurred during execution of job: %s, \n For more details see Big Query Error collection: %s:",
            job,
            errors
                .stream()
                .map { obj: BigQueryError -> obj.toString() }
                .collect(Collectors.joining(",\n "))
        )
    }

    val headerProvider: HeaderProvider
        get() {
            val connectorName = connectorNameOrDefault
            return HeaderProvider {
                ImmutableMap.of("user-agent", String.format(USER_AGENT_FORMAT, connectorName))
            }
        }

    private val connectorNameOrDefault: String
        get() =
            Optional.ofNullable(System.getenv("WORKER_CONNECTOR_IMAGE"))
                .map { name: String -> name.replace("airbyte/", "").replace(":", "/") }
                .orElse("destination-bigquery")
}

fun TableId.toPrettyString() = "${this.dataset}.${this.table}"
