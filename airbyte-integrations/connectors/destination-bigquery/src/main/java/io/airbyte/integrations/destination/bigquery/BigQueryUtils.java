/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.bigquery;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryException;
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
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import java.util.Set;
import java.util.UUID;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryUtils.class);

  static ImmutablePair<Job, String> executeQuery(BigQuery bigquery, QueryJobConfiguration queryConfig) {
    final JobId jobId = JobId.of(UUID.randomUUID().toString());
    final Job queryJob = bigquery.create(JobInfo.newBuilder(queryConfig).setJobId(jobId).build());
    return executeQuery(queryJob);
  }

  static ImmutablePair<Job, String> executeQuery(Job queryJob) {
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

  static Job waitForQuery(Job queryJob) {
    try {
      return queryJob.waitFor();
    } catch (Exception e) {
      LOGGER.error("Failed to wait for a query job:" + queryJob);
      throw new RuntimeException(e);
    }
  }

  static void createSchemaAndTableIfNeeded(BigQuery bigquery,
                                           Set<String> existingSchemas,
                                           String schemaName,
                                           String tmpTableName,
                                           String datasetLocation,
                                           Schema schema) {
    if (!existingSchemas.contains(schemaName)) {
      createSchemaTable(bigquery, schemaName, datasetLocation);
      existingSchemas.add(schemaName);
    }
    BigQueryUtils.createTable(bigquery, schemaName, tmpTableName, schema);
  }

  static void createSchemaTable(BigQuery bigquery, String datasetId, String datasetLocation) {
    final Dataset dataset = bigquery.getDataset(datasetId);
    if (dataset == null || !dataset.exists()) {
      final DatasetInfo datasetInfo = DatasetInfo.newBuilder(datasetId).setLocation(datasetLocation).build();
      bigquery.create(datasetInfo);
    }
  }

  // https://cloud.google.com/bigquery/docs/tables#create-table
  static void createTable(BigQuery bigquery, String datasetName, String tableName, Schema schema) {
    try {

      final TableId tableId = TableId.of(datasetName, tableName);
      final TableDefinition tableDefinition = StandardTableDefinition.of(schema);
      final TableInfo tableInfo = TableInfo.newBuilder(tableId, tableDefinition).build();

      bigquery.create(tableInfo);
      LOGGER.info("Table: {} created successfully", tableId);
    } catch (BigQueryException e) {
      LOGGER.info("Table was not created. \n", e);
    }
  }

  public static JsonNode getGcsJsonNodeConfig(JsonNode config) {
    JsonNode loadingMethod = config.get(BigQueryConsts.LOADING_METHOD);
    JsonNode gcsJsonNode = Jsons.jsonNode(ImmutableMap.builder()
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

  public static String getDatasetLocation(JsonNode config) {
    if (config.has(BigQueryConsts.CONFIG_DATASET_LOCATION)) {
      return config.get(BigQueryConsts.CONFIG_DATASET_LOCATION).asText();
    } else {
      return "US";
    }
  }

}
