/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryException;
import com.google.cloud.bigquery.Clustering;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.DatasetInfo;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.JobId;
import com.google.cloud.bigquery.JobInfo;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.StandardTableDefinition;
import com.google.cloud.bigquery.TableDefinition;
import com.google.cloud.bigquery.TableId;
import com.google.cloud.bigquery.TableInfo;
import com.google.cloud.bigquery.TimePartitioning;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import java.util.Set;
import java.util.UUID;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryUtils.class);

  static ImmutablePair<Job, String> executeQuery(final BigQuery bigquery, final QueryJobConfiguration queryConfig) {
    final JobId jobId = JobId.of(UUID.randomUUID().toString());
    final Job queryJob = bigquery.create(JobInfo.newBuilder(queryConfig).setJobId(jobId).build());
    return executeQuery(queryJob);
  }

  static ImmutablePair<Job, String> executeQuery(final Job queryJob) {
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

  static void createSchemaAndTableIfNeeded(final BigQuery bigquery,
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
            + "  \"flattening\": \"No flattening\"\n"
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

}
