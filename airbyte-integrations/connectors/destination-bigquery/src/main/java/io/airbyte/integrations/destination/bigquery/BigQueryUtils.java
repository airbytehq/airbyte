/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.api.gax.rpc.HeaderProvider;
import com.google.cloud.RetryOption;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryError;
import com.google.cloud.bigquery.BigQueryException;
import com.google.cloud.bigquery.Clustering;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.DatasetInfo;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.InsertAllRequest;
import com.google.cloud.bigquery.InsertAllRequest.RowToInsert;
import com.google.cloud.bigquery.InsertAllResponse;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.JobId;
import com.google.cloud.bigquery.JobInfo;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.StandardTableDefinition;
import com.google.cloud.bigquery.Table;
import com.google.cloud.bigquery.TableDefinition;
import com.google.cloud.bigquery.TableId;
import com.google.cloud.bigquery.TableInfo;
import com.google.cloud.bigquery.TimePartitioning;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.integrations.base.AirbyteExceptionHandler;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.logging.log4j.util.Strings;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.threeten.bp.Duration;

public class BigQueryUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryUtils.class);
  private static final String USER_AGENT_FORMAT = "%s (GPN: Airbyte)";
  private static final String CHECK_TEST_DATASET_SUFFIX = "_airbyte_check_stage_tmp_";
  private static final String CHECK_TEST_TMP_TABLE_NAME = "test_connection_table_name";

  public static ImmutablePair<Job, String> executeQuery(final BigQuery bigquery, final QueryJobConfiguration queryConfig) {
    final JobId jobId = JobId.of(UUID.randomUUID().toString());
    final Job queryJob = bigquery.create(JobInfo.newBuilder(queryConfig).setJobId(jobId).build());
    return executeQuery(queryJob);
  }

  public static ImmutablePair<Job, String> executeQuery(final Job queryJob) {
    final Job completedJob = waitForQuery(queryJob);
    if (completedJob == null) {
      LOGGER.error("Job no longer exists:" + queryJob);
      throw new RuntimeException("Job no longer exists");
    } else if (completedJob.getStatus().getError() != null) {
      // You can also look at queryJob.getStatus().getExecutionErrors() for all
      // errors and not just the latest one.
      return ImmutablePair.of(null, (completedJob.getStatus().getError().toString()));
    }

    return ImmutablePair.of(completedJob, null);
  }

  static Job waitForQuery(final Job queryJob) {
    try {
      final Job job = queryJob.waitFor();
      AirbyteExceptionHandler.addStringForDeinterpolation(job.getEtag());
      return job;
    } catch (final Exception e) {
      LOGGER.error("Failed to wait for a query job:" + queryJob);
      throw new RuntimeException(e);
    }
  }

  public static Dataset getOrCreateDataset(final BigQuery bigquery, final String datasetId, final String datasetLocation) {
    Dataset dataset = bigquery.getDataset(datasetId);
    if (dataset == null || !dataset.exists()) {
      final DatasetInfo datasetInfo = DatasetInfo.newBuilder(datasetId).setLocation(datasetLocation).build();
      dataset = bigquery.create(datasetInfo);
    }
    return dataset;
  }

  public static void checkHasCreateAndDeleteDatasetRole(final BigQuery bigquery, final String datasetId, final String datasetLocation) {
    final String tmpTestDatasetId = datasetId + CHECK_TEST_DATASET_SUFFIX + System.currentTimeMillis();
    final DatasetInfo datasetInfo = DatasetInfo.newBuilder(tmpTestDatasetId).setLocation(datasetLocation).build();

    bigquery.create(datasetInfo);

    try {
      attemptCreateTableAndTestInsert(bigquery, tmpTestDatasetId);
    } finally {
      bigquery.delete(tmpTestDatasetId);
    }
  }

  /**
   * Method is used to create tmp table and make dummy record insert. It's used in Check() connection
   * method to make sure that user has all required roles for upcoming data sync/migration. It also
   * verifies if BigQuery project is billable, if not - later sync will fail as non-billable project
   * has limitations with stream uploading and DML queries. More details may be found there:
   * https://cloud.google.com/bigquery/docs/streaming-data-into-bigquery
   * https://cloud.google.com/bigquery/docs/reference/standard-sql/data-manipulation-language
   *
   * @param bigquery - initialized bigquery client
   * @param tmpTestDatasetId - dataset name where tmp table will be created
   */
  private static void attemptCreateTableAndTestInsert(final BigQuery bigquery, final String tmpTestDatasetId) {
    // Create dummy schema that will be used for tmp table creation
    final Schema testTableSchema = Schema.of(
        Field.of("id", StandardSQLTypeName.INT64),
        Field.of("name", StandardSQLTypeName.STRING));

    // Create tmp table to verify if user has a create table permission. Also below we will do test
    // records insert in it
    final Table test_connection_table_name = createTable(bigquery, tmpTestDatasetId,
        CHECK_TEST_TMP_TABLE_NAME, testTableSchema);

    // Try to make test (dummy records) insert to make sure that user has required permissions
    // Use ids for BigQuery client to attempt idempotent retries.
    // See https://github.com/airbytehq/airbyte/issues/33982
    try {
      final InsertAllResponse response =
          bigquery.insertAll(InsertAllRequest
              .newBuilder(test_connection_table_name)
              .addRow(RowToInsert.of("1", ImmutableMap.of("id", 1, "name", "James")))
              .addRow(RowToInsert.of("2", ImmutableMap.of("id", 2, "name", "Eugene")))
              .addRow(RowToInsert.of("3", ImmutableMap.of("id", 3, "name", "Angelina")))
              .build());

      if (response.hasErrors()) {
        // If any of the insertions failed, this lets you inspect the errors
        for (final Map.Entry<Long, List<BigQueryError>> entry : response.getInsertErrors().entrySet()) {
          throw new ConfigErrorException("Failed to check connection: \n" + entry.getValue());
        }
      }
    } catch (final BigQueryException e) {
      LOGGER.error("Dummy inserts in check failed", e);
      throw new ConfigErrorException("Failed to check connection: \n" + e.getMessage());
    } finally {
      test_connection_table_name.delete();
    }
  }

  public static Table createTable(final BigQuery bigquery, final String datasetName, final String tableName, final Schema schema) {
    final TableId tableId = TableId.of(datasetName, tableName);
    final TableDefinition tableDefinition = StandardTableDefinition.of(schema);
    final TableInfo tableInfo = TableInfo.newBuilder(tableId, tableDefinition).build();
    return bigquery.create(tableInfo);
  }

  /**
   * Creates a partitioned table with clustering based on time
   *
   * <p>
   * https://cloud.google.com/bigquery/docs/creating-partitioned-tables#java
   * </p>
   *
   * @param bigquery BigQuery interface
   * @param tableId equivalent to table name
   * @param schema representation for table schema
   * @return Table BigQuery table object to be referenced for deleting, otherwise empty meaning table
   *         was not successfully created
   */
  public static void createPartitionedTableIfNotExists(final BigQuery bigquery, final TableId tableId, final Schema schema) {
    try {
      final var chunkingColumn = JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT;
      final TimePartitioning partitioning = TimePartitioning.newBuilder(TimePartitioning.Type.DAY)
          .setField(chunkingColumn)
          .build();

      final Clustering clustering = Clustering.newBuilder()
          .setFields(ImmutableList.of(chunkingColumn))
          .build();

      final StandardTableDefinition tableDefinition =
          StandardTableDefinition.newBuilder()
              .setSchema(schema)
              .setTimePartitioning(partitioning)
              .setClustering(clustering)
              .build();
      final TableInfo tableInfo = TableInfo.newBuilder(tableId, tableDefinition).build();

      final Table table = bigquery.getTable(tableInfo.getTableId());
      if (table != null && table.exists()) {
        // TODO: Handle migration from v1 -> v2
        LOGGER.info("Partitioned table ALREADY EXISTS: {}", tableId);
      } else {
        bigquery.create(tableInfo);
        LOGGER.info("Partitioned table created successfully: {}", tableId);
      }

    } catch (final BigQueryException e) {
      LOGGER.error("Partitioned table was not created: {}", tableId, e);
      throw e;
    }
  }

  public static JsonNode getGcsJsonNodeConfig(final JsonNode config) {
    final JsonNode loadingMethod = config.get(BigQueryConsts.LOADING_METHOD);
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(BigQueryConsts.GCS_BUCKET_NAME, loadingMethod.get(BigQueryConsts.GCS_BUCKET_NAME))
        .put(BigQueryConsts.GCS_BUCKET_PATH, loadingMethod.get(BigQueryConsts.GCS_BUCKET_PATH))
        .put(BigQueryConsts.GCS_BUCKET_REGION, getDatasetLocation(config))
        .put(BigQueryConsts.CREDENTIAL, loadingMethod.get(BigQueryConsts.CREDENTIAL))
        .put(BigQueryConsts.FORMAT, Jsons.deserialize("{\n"
            + "  \"format_type\": \"CSV\",\n"
            + "  \"flattening\": \"No flattening\"\n"
            + "}"))
        .build());
  }

  public static GcsDestinationConfig getGcsCsvDestinationConfig(final JsonNode config) {
    return GcsDestinationConfig.getGcsDestinationConfig(getGcsJsonNodeConfig(config));
  }

  /**
   * @return a default schema name based on the config.
   */
  public static String getDatasetId(final JsonNode config) {
    final String datasetId = config.get(BigQueryConsts.CONFIG_DATASET_ID).asText();

    final int colonIndex = datasetId.indexOf(":");
    if (colonIndex != -1) {
      final String projectIdPart = datasetId.substring(0, colonIndex);
      final String projectId = config.get(BigQueryConsts.CONFIG_PROJECT_ID).asText();
      if (!(projectId.equals(projectIdPart))) {
        throw new IllegalArgumentException(String.format(
            "Project ID included in Dataset ID must match Project ID field's value: Project ID is `%s`, but you specified `%s` in Dataset ID",
            projectId,
            projectIdPart));
      }
    }
    // if colonIndex is -1, then this returns the entire string
    // otherwise it returns everything after the colon
    return datasetId.substring(colonIndex + 1);
  }

  public static String getDatasetLocation(final JsonNode config) {
    if (config.has(BigQueryConsts.CONFIG_DATASET_LOCATION)) {
      return config.get(BigQueryConsts.CONFIG_DATASET_LOCATION).asText();
    } else {
      return "US";
    }
  }

  public static boolean getDisableTypeDedupFlag(final JsonNode config) {
    if (config.has(BigQueryConsts.DISABLE_TYPE_DEDUPE)) {
      return config.get(BigQueryConsts.DISABLE_TYPE_DEDUPE).asBoolean(false);
    }

    return false;
  }

  // https://googleapis.dev/python/bigquery/latest/generated/google.cloud.bigquery.client.Client.html
  public static Integer getBigQueryClientChunkSize(final JsonNode config) {
    Integer chunkSizeFromConfig = null;
    if (config.has(BigQueryConsts.BIG_QUERY_CLIENT_CHUNK_SIZE)) {
      chunkSizeFromConfig = config.get(BigQueryConsts.BIG_QUERY_CLIENT_CHUNK_SIZE).asInt();
      if (chunkSizeFromConfig <= 0) {
        LOGGER.error("BigQuery client Chunk (buffer) size must be a positive number (MB), but was:" + chunkSizeFromConfig);
        throw new IllegalArgumentException("BigQuery client Chunk (buffer) size must be a positive number (MB)");
      }
      chunkSizeFromConfig = chunkSizeFromConfig * BigQueryConsts.MiB;
    }
    return chunkSizeFromConfig;
  }

  public static UploadingMethod getLoadingMethod(final JsonNode config) {
    final JsonNode loadingMethod = config.get(BigQueryConsts.LOADING_METHOD);
    if (loadingMethod != null && BigQueryConsts.GCS_STAGING.equals(loadingMethod.get(BigQueryConsts.METHOD).asText())) {
      LOGGER.info("Selected loading method is set to: " + UploadingMethod.GCS);
      return UploadingMethod.GCS;
    } else {
      LOGGER.info("Selected loading method is set to: " + UploadingMethod.STANDARD);
      return UploadingMethod.STANDARD;
    }
  }

  public static boolean isKeepFilesInGcs(final JsonNode config) {
    final JsonNode loadingMethod = config.get(BigQueryConsts.LOADING_METHOD);
    if (loadingMethod != null && loadingMethod.get(BigQueryConsts.KEEP_GCS_FILES) != null
        && BigQueryConsts.KEEP_GCS_FILES_VAL
            .equals(loadingMethod.get(BigQueryConsts.KEEP_GCS_FILES).asText())) {
      LOGGER.info("All tmp files GCS will be kept in bucket when replication is finished");
      return true;
    } else {
      LOGGER.info("All tmp files will be removed from GCS when replication is finished");
      return false;
    }
  }

  public static void waitForJobFinish(final Job job) throws InterruptedException {
    if (job != null) {
      AirbyteExceptionHandler.addStringForDeinterpolation(job.getEtag());
      try {
        LOGGER.info("Waiting for Job {} to finish. Status: {}", job.getJobId(), job.getStatus());
        // Default totalTimeout is 12 Hours, 30 minutes seems reasonable
        final Job completedJob = job.waitFor(RetryOption.totalTimeout(Duration.ofMinutes(30)));
        if (completedJob == null) {
          // job no longer exists
          LOGGER.warn("Job {} No longer exists", job.getJobId());
        } else if (completedJob.getStatus().getError() != null) {
          // job failed, handle error
          LOGGER.error("Job {} failed with errors {}", completedJob.getJobId(), completedJob.getStatus().getError().toString());
          throw new RuntimeException(
              "Fail to complete a load job in big query, Job id: " + completedJob.getJobId() +
                  ", with error: " + completedJob.getStatus().getError());
        } else {
          // job completed successfully
          LOGGER.info("Job {} completed successfully, job info {}", completedJob.getJobId(), completedJob);
        }
      } catch (final BigQueryException e) {
        final String errorMessage = getJobErrorMessage(e.getErrors(), job);
        LOGGER.error(errorMessage);
        throw new BigQueryException(e.getCode(), errorMessage, e);
      }
    } else {
      LOGGER.warn("Received null value for Job, nothing to waitFor");
    }
  }

  private static String getJobErrorMessage(List<BigQueryError> errors, Job job) {
    if (errors == null || errors.isEmpty()) {
      return StringUtils.EMPTY;

    }
    return String.format("An error occurred during execution of job: %s, \n For more details see Big Query Error collection: %s:", job,
        errors.stream().map(BigQueryError::toString).collect(Collectors.joining(",\n ")));
  }

  public static HeaderProvider getHeaderProvider() {
    final String connectorName = getConnectorNameOrDefault();
    return () -> ImmutableMap.of("user-agent", String.format(USER_AGENT_FORMAT, connectorName));
  }

  private static String getConnectorNameOrDefault() {
    return Optional.ofNullable(System.getenv("WORKER_CONNECTOR_IMAGE"))
        .map(name -> name.replace("airbyte/", Strings.EMPTY).replace(":", "/"))
        .orElse("destination-bigquery");
  }

}
