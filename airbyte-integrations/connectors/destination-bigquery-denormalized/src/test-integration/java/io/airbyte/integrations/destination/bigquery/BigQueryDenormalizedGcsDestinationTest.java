/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static io.airbyte.integrations.destination.bigquery.formatter.DefaultBigQueryDenormalizedRecordFormatter.NESTED_ARRAY_FIELD;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getSchemaWithDateTime;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getSchemaWithFormats;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.DeleteObjectsRequest;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.auth.oauth2.ServiceAccountCredentials;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.DatasetInfo;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.SyncMode;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Set;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInfo;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class BigQueryDenormalizedGcsDestinationTest extends BigQueryDenormalizedDestinationTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDenormalizedGcsDestinationTest.class);

  private JsonNode config;
  private AmazonS3 s3Client;

  private BigQuery bigquery;
  private Dataset dataset;
  private ConfiguredAirbyteCatalog catalog;
  private String datasetId;

  private boolean tornDown = true;

  @BeforeEach
  void setup(final TestInfo info) throws IOException {
    if (info.getDisplayName().equals("testSpec()")) {
      return;
    }

    if (!Files.exists(CREDENTIALS_PATH)) {
      throw new IllegalStateException(
          "Must provide path to a big query credentials file. By default {module-root}/" + CREDENTIALS_PATH
              + ". Override by setting setting path with the CREDENTIALS_PATH constant.");
    }
    final String credentialsJsonString = Files.readString(CREDENTIALS_PATH);
    final JsonNode credentialsJson = Jsons.deserialize(credentialsJsonString).get(BigQueryConsts.BIGQUERY_BASIC_CONFIG);
    final JsonNode credentialsGcsJson = Jsons.deserialize(credentialsJsonString).get(BigQueryConsts.GCS_CONFIG);

    final String projectId = credentialsJson.get(BigQueryConsts.CONFIG_PROJECT_ID).asText();
    final ServiceAccountCredentials credentials =
        ServiceAccountCredentials.fromStream(new ByteArrayInputStream(credentialsJson.toString().getBytes(StandardCharsets.UTF_8)));
    bigquery = BigQueryOptions.newBuilder()
        .setProjectId(projectId)
        .setCredentials(credentials)
        .build()
        .getService();

    datasetId = Strings.addRandomSuffix("airbyte_tests", "_", 8);
    final String datasetLocation = "EU";
    MESSAGE_USERS1.getRecord().setNamespace(datasetId);
    MESSAGE_USERS2.getRecord().setNamespace(datasetId);
    MESSAGE_USERS3.getRecord().setNamespace(datasetId);
    MESSAGE_USERS4.getRecord().setNamespace(datasetId);
    MESSAGE_USERS5.getRecord().setNamespace(datasetId);
    MESSAGE_USERS6.getRecord().setNamespace(datasetId);
    EMPTY_MESSAGE.getRecord().setNamespace(datasetId);

    final DatasetInfo datasetInfo = DatasetInfo.newBuilder(datasetId).setLocation(datasetLocation).build();
    dataset = bigquery.create(datasetInfo);

    final JsonNode credentialFromSecretFile = credentialsGcsJson.get(BigQueryConsts.CREDENTIAL);
    final JsonNode credential = Jsons.jsonNode(ImmutableMap.builder()
        .put(BigQueryConsts.CREDENTIAL_TYPE, credentialFromSecretFile.get(BigQueryConsts.CREDENTIAL_TYPE))
        .put(BigQueryConsts.HMAC_KEY_ACCESS_ID, credentialFromSecretFile.get(BigQueryConsts.HMAC_KEY_ACCESS_ID))
        .put(BigQueryConsts.HMAC_KEY_ACCESS_SECRET, credentialFromSecretFile.get(BigQueryConsts.HMAC_KEY_ACCESS_SECRET))
        .build());

    final JsonNode loadingMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put(BigQueryConsts.METHOD, BigQueryConsts.GCS_STAGING)
        .put(BigQueryConsts.KEEP_GCS_FILES, BigQueryConsts.KEEP_GCS_FILES_VAL)
        .put(BigQueryConsts.GCS_BUCKET_NAME, credentialsGcsJson.get(BigQueryConsts.GCS_BUCKET_NAME))
        .put(BigQueryConsts.GCS_BUCKET_PATH, credentialsGcsJson.get(BigQueryConsts.GCS_BUCKET_PATH).asText() + System.currentTimeMillis())
        .put(BigQueryConsts.CREDENTIAL, credential)
        .build());

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(BigQueryConsts.CONFIG_PROJECT_ID, projectId)
        .put(BigQueryConsts.CONFIG_CREDS, credentialsJson.toString())
        .put(BigQueryConsts.CONFIG_DATASET_ID, datasetId)
        .put(BigQueryConsts.CONFIG_DATASET_LOCATION, datasetLocation)
        .put(BigQueryConsts.LOADING_METHOD, loadingMethod)
        .put(BIG_QUERY_CLIENT_CHUNK_SIZE, 10)
        .build());

    final GcsDestinationConfig gcsDestinationConfig = GcsDestinationConfig
        .getGcsDestinationConfig(BigQueryUtils.getGcsJsonNodeConfig(config));
    this.s3Client = gcsDestinationConfig.getS3Client();

    tornDown = false;
    Runtime.getRuntime().addShutdownHook(
        new Thread(() -> {
          if (!tornDown) {
            tearDownBigQuery();
          }
        }));
  }

  @AfterEach
  void tearDown(final TestInfo info) {
    super.tearDown(info);
    tearDownGcs();
  }

  /**
   * Remove all the GCS output from the tests.
   */
  protected void tearDownGcs() {
    final JsonNode properties = config.get(BigQueryConsts.LOADING_METHOD);
    final String gcsBucketName = properties.get(BigQueryConsts.GCS_BUCKET_NAME).asText();
    final String gcs_bucket_path = properties.get(BigQueryConsts.GCS_BUCKET_PATH).asText();

    final List<DeleteObjectsRequest.KeyVersion> keysToDelete = new LinkedList<>();
    final List<S3ObjectSummary> objects = s3Client
        .listObjects(gcsBucketName, gcs_bucket_path)
        .getObjectSummaries();
    for (final S3ObjectSummary object : objects) {
      keysToDelete.add(new DeleteObjectsRequest.KeyVersion(object.getKey()));
    }

    if (keysToDelete.size() > 0) {
      LOGGER.info("Tearing down test bucket path: {}/{}", gcsBucketName, gcs_bucket_path);
      // Google Cloud Storage doesn't accept request to delete multiple objects
      for (final DeleteObjectsRequest.KeyVersion keyToDelete : keysToDelete) {
        s3Client.deleteObject(gcsBucketName, keyToDelete.getKey());
      }
      LOGGER.info("Deleted {} file(s).", keysToDelete.size());
    }
  }

//  @Test
//  void testWriteWithFormat() throws Exception {
//    catalog = new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(new ConfiguredAirbyteStream()
//        .withStream(new AirbyteStream().withName(USERS_STREAM_NAME).withNamespace(datasetId).withJsonSchema(getSchemaWithFormats()))
//        .withSyncMode(SyncMode.FULL_REFRESH).withDestinationSyncMode(DestinationSyncMode.OVERWRITE)));
//
//    final BigQueryDestination destination = new BigQueryDenormalizedDestination();
//    final AirbyteMessageConsumer consumer = destination.getConsumer(config, catalog, Destination::defaultOutputRecordCollector);
//
//    consumer.start();
//    consumer.accept(MESSAGE_USERS3);
//    consumer.close();
//
//    final List<JsonNode> usersActual = retrieveRecordsAsJson(USERS_STREAM_NAME);
//    final JsonNode expectedUsersJson = MESSAGE_USERS3.getRecord().getData();
//    assertEquals(usersActual.size(), 1);
//    final JsonNode resultJson = usersActual.get(0);
//    assertEquals(extractJsonValues(resultJson, "name"), extractJsonValues(expectedUsersJson, "name"));
//    assertEquals(extractJsonValues(resultJson, "date_of_birth"), extractJsonValues(expectedUsersJson, "date_of_birth"));
//
//    // Bigquery's datetime type accepts multiple input format but always outputs the same, so we can't
//    // expect to receive the value we sent.
//    assertEquals(extractJsonValues(resultJson, "updated_at"), Set.of("2021-10-11T06:36:53Z"));
//
//    final Schema expectedSchema = Schema.of(
//        Field.of("name", StandardSQLTypeName.STRING),
//        Field.of("date_of_birth", StandardSQLTypeName.DATE),
//        Field.of("updated_at", StandardSQLTypeName.DATETIME),
//        Field.of(JavaBaseConstants.COLUMN_NAME_AB_ID, StandardSQLTypeName.STRING),
//        Field.of(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, StandardSQLTypeName.TIMESTAMP));
//    final Schema actualSchema = BigQueryUtils.getTableDefinition(bigquery, dataset.getDatasetId().getDataset(), USERS_STREAM_NAME).getSchema();
//
//    assertNotNull(actualSchema);
//    actualSchema.getFields().forEach(actualField ->
//        assertEquals(
//            expectedSchema.getFields().get(actualField.getName()),
//            Field.of(actualField.getName(), actualField.getType())));
//  }

//  @Test
//  void testIfJSONDateTimeWasConvertedToBigQueryFormat() throws Exception {
//    catalog = new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(new ConfiguredAirbyteStream()
//        .withStream(new AirbyteStream().withName(USERS_STREAM_NAME).withNamespace(datasetId).withJsonSchema(getSchemaWithDateTime()))
//        .withSyncMode(SyncMode.FULL_REFRESH).withDestinationSyncMode(DestinationSyncMode.OVERWRITE)));
//
//    final BigQueryDestination destination = new BigQueryDenormalizedDestination();
//    final AirbyteMessageConsumer consumer = destination.getConsumer(config, catalog, Destination::defaultOutputRecordCollector);
//
//    consumer.start();
//    consumer.accept(MESSAGE_USERS4);
//    consumer.close();
//
//    final List<JsonNode> usersActual = retrieveRecordsAsJson(USERS_STREAM_NAME);
//    assertEquals(usersActual.size(), 1);
//    final JsonNode resultJson = usersActual.get(0);
//
//    // BigQuery Accepts "YYYY-MM-DD HH:MM:SS[.SSSSSS]" format
//    // returns "yyyy-MM-dd'T'HH:mm:ss" format
//    assertEquals(Set.of("2021-10-11T06:36:53Z"), extractJsonValues(resultJson, "updated_at"));
//    // check nested datetime
//    assertEquals(Set.of("2021-11-11T06:36:53Z"),
//        extractJsonValues(resultJson.get("items"), "nested_datetime"));
//  }

  private Set<String> extractJsonValues(final JsonNode node, final String attributeName) {
    final List<JsonNode> valuesNode = node.findValues(attributeName);
    final Set<String> resultSet = new HashSet<>();
    valuesNode.forEach(jsonNode -> {
      if (jsonNode.isArray()) {
        jsonNode.forEach(arrayNodeValue -> resultSet.add(arrayNodeValue.textValue()));
      } else if (jsonNode.isObject()) {
        resultSet.addAll(extractJsonValues(jsonNode, NESTED_ARRAY_FIELD));
      } else {
        resultSet.add(jsonNode.textValue());
      }
    });

    return resultSet;
  }

}
