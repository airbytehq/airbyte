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
import io.airbyte.cdk.integrations.base.AirbyteExceptionHandler
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.gcs.GcsDestinationConfig
import io.airbyte.commons.json.Jsons.deserialize
import io.airbyte.commons.json.Jsons.jsonNode
import java.util.*
import java.util.stream.Collectors
import org.apache.commons.lang3.StringUtils
import org.apache.commons.lang3.tuple.ImmutablePair
import org.apache.logging.log4j.util.Strings
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import org.threeten.bp.Duration

object BigQueryUtils {
    private val LOGGER: Logger = LoggerFactory.getLogger(BigQueryUtils::class.java)
    private const val USER_AGENT_FORMAT = "%s (GPN: Airbyte)"
    private const val CHECK_TEST_DATASET_SUFFIX = "_airbyte_check_stage_tmp_"
    private const val CHECK_TEST_TMP_TABLE_NAME = "test_connection_table_name"

    @JvmStatic
    fun executeQuery(
        bigquery: BigQuery,
        queryConfig: QueryJobConfiguration?
    ): ImmutablePair<Job, String> {
        val jobId = JobId.of(UUID.randomUUID().toString())
        val queryJob = bigquery.create(JobInfo.newBuilder(queryConfig).setJobId(jobId).build())
        return executeQuery(queryJob)
    }

    fun executeQuery(queryJob: Job): ImmutablePair<Job, String> {
        val completedJob = waitForQuery(queryJob)
        if (completedJob == null) {
            LOGGER.error("Job no longer exists:$queryJob")
            throw RuntimeException("Job no longer exists")
        } else if (completedJob.status.error != null) {
            // You can also look at queryJob.getStatus().getExecutionErrors() for all
            // errors and not just the latest one.
            return ImmutablePair.of(null, (completedJob.status.error.toString()))
        }

        return ImmutablePair.of(completedJob, null)
    }

    fun waitForQuery(queryJob: Job): Job? {
        try {
            val job = queryJob.waitFor()
            AirbyteExceptionHandler.addStringForDeinterpolation(job.etag)
            return job
        } catch (e: Exception) {
            LOGGER.error("Failed to wait for a query job:$queryJob")
            throw RuntimeException(e)
        }
    }

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
            // Partition by generation ID. This will be useful for when we want to build
            // hybrid refreshes.
            val partitioning =
                RangePartitioning.newBuilder()
                    .setField(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID)
                    .setRange(
                        RangePartitioning.Range.newBuilder()
                            .setStart(
                                0L
                            ) // Bigquery allows a table to have up to 10_000 partitions.
                            .setEnd(
                                10000L
                            ) // Somewhat conservative estimate. This should avoid issues with
                            // users running many merge refreshes.
                            .setInterval(5L)
                            .build()
                    )
                    .build()

            val clustering =
                Clustering.newBuilder()
                    .setFields(
                        ImmutableList.of<String>(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT)
                    )
                    .build()

            val tableDefinition =
                StandardTableDefinition.newBuilder()
                    .setSchema(schema)
                    .setRangePartitioning(partitioning)
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

    @JvmStatic
    fun getGcsJsonNodeConfig(config: JsonNode): JsonNode {
        val loadingMethod = config[BigQueryConsts.LOADING_METHOD]
        return jsonNode(
            ImmutableMap.builder<Any, Any>()
                .put(BigQueryConsts.GCS_BUCKET_NAME, loadingMethod[BigQueryConsts.GCS_BUCKET_NAME])
                .put(BigQueryConsts.GCS_BUCKET_PATH, loadingMethod[BigQueryConsts.GCS_BUCKET_PATH])
                .put(BigQueryConsts.GCS_BUCKET_REGION, getDatasetLocation(config))
                .put(BigQueryConsts.CREDENTIAL, loadingMethod[BigQueryConsts.CREDENTIAL])
                .put(
                    BigQueryConsts.FORMAT,
                    deserialize("""{
  "format_type": "CSV",
  "flattening": "No flattening"
}""")
                )
                .build()
        )
    }

    fun getGcsCsvDestinationConfig(config: JsonNode): GcsDestinationConfig {
        return GcsDestinationConfig.getGcsDestinationConfig(getGcsJsonNodeConfig(config))
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

    @JvmStatic
    fun getDatasetLocation(config: JsonNode): String {
        return if (config.has(BigQueryConsts.CONFIG_DATASET_LOCATION)) {
            config[BigQueryConsts.CONFIG_DATASET_LOCATION].asText()
        } else {
            "US"
        }
    }

    fun getDisableTypeDedupFlag(config: JsonNode): Boolean {
        if (config.has(BigQueryConsts.DISABLE_TYPE_DEDUPE)) {
            return config[BigQueryConsts.DISABLE_TYPE_DEDUPE].asBoolean(false)
        }

        return false
    }

    // https://googleapis.dev/python/bigquery/latest/generated/google.cloud.bigquery.client.Client.html
    fun getBigQueryClientChunkSize(config: JsonNode): Int? {
        var chunkSizeFromConfig: Int? = null
        if (config.has(BigQueryConsts.BIG_QUERY_CLIENT_CHUNK_SIZE)) {
            chunkSizeFromConfig = config[BigQueryConsts.BIG_QUERY_CLIENT_CHUNK_SIZE].asInt()
            if (chunkSizeFromConfig <= 0) {
                LOGGER.error(
                    "BigQuery client Chunk (buffer) size must be a positive number (MB), but was:$chunkSizeFromConfig"
                )
                throw IllegalArgumentException(
                    "BigQuery client Chunk (buffer) size must be a positive number (MB)"
                )
            }
            chunkSizeFromConfig = chunkSizeFromConfig * BigQueryConsts.MiB
        }
        return chunkSizeFromConfig
    }

    @JvmStatic
    fun getLoadingMethod(config: JsonNode): UploadingMethod {
        val loadingMethod = config[BigQueryConsts.LOADING_METHOD]
        if (
            loadingMethod != null &&
                BigQueryConsts.GCS_STAGING == loadingMethod[BigQueryConsts.METHOD].asText()
        ) {
            LOGGER.info("Selected loading method is set to: " + UploadingMethod.GCS)
            return UploadingMethod.GCS
        } else {
            LOGGER.info("Selected loading method is set to: " + UploadingMethod.STANDARD)
            return UploadingMethod.STANDARD
        }
    }

    fun isKeepFilesInGcs(config: JsonNode): Boolean {
        val loadingMethod = config[BigQueryConsts.LOADING_METHOD]
        if (
            loadingMethod != null &&
                loadingMethod[BigQueryConsts.KEEP_GCS_FILES] != null &&
                (BigQueryConsts.KEEP_GCS_FILES_VAL ==
                    loadingMethod[BigQueryConsts.KEEP_GCS_FILES].asText())
        ) {
            LOGGER.info("All tmp files GCS will be kept in bucket when replication is finished")
            return true
        } else {
            LOGGER.info("All tmp files will be removed from GCS when replication is finished")
            return false
        }
    }

    @Throws(InterruptedException::class)
    fun waitForJobFinish(job: Job?) {
        if (job != null) {
            AirbyteExceptionHandler.addStringForDeinterpolation(job.etag)
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
                .map { name: String -> name.replace("airbyte/", Strings.EMPTY).replace(":", "/") }
                .orElse("destination-bigquery")
}
