/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.standardtest.destination.DataArgumentsProvider;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
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
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ArgumentsSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryDenormalizedGscDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDenormalizedGscDestinationAcceptanceTest.class);

  private static final Path CREDENTIALS_PATH = Path.of("secrets/credentials.json");

  private static final String CONFIG_DATASET_ID = "dataset_id";
  private static final String CONFIG_PROJECT_ID = "project_id";
  private static final String CONFIG_DATASET_LOCATION = "dataset_location";
  private static final List<String> AIRBYTE_COLUMNS = List.of(JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_EMITTED_AT);

  private BigQuery bigquery;
  private Dataset dataset;
  private boolean tornDown;
  private JsonNode config;
  private final StandardNameTransformer namingResolver = new StandardNameTransformer();

  @Override
  protected String getImageName() {
    return "airbyte/destination-bigquery-denormalized:dev";
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
  protected boolean supportsDBT() {
    return true;
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected String getDefaultSchema(final JsonNode config) {
    return config.get(CONFIG_DATASET_ID).asText();
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv testEnv, final String streamName, final String namespace)
      throws Exception {
    final String tableName = namingResolver.getIdentifier(streamName);
    final String schema = namingResolver.getIdentifier(namespace);
    return retrieveRecordsFromTable(tableName, schema);
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv env,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    return new ArrayList<>(retrieveRecordsFromTable(namingResolver.getIdentifier(streamName), namingResolver.getIdentifier(namespace)));
  }

  @Override
  protected List<String> resolveIdentifier(final String identifier) {
    final List<String> result = new ArrayList<>();
    result.add(identifier);
    result.add(namingResolver.getIdentifier(identifier));
    return result;
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schema) throws InterruptedException {
    final QueryJobConfiguration queryConfig =
        QueryJobConfiguration
            .newBuilder(
                String.format("SELECT * FROM `%s`.`%s` order by %s asc;", schema, tableName,
                    JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
            .setUseLegacySql(false).build();

    final TableResult queryResults = executeQuery(bigquery, queryConfig).getLeft().getQueryResults();
    final FieldList fields = queryResults.getSchema().getFields();

    return StreamSupport
        .stream(queryResults.iterateAll().spliterator(), false)
        .map(row -> {
          final Map<String, Object> jsonMap = Maps.newHashMap();
          for (final Field field : fields) {
            final Object value = getTypedFieldValue(row, field);
            if (!isAirbyteColumn(field.getName()) && value != null) {
              jsonMap.put(field.getName(), value);
            }
          }
          return jsonMap;
        })
        .map(Jsons::jsonNode)
        .collect(Collectors.toList());
  }

  private boolean isAirbyteColumn(final String name) {
    if (AIRBYTE_COLUMNS.contains(name)) {
      return true;
    }
    return name.startsWith("_airbyte") && name.endsWith("_hashid");
  }

  private Object getTypedFieldValue(final FieldValueList row, final Field field) {
    final FieldValue fieldValue = row.get(field.getName());
    if (fieldValue.getValue() != null) {
      return switch (field.getType().getStandardType()) {
        case FLOAT64, NUMERIC -> fieldValue.getDoubleValue();
        case INT64 -> fieldValue.getNumericValue().intValue();
        case STRING -> fieldValue.getStringValue();
        case BOOL -> fieldValue.getBooleanValue();
        case STRUCT -> fieldValue.getRecordValue().toString();
        default -> fieldValue.getValue();
      };
    } else {
      return null;
    }
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) throws Exception {
    if (!Files.exists(CREDENTIALS_PATH)) {
      throw new IllegalStateException(
          "Must provide path to a big query credentials file. By default {module-root}/" + CREDENTIALS_PATH
              + ". Override by setting setting path with the CREDENTIALS_PATH constant.");
    }

    final String fullConfigFromSecretFileAsString = new String(Files.readAllBytes(CREDENTIALS_PATH));

    final JsonNode fullConfigFromSecretFileJson = Jsons.deserialize(fullConfigFromSecretFileAsString);
    final JsonNode bigqueryConfigFromSecretFile = fullConfigFromSecretFileJson.get(BigQueryConsts.BIGQUERY_BASIC_CONFIG);
    final JsonNode gcsConfigFromSecretFile = fullConfigFromSecretFileJson.get(BigQueryConsts.GCS_CONFIG);

    final String projectId = bigqueryConfigFromSecretFile.get(CONFIG_PROJECT_ID).asText();
    final String datasetLocation = "US";

    final String datasetId = Strings.addRandomSuffix("airbyte_tests", "_", 8);

    final JsonNode gcsCredentialFromSecretFile = gcsConfigFromSecretFile.get(BigQueryConsts.CREDENTIAL);
    final JsonNode credential = Jsons.jsonNode(ImmutableMap.builder()
        .put(BigQueryConsts.CREDENTIAL_TYPE, gcsCredentialFromSecretFile.get(BigQueryConsts.CREDENTIAL_TYPE))
        .put(BigQueryConsts.HMAC_KEY_ACCESS_ID, gcsCredentialFromSecretFile.get(BigQueryConsts.HMAC_KEY_ACCESS_ID))
        .put(BigQueryConsts.HMAC_KEY_ACCESS_SECRET, gcsCredentialFromSecretFile.get(BigQueryConsts.HMAC_KEY_ACCESS_SECRET))
        .build());

    final JsonNode loadingMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put(BigQueryConsts.METHOD, BigQueryConsts.GCS_STAGING)
        .put(BigQueryConsts.GCS_BUCKET_NAME, gcsConfigFromSecretFile.get(BigQueryConsts.GCS_BUCKET_NAME))
        .put(BigQueryConsts.GCS_BUCKET_PATH, gcsConfigFromSecretFile.get(BigQueryConsts.GCS_BUCKET_PATH).asText() + System.currentTimeMillis())
        .put(BigQueryConsts.PART_SIZE, gcsConfigFromSecretFile.get(BigQueryConsts.PART_SIZE))
        .put(BigQueryConsts.CREDENTIAL, credential)
        .build());

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(BigQueryConsts.CONFIG_PROJECT_ID, projectId)
        .put(BigQueryConsts.CONFIG_CREDS, bigqueryConfigFromSecretFile.toString())
        .put(BigQueryConsts.CONFIG_DATASET_ID, datasetId)
        .put(BigQueryConsts.CONFIG_DATASET_LOCATION, datasetLocation)
        .put(BigQueryConsts.LOADING_METHOD, loadingMethod)
        .build());

    final ServiceAccountCredentials credentials = ServiceAccountCredentials
        .fromStream(new ByteArrayInputStream(bigqueryConfigFromSecretFile.toString().getBytes()));

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
  protected void tearDown(final TestDestinationEnv testEnv) {
    // gcs tmp files are supposed to be removed automatically by consumer
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
  private static ImmutablePair<Job, String> executeQuery(final BigQuery bigquery, final QueryJobConfiguration queryConfig) {
    final JobId jobId = JobId.of(UUID.randomUUID().toString());
    final Job queryJob = bigquery.create(JobInfo.newBuilder(queryConfig).setJobId(jobId).build());
    return executeQuery(queryJob);
  }

  private static ImmutablePair<Job, String> executeQuery(final Job queryJob) {
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

  private static Job waitForQuery(final Job queryJob) {
    try {
      return queryJob.waitFor();
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  /**
   * Verify that the integration successfully writes normalized records successfully (without actually
   * running the normalization module) Tests a wide variety of messages an schemas (aspirationally,
   * anyway).
   */
  @ParameterizedTest
  @ArgumentsSource(DataArgumentsProvider.class)
  public void testSyncNormalizedWithoutNormalization(final String messagesFilename, final String catalogFilename) throws Exception {
    final AirbyteCatalog catalog = Jsons.deserialize(MoreResources.readResource(catalogFilename), AirbyteCatalog.class);
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);
    final List<AirbyteMessage> messages = MoreResources.readResource(messagesFilename).lines()
        .map(record -> Jsons.deserialize(record, AirbyteMessage.class)).collect(Collectors.toList());

    final JsonNode config = getConfig();
    // don't run normalization though
    runSyncAndVerifyStateOutput(config, messages, configuredCatalog, false);

    final String defaultSchema = getDefaultSchema(config);
    final List<AirbyteRecordMessage> actualMessages = retrieveNormalizedRecords(catalog, defaultSchema);
    assertSameMessages(messages, actualMessages, true);
  }

}
