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
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.auth.oauth2.ServiceAccountCredentials;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.DatasetInfo;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.FieldList;
import com.google.cloud.bigquery.FieldValue;
import com.google.cloud.bigquery.FieldValueList;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.JobId;
import com.google.cloud.bigquery.JobInfo;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.TableResult;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Maps;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.io.ByteArrayInputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDestinationAcceptanceTest.class);

  private static final Path CREDENTIALS_PATH = Path.of("secrets/credentials.json");

  private static final String CONFIG_DATASET_ID = "dataset_id";
  private static final String CONFIG_PROJECT_ID = "project_id";
  private static final String CONFIG_DATASET_LOCATION = "dataset_location";
  private static final String CONFIG_CREDS = "credentials_json";

  private BigQuery bigquery;
  private Dataset dataset;
  private boolean tornDown;
  private JsonNode config;
  private StandardNameTransformer namingResolver = new StandardNameTransformer();

  @Override
  protected String getImageName() {
    return "airbyte/destination-bigquery:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected JsonNode getFailCheckConfig() throws Exception {
    ((ObjectNode) config).put(CONFIG_PROJECT_ID, "fake");
    return config;
  }

  @Override
  protected boolean supportsNormalization() {
    return true;
  }

  @Override
  protected boolean supportsDBT() {
    return true;
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected String getDefaultSchema(JsonNode config) {
    return config.get(CONFIG_DATASET_ID).asText();
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(TestDestinationEnv testEnv, String streamName, String namespace) throws Exception {
    String tableName = namingResolver.getIdentifier(streamName);
    String schema = namingResolver.getIdentifier(namespace);
    return retrieveRecordsFromTable(tableName, schema);
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv env,
                                           String streamName,
                                           String namespace,
                                           JsonNode streamSchema)
      throws Exception {
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namingResolver.getIdentifier(namespace))
        .stream()
        .map(node -> node.get(JavaBaseConstants.COLUMN_NAME_DATA).asText())
        .map(Jsons::deserialize)
        .collect(Collectors.toList());
  }

  @Override
  protected List<String> resolveIdentifier(String identifier) {
    final List<String> result = new ArrayList<>();
    result.add(identifier);
    result.add(namingResolver.getIdentifier(identifier));
    return result;
  }

  private List<JsonNode> retrieveRecordsFromTable(String tableName, String schema) throws InterruptedException {
    final QueryJobConfiguration queryConfig =
        QueryJobConfiguration
            .newBuilder(
                String.format("SELECT * FROM `%s`.`%s` order by %s asc;", schema, tableName,
                    JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
            .setUseLegacySql(false).build();

    TableResult queryResults = executeQuery(bigquery, queryConfig).getLeft().getQueryResults();
    FieldList fields = queryResults.getSchema().getFields();

    return StreamSupport
        .stream(queryResults.iterateAll().spliterator(), false)
        .map(row -> {
          Map<String, Object> jsonMap = Maps.newHashMap();
          for (Field field : fields) {
            Object value = getTypedFieldValue(row, field);
            jsonMap.put(field.getName(), value);
          }
          return jsonMap;
        })
        .map(Jsons::jsonNode)
        .collect(Collectors.toList());
  }

  private Object getTypedFieldValue(FieldValueList row, Field field) {
    FieldValue fieldValue = row.get(field.getName());
    if (fieldValue.getValue() != null) {
      return switch (field.getType().getStandardType()) {
        case FLOAT64, NUMERIC -> fieldValue.getDoubleValue();
        case INT64 -> fieldValue.getNumericValue().intValue();
        case STRING -> fieldValue.getStringValue();
        case BOOL -> fieldValue.getBooleanValue();
        default -> fieldValue.getValue();
      };
    } else {
      return null;
    }
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) throws Exception {
    if (!Files.exists(CREDENTIALS_PATH)) {
      throw new IllegalStateException(
          "Must provide path to a big query credentials file. By default {module-root}/" + CREDENTIALS_PATH
              + ". Override by setting setting path with the CREDENTIALS_PATH constant.");
    }

    final String fullConfigAsString = new String(Files.readAllBytes(CREDENTIALS_PATH));
    final JsonNode credentialsJson = Jsons.deserialize(fullConfigAsString).get(BigQueryConsts.BIGQUERY_BASIC_CONFIG);
    final String projectId = credentialsJson.get(CONFIG_PROJECT_ID).asText();
    final String datasetLocation = "US";

    final String datasetId = Strings.addRandomSuffix("airbyte_tests", "_", 8);

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(CONFIG_PROJECT_ID, projectId)
        .put(CONFIG_CREDS, credentialsJson.toString())
        .put(CONFIG_DATASET_ID, datasetId)
        .put(CONFIG_DATASET_LOCATION, datasetLocation)
        .build());

    final ServiceAccountCredentials credentials = ServiceAccountCredentials
        .fromStream(new ByteArrayInputStream(credentialsJson.toString().getBytes()));

    bigquery = BigQueryOptions.newBuilder()
        .setProjectId(config.get(CONFIG_PROJECT_ID).asText())
        .setCredentials(credentials)
        .build()
        .getService();

    final DatasetInfo datasetInfo =
        DatasetInfo.newBuilder(config.get(CONFIG_DATASET_ID).asText()).setLocation(config.get(CONFIG_DATASET_LOCATION).asText()).build();
    dataset = bigquery.create(datasetInfo);

    tornDown = false;
    Runtime.getRuntime()
        .addShutdownHook(
            new Thread(
                () -> {
                  if (!tornDown) {
                    tearDownBigQuery();
                  }
                }));
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    tearDownBigQuery();
  }

  private void tearDownBigQuery() {
    // allows deletion of a dataset that has contents
    final BigQuery.DatasetDeleteOption option = BigQuery.DatasetDeleteOption.deleteContents();

    final boolean success = bigquery.delete(dataset.getDatasetId(), option);
    if (success) {
      LOGGER.info("BQ Dataset " + dataset + " deleted...");
    } else {
      LOGGER.info("BQ Dataset cleanup for " + dataset + " failed!");
    }

    tornDown = true;
  }

  // todo (cgardens) - figure out how to share these helpers. they are currently copied from
  // BigQueryDestination.
  private static ImmutablePair<Job, String> executeQuery(BigQuery bigquery, QueryJobConfiguration queryConfig) {
    final JobId jobId = JobId.of(UUID.randomUUID().toString());
    final Job queryJob = bigquery.create(JobInfo.newBuilder(queryConfig).setJobId(jobId).build());
    return executeQuery(queryJob);
  }

  private static ImmutablePair<Job, String> executeQuery(Job queryJob) {
    final Job completedJob = waitForQuery(queryJob);
    if (completedJob == null) {
      throw new RuntimeException("Job no longer exists");
    } else if (completedJob.getStatus().getError() != null) {
      // You can also look at queryJob.getStatus().getExecutionErrors() for all
      // errors, not just the latest one.
      return ImmutablePair.of(null, (completedJob.getStatus().getError().toString()));
    }

    return ImmutablePair.of(completedJob, null);
  }

  private static Job waitForQuery(Job queryJob) {
    try {
      return queryJob.waitFor();
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

}
