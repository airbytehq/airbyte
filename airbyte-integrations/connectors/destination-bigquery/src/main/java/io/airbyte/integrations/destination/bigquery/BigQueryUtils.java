/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static io.airbyte.integrations.destination.bigquery.helpers.LoggerHelper.getJobErrorMessage;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryException;
import com.google.cloud.bigquery.Clustering;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.DatasetInfo;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.FieldList;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.JobId;
import com.google.cloud.bigquery.JobInfo;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.QueryParameterValue;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.StandardTableDefinition;
import com.google.cloud.bigquery.TableDefinition;
import com.google.cloud.bigquery.TableId;
import com.google.cloud.bigquery.TableInfo;
import com.google.cloud.bigquery.TimePartitioning;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.joda.time.DateTime;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryUtils.class);
  private static final String BIG_QUERY_DATETIME_FORMAT = "yyyy-MM-dd HH:mm:ss.SSSSSS";

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
      // errors, not just the latest one.
      return ImmutablePair.of(null, (completedJob.getStatus().getError().toString()));
    }

    return ImmutablePair.of(completedJob, null);
  }

  static Job waitForQuery(final Job queryJob) {
    try {
      return queryJob.waitFor();
    } catch (final Exception e) {
      LOGGER.error("Failed to wait for a query job:" + queryJob);
      throw new RuntimeException(e);
    }
  }

  public static void createSchemaAndTableIfNeeded(final BigQuery bigquery,
                                                  final Set<String> existingSchemas,
                                                  final String schemaName,
                                                  final String tmpTableName,
                                                  final String datasetLocation,
                                                  final Schema schema) {
    if (!existingSchemas.contains(schemaName)) {
      createSchemaTable(bigquery, schemaName, datasetLocation);
      existingSchemas.add(schemaName);
    }
    BigQueryUtils.createPartitionedTable(bigquery, schemaName, tmpTableName, schema);
  }

  static void createSchemaTable(final BigQuery bigquery, final String datasetId, final String datasetLocation) {
    final Dataset dataset = bigquery.getDataset(datasetId);
    if (dataset == null || !dataset.exists()) {
      final DatasetInfo datasetInfo = DatasetInfo.newBuilder(datasetId).setLocation(datasetLocation).build();
      bigquery.create(datasetInfo);
    }
  }

  // https://cloud.google.com/bigquery/docs/creating-partitioned-tables#java
  static void createPartitionedTable(final BigQuery bigquery, final String datasetName, final String tableName, final Schema schema) {
    try {

      final TableId tableId = TableId.of(datasetName, tableName);

      final TimePartitioning partitioning = TimePartitioning.newBuilder(TimePartitioning.Type.DAY)
          .setField(JavaBaseConstants.COLUMN_NAME_EMITTED_AT)
          .build();

      final Clustering clustering = Clustering.newBuilder()
          .setFields(ImmutableList.of(JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
          .build();

      final StandardTableDefinition tableDefinition =
          StandardTableDefinition.newBuilder()
              .setSchema(schema)
              .setTimePartitioning(partitioning)
              .setClustering(clustering)
              .build();
      final TableInfo tableInfo = TableInfo.newBuilder(tableId, tableDefinition).build();

      bigquery.create(tableInfo);
      LOGGER.info("Partitioned Table: {} created successfully", tableId);
    } catch (BigQueryException e) {
      LOGGER.info("Partitioned table was not created. \n" + e);
    }
  }

  public static JsonNode getGcsJsonNodeConfig(final JsonNode config) {
    final JsonNode loadingMethod = config.get(BigQueryConsts.LOADING_METHOD);
    final JsonNode gcsJsonNode = Jsons.jsonNode(ImmutableMap.builder()
        .put(BigQueryConsts.GCS_BUCKET_NAME, loadingMethod.get(BigQueryConsts.GCS_BUCKET_NAME))
        .put(BigQueryConsts.GCS_BUCKET_PATH, loadingMethod.get(BigQueryConsts.GCS_BUCKET_PATH))
        .put(BigQueryConsts.GCS_BUCKET_REGION, getDatasetLocation(config))
        .put(BigQueryConsts.CREDENTIAL, loadingMethod.get(BigQueryConsts.CREDENTIAL))
        .put(BigQueryConsts.FORMAT, Jsons.deserialize("{\n"
            + "  \"format_type\": \"CSV\",\n"
            + "  \"flattening\": \"No flattening\",\n"
            + "  \"part_size_mb\": \"" + loadingMethod.get(BigQueryConsts.PART_SIZE) + "\"\n"
            + "}"))
        .build());

    LOGGER.debug("Composed GCS config is: \n" + gcsJsonNode.toPrettyString());
    return gcsJsonNode;
  }

  public static JsonNode getGcsAvroJsonNodeConfig(final JsonNode config) {
    final JsonNode loadingMethod = config.get(BigQueryConsts.LOADING_METHOD);
    final JsonNode gcsJsonNode = Jsons.jsonNode(ImmutableMap.builder()
        .put(BigQueryConsts.GCS_BUCKET_NAME, loadingMethod.get(BigQueryConsts.GCS_BUCKET_NAME))
        .put(BigQueryConsts.GCS_BUCKET_PATH, loadingMethod.get(BigQueryConsts.GCS_BUCKET_PATH))
        .put(BigQueryConsts.GCS_BUCKET_REGION, getDatasetLocation(config))
        .put(BigQueryConsts.CREDENTIAL, loadingMethod.get(BigQueryConsts.CREDENTIAL))
        .put(BigQueryConsts.FORMAT, Jsons.deserialize("{\n"
            + "  \"format_type\": \"AVRO\",\n"
            + "  \"flattening\": \"No flattening\",\n"
            + "  \"part_size_mb\": \"" + loadingMethod.get(BigQueryConsts.PART_SIZE) + "\"\n"
            + "}"))
        .build());

    LOGGER.debug("Composed GCS config is: \n" + gcsJsonNode.toPrettyString());
    return gcsJsonNode;
  }

  public static String getDatasetLocation(final JsonNode config) {
    if (config.has(BigQueryConsts.CONFIG_DATASET_LOCATION)) {
      return config.get(BigQueryConsts.CONFIG_DATASET_LOCATION).asText();
    } else {
      return "US";
    }
  }

  static TableDefinition getTableDefinition(final BigQuery bigquery, final String datasetName, final String tableName) {
    final TableId tableId = TableId.of(datasetName, tableName);
    return bigquery.getTable(tableId).getDefinition();
  }

  /**
   * @param fieldList - the list to be checked
   * @return The list of fields with datetime format.
   *
   */
  public static List<String> getDateTimeFieldsFromSchema(FieldList fieldList) {
    List<String> dateTimeFields = new ArrayList<>();
    for (Field field : fieldList) {
      if (field.getType().getStandardType().equals(StandardSQLTypeName.DATETIME)) {
        dateTimeFields.add(field.getName());
      }
    }
    return dateTimeFields;
  }

  /**
   * @param dateTimeFields - list contains fields of DATETIME format
   * @param data - Json will be sent to Google BigData service
   *
   *        The special DATETIME format is required to save this type to BigQuery.
   * @see <a href=
   *      "https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-json#details_of_loading_json_data">Supported
   *      Google bigquery datatype</a> This method is responsible to adapt JSON DATETIME to Bigquery
   */
  public static void transformJsonDateTimeToBigDataFormat(List<String> dateTimeFields, ObjectNode data) {
    dateTimeFields.forEach(e -> {
      if (data.findValue(e) != null && !data.get(e).isNull()) {
        String googleBigQueryDateFormat = QueryParameterValue
            .dateTime(new DateTime(data
                .findValue(e)
                .asText())
                    .toString(BIG_QUERY_DATETIME_FORMAT))
            .getValue();
        data.put(e, googleBigQueryDateFormat);
      }
    });
  }

  public static String getSchema(final JsonNode config, final ConfiguredAirbyteStream stream) {
    final String defaultSchema = config.get(BigQueryConsts.CONFIG_DATASET_ID).asText();
    final String srcNamespace = stream.getStream().getNamespace();
    if (srcNamespace == null) {
      return defaultSchema;
    }
    return srcNamespace;
  }

  public static JobInfo.WriteDisposition getWriteDisposition(final DestinationSyncMode syncMode) {
    if (syncMode == null) {
      throw new IllegalStateException("Undefined destination sync mode");
    }
    switch (syncMode) {
      case OVERWRITE -> {
        return JobInfo.WriteDisposition.WRITE_TRUNCATE;
      }
      case APPEND, APPEND_DEDUP -> {
        return JobInfo.WriteDisposition.WRITE_APPEND;
      }
      default -> throw new IllegalStateException("Unrecognized destination sync mode: " + syncMode);
    }
  }

  public static boolean isUsingJsonCredentials(final JsonNode config) {
    return config.has(BigQueryConsts.CONFIG_CREDS) && !config.get(BigQueryConsts.CONFIG_CREDS).asText().isEmpty();
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

  public static void waitForJobFinish(Job job) throws InterruptedException {
    if (job != null) {
      try {
        LOGGER.info("Waiting for job finish {}. Status: {}", job, job.getStatus());
        job.waitFor();
        LOGGER.info("Job finish {} with status {}", job, job.getStatus());
      } catch (final BigQueryException e) {
        String errorMessage = getJobErrorMessage(e.getErrors(), job);
        LOGGER.error(errorMessage);
        throw new BigQueryException(e.getCode(), errorMessage, e);
      }
    }
  }

}
