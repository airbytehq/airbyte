/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.util;

import static io.airbyte.integrations.destination.bigquery.BigQueryDenormalizedTestConstants.CONFIG_CREDS;
import static io.airbyte.integrations.destination.bigquery.BigQueryDenormalizedTestConstants.CONFIG_DATASET_ID;
import static io.airbyte.integrations.destination.bigquery.BigQueryDenormalizedTestConstants.CONFIG_DATASET_LOCATION;
import static io.airbyte.integrations.destination.bigquery.BigQueryDenormalizedTestConstants.CONFIG_PROJECT_ID;
import static io.airbyte.integrations.destination.bigquery.BigQueryDenormalizedTestConstants.CREDENTIALS_PATH;
import static io.airbyte.integrations.destination.bigquery.BigQueryDenormalizedTestConstants.USERS_STREAM_NAME;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.auth.oauth2.ServiceAccountCredentials;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.DatasetInfo;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.destination.bigquery.BigQueryConsts;
import io.airbyte.integrations.destination.bigquery.BigQueryDenormalizedDestination;
import io.airbyte.integrations.destination.bigquery.BigQueryDenormalizedTestConstants;
import io.airbyte.integrations.destination.bigquery.BigQueryDestination;
import io.airbyte.integrations.destination.bigquery.BigQueryUtils;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashSet;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryDenormalizedTestDataUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDenormalizedTestDataUtils.class);

  private static final String JSON_FILES_BASE_LOCATION = "testdata/";

  public static JsonNode getSchema() {
    return getTestDataFromResourceJson("schema.json");
  }

  public static JsonNode getAnyOfSchema() {
    return getTestDataFromResourceJson("schemaAnyOfAllOf.json");
  }

  public static JsonNode getSchemaWithFormats() {
    return getTestDataFromResourceJson("schemaWithFormats.json");
  }

  public static JsonNode getSchemaWithDateTime() {
    return getTestDataFromResourceJson("schemaWithDateTime.json");
  }

  public static JsonNode getSchemaWithInvalidArrayType() {
    return getTestDataFromResourceJson("schemaWithInvalidArrayType.json");
  }

  public static JsonNode getSchemaArrays() {
    return getTestDataFromResourceJson("schemaArrays.json");
  }

  public static JsonNode getDataArrays() {
    return getTestDataFromResourceJson("dataArrays.json");
  }

  public static JsonNode getSchemaTooDeepNestedDepth() {
    return getTestDataFromResourceJson("schemaTooDeepNestedDepth.json");
  }

  public static JsonNode getDataTooDeepNestedDepth() {
    return getTestDataFromResourceJson("dataTooDeepNestedDepth.json");
  }

  public static JsonNode getSchemaMaxNestedDepth() {
    return getTestDataFromResourceJson("schemaMaxNestedDepth.json");
  }

  public static JsonNode getDataMaxNestedDepth() {
    return getTestDataFromResourceJson("dataMaxNestedDepth.json");
  }

  public static JsonNode getExpectedDataArrays() {
    return getTestDataFromResourceJson("expectedDataArrays.json");
  }

  public static JsonNode getData() {
    return getTestDataFromResourceJson("data.json");
  }

  public static JsonNode getDataWithFormats() {
    return getTestDataFromResourceJson("dataWithFormats.json");
  }

  public static JsonNode getAnyOfFormats() {
    return getTestDataFromResourceJson("dataAnyOfFormats.json");
  }

  public static JsonNode getAnyOfFormatsWithNull() {
    return getTestDataFromResourceJson("dataAnyOfFormatsWithNull.json");
  }

  public static JsonNode getAnyOfFormatsWithEmptyList() {
    return getTestDataFromResourceJson("dataAnyOfFormatsWithEmptyList.json");
  }

  public static JsonNode getDataWithJSONDateTimeFormats() {
    return getTestDataFromResourceJson("dataWithJSONDateTimeFormats.json");
  }

  public static JsonNode getDataWithJSONWithReference() {
    return getTestDataFromResourceJson("dataWithJSONWithReference.json");
  }

  public static JsonNode getSchemaWithReferenceDefinition() {
    return getTestDataFromResourceJson("schemaWithReferenceDefinition.json");
  }

  public static JsonNode getSchemaWithNestedDatetimeInsideNullObject() {
    return getTestDataFromResourceJson("schemaWithNestedDatetimeInsideNullObject.json");
  }

  public static JsonNode getDataWithEmptyObjectAndArray() {
    return getTestDataFromResourceJson("dataWithEmptyObjectAndArray.json");
  }

  public static JsonNode getDataWithNestedDatetimeInsideNullObject() {
    return getTestDataFromResourceJson("dataWithNestedDatetimeInsideNullObject.json");

  }

  private static JsonNode getTestDataFromResourceJson(final String fileName) {
    final String fileContent;
    try {
      fileContent = Files.readString(Path.of(BigQueryDenormalizedTestDataUtils.class.getClassLoader()
          .getResource(JSON_FILES_BASE_LOCATION + fileName).getPath()));
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
    return Jsons.deserialize(fileContent);
  }

  public static ConfiguredAirbyteCatalog getCommonCatalog(final JsonNode schema, final String datasetId) {
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(new ConfiguredAirbyteStream()
        .withStream(new AirbyteStream().withName(USERS_STREAM_NAME).withNamespace(datasetId).withJsonSchema(schema)
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH)))
        .withSyncMode(SyncMode.FULL_REFRESH).withDestinationSyncMode(DestinationSyncMode.OVERWRITE)));
  }

  public static void runDestinationWrite(ConfiguredAirbyteCatalog catalog, JsonNode config, AirbyteMessage... messages) throws Exception {
    final BigQueryDestination destination = new BigQueryDenormalizedDestination();
    final AirbyteMessageConsumer consumer = destination.getConsumer(config, catalog, Destination::defaultOutputRecordCollector);

    consumer.start();
    for (AirbyteMessage message : messages) {
      consumer.accept(message);
    }
    consumer.close();
  }

  private static void checkCredentialPath() {
    if (!Files.exists(CREDENTIALS_PATH)) {
      throw new IllegalStateException(
          "Must provide path to a big query credentials file. By default {module-root}/" + CREDENTIALS_PATH
              + ". Override by setting setting path with the CREDENTIALS_PATH constant.");
    }
  }

  public static JsonNode createCommonConfig() throws IOException {
    checkCredentialPath();

    final String credentialsJsonString = Files.readString(CREDENTIALS_PATH);
    final JsonNode credentialsJson = Jsons.deserialize(credentialsJsonString).get(BigQueryConsts.BIGQUERY_BASIC_CONFIG);
    final String projectId = credentialsJson.get(CONFIG_PROJECT_ID).asText();
    final String datasetLocation = "US";
    final String datasetId = Strings.addRandomSuffix("airbyte_tests", "_", 8);

    return Jsons.jsonNode(ImmutableMap.builder()
        .put(CONFIG_PROJECT_ID, projectId)
        .put(BigQueryDenormalizedTestConstants.CONFIG_CREDS, credentialsJson.toString())
        .put(CONFIG_DATASET_ID, datasetId)
        .put(CONFIG_DATASET_LOCATION, datasetLocation)
        .build());
  }

  public static JsonNode createGcsConfig() throws IOException {
    checkCredentialPath();

    final String credentialsJsonString = Files.readString(CREDENTIALS_PATH);

    final JsonNode fullConfigFromSecretFileJson = Jsons.deserialize(credentialsJsonString);
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
        .put(BigQueryConsts.CREDENTIAL, credential)
        .build());

    return Jsons.jsonNode(ImmutableMap.builder()
        .put(BigQueryConsts.CONFIG_PROJECT_ID, projectId)
        .put(BigQueryConsts.CONFIG_CREDS, bigqueryConfigFromSecretFile.toString())
        .put(BigQueryConsts.CONFIG_DATASET_ID, datasetId)
        .put(BigQueryConsts.CONFIG_DATASET_LOCATION, datasetLocation)
        .put(BigQueryConsts.LOADING_METHOD, loadingMethod)
        .build());
  }

  public static BigQuery configureBigQuery(final JsonNode config) throws IOException {
    final ServiceAccountCredentials credentials = ServiceAccountCredentials
        .fromStream(new ByteArrayInputStream(config.get(CONFIG_CREDS).asText().getBytes(StandardCharsets.UTF_8)));

    return BigQueryOptions.newBuilder()
        .setProjectId(config.get(CONFIG_PROJECT_ID).asText())
        .setCredentials(credentials)
        .build()
        .getService();
  }

  public static Dataset getBigQueryDataSet(final JsonNode config, final BigQuery bigQuery) {
    final DatasetInfo datasetInfo =
        DatasetInfo.newBuilder(BigQueryUtils.getDatasetId(config)).setLocation(config.get(CONFIG_DATASET_LOCATION).asText()).build();
    Dataset dataset = bigQuery.create(datasetInfo);
    trackTestDataSet(dataset, bigQuery);
    return dataset;
  }

  private static Set<Dataset> dataSetsForDrop = new HashSet<>();

  public static void trackTestDataSet(final Dataset dataset, final BigQuery bigQuery) {
    Runtime.getRuntime()
        .addShutdownHook(
            new Thread(
                () -> tearDownBigQuery(dataset, bigQuery)));
  }

  public static synchronized void tearDownBigQuery(final Dataset dataset, final BigQuery bigQuery) {
    if (dataSetsForDrop.contains(dataset)) {
      // allows deletion of a dataset that has contents
      final BigQuery.DatasetDeleteOption option = BigQuery.DatasetDeleteOption.deleteContents();

      final boolean success = bigQuery.delete(dataset.getDatasetId(), option);
      if (success) {
        LOGGER.info("BQ Dataset " + dataset + " deleted...");
      } else {
        LOGGER.info("BQ Dataset cleanup for " + dataset + " failed!");
      }
      dataSetsForDrop.remove(dataset);
    }
  }

}
