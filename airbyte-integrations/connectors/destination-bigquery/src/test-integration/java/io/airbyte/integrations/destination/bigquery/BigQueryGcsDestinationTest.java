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

import static java.util.stream.Collectors.toList;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.spy;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.DeleteObjectsRequest.KeyVersion;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.auth.oauth2.ServiceAccountCredentials;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.DatasetInfo;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.GcsS3Helper;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.LinkedList;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInfo;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class BigQueryGcsDestinationTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryGcsDestinationTest.class);
  private static final Path CREDENTIALS_PATH = Path.of("secrets/credentials.json");

  private static final String BIG_QUERY_CLIENT_CHUNK_SIZE = "big_query_client_buffer_size_mb";
  private static final Instant NOW = Instant.now();
  private static final String USERS_STREAM_NAME = "users";
  private static final String TASKS_STREAM_NAME = "tasks";
  private static final AirbyteMessage MESSAGE_USERS1 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
      .withRecord(new AirbyteRecordMessage().withStream(USERS_STREAM_NAME)
          .withData(Jsons.jsonNode(ImmutableMap.builder().put("name", "john").put("id", "10").build()))
          .withEmittedAt(NOW.toEpochMilli()));
  private static final AirbyteMessage MESSAGE_USERS2 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
      .withRecord(new AirbyteRecordMessage().withStream(USERS_STREAM_NAME)
          .withData(Jsons.jsonNode(ImmutableMap.builder().put("name", "susan").put("id", "30").build()))
          .withEmittedAt(NOW.toEpochMilli()));
  private static final AirbyteMessage MESSAGE_TASKS1 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
      .withRecord(new AirbyteRecordMessage().withStream(TASKS_STREAM_NAME)
          .withData(Jsons.jsonNode(ImmutableMap.builder().put("goal", "announce the game.").build()))
          .withEmittedAt(NOW.toEpochMilli()));
  private static final AirbyteMessage MESSAGE_TASKS2 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
      .withRecord(new AirbyteRecordMessage().withStream(TASKS_STREAM_NAME)
          .withData(Jsons.jsonNode(ImmutableMap.builder().put("goal", "ship some code.").build()))
          .withEmittedAt(NOW.toEpochMilli()));
  private static final AirbyteMessage MESSAGE_STATE = new AirbyteMessage().withType(AirbyteMessage.Type.STATE)
      .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.builder().put("checkpoint", "now!").build())));

  private static final NamingConventionTransformer NAMING_RESOLVER = new StandardNameTransformer();

  private JsonNode config;

  private BigQuery bigquery;
  private AmazonS3 s3Client;
  private Dataset dataset;
  private ConfiguredAirbyteCatalog catalog;

  private boolean tornDown = true;

  @BeforeEach
  void setup(TestInfo info) throws IOException {
    if (info.getDisplayName().equals("testSpec()")) {
      return;
    }

    if (!Files.exists(CREDENTIALS_PATH)) {
      throw new IllegalStateException(
          "Must provide path to a big query credentials file. By default {module-root}/config/credentials.json. Override by setting setting path with the CREDENTIALS_PATH constant.");
    }
    final String fullConfigAsString = new String(Files.readAllBytes(CREDENTIALS_PATH));
    final JsonNode credentialsJson = Jsons.deserialize(fullConfigAsString).get(BigQueryConsts.BIGQUERY_BASIC_CONFIG);
    final JsonNode credentialsGcsJson = Jsons.deserialize(fullConfigAsString).get(BigQueryConsts.GCS_CONFIG);

    final String projectId = credentialsJson.get(BigQueryConsts.CONFIG_PROJECT_ID).asText();

    final ServiceAccountCredentials credentials = ServiceAccountCredentials
        .fromStream(new ByteArrayInputStream(credentialsJson.toString().getBytes()));
    bigquery = BigQueryOptions.newBuilder()
        .setProjectId(projectId)
        .setCredentials(credentials)
        .build()
        .getService();

    final String datasetId = Strings.addRandomSuffix("airbyte_tests", "_", 8);
    final String datasetLocation = "EU";
    MESSAGE_USERS1.getRecord().setNamespace(datasetId);
    MESSAGE_USERS2.getRecord().setNamespace(datasetId);
    MESSAGE_TASKS1.getRecord().setNamespace(datasetId);
    MESSAGE_TASKS2.getRecord().setNamespace(datasetId);

    catalog = new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        CatalogHelpers.createConfiguredAirbyteStream(USERS_STREAM_NAME, datasetId,
            Field.of("name", JsonSchemaPrimitive.STRING),
            Field
                .of("id", JsonSchemaPrimitive.STRING)),
        CatalogHelpers.createConfiguredAirbyteStream(TASKS_STREAM_NAME, datasetId, Field.of("goal", JsonSchemaPrimitive.STRING))));

    final DatasetInfo datasetInfo = DatasetInfo.newBuilder(datasetId).setLocation(datasetLocation).build();
    dataset = bigquery.create(datasetInfo);

    JsonNode credentialFromSecretFile = credentialsGcsJson.get(BigQueryConsts.CREDENTIAL);
    JsonNode credential = Jsons.jsonNode(ImmutableMap.builder()
        .put(BigQueryConsts.CREDENTIAL_TYPE, credentialFromSecretFile.get(BigQueryConsts.CREDENTIAL_TYPE))
        .put(BigQueryConsts.HMAC_KEY_ACCESS_ID, credentialFromSecretFile.get(BigQueryConsts.HMAC_KEY_ACCESS_ID))
        .put(BigQueryConsts.HMAC_KEY_ACCESS_SECRET, credentialFromSecretFile.get(BigQueryConsts.HMAC_KEY_ACCESS_SECRET))
        .build());

    JsonNode loadingMethod = Jsons.jsonNode(ImmutableMap.builder()
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

    GcsDestinationConfig gcsDestinationConfig = GcsDestinationConfig
        .getGcsDestinationConfig(BigQueryUtils.getGcsJsonNodeConfig(config));
    this.s3Client = GcsS3Helper.getGcsS3Client(gcsDestinationConfig);

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

  @AfterEach
  void tearDown(TestInfo info) {
    if (info.getDisplayName().equals("testSpec()")) {
      return;
    }

    tearDownGcs();
    tearDownBigQuery();
  }

  /**
   * Remove all the GCS output from the tests.
   */
  protected void tearDownGcs() {
    JsonNode properties = config.get(BigQueryConsts.LOADING_METHOD);
    String gcsBucketName = properties.get(BigQueryConsts.GCS_BUCKET_NAME).asText();
    String gcs_bucket_path = properties.get(BigQueryConsts.GCS_BUCKET_PATH).asText();

    List<KeyVersion> keysToDelete = new LinkedList<>();
    List<S3ObjectSummary> objects = s3Client
        .listObjects(gcsBucketName, gcs_bucket_path)
        .getObjectSummaries();
    for (S3ObjectSummary object : objects) {
      keysToDelete.add(new KeyVersion(object.getKey()));
    }

    if (keysToDelete.size() > 0) {
      LOGGER.info("Tearing down test bucket path: {}/{}", gcsBucketName, gcs_bucket_path);
      // Google Cloud Storage doesn't accept request to delete multiple objects
      for (KeyVersion keyToDelete : keysToDelete) {
        s3Client.deleteObject(gcsBucketName, keyToDelete.getKey());
      }
      LOGGER.info("Deleted {} file(s).", keysToDelete.size());
    }
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

  @Test
  void testSpec() throws Exception {
    final ConnectorSpecification actual = new BigQueryDestination().spec();
    final String resourceString = MoreResources.readResource("spec.json");
    final ConnectorSpecification expected = Jsons.deserialize(resourceString, ConnectorSpecification.class);

    assertEquals(expected, actual);
  }

  @Test
  void testCheckSuccess() {
    final AirbyteConnectionStatus actual = new BigQueryDestination().check(config);
    final AirbyteConnectionStatus expected = new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    assertEquals(expected, actual);
  }

  @Test
  void testCheckFailure() {
    ((ObjectNode) config).put(BigQueryConsts.CONFIG_PROJECT_ID, "fake");
    final AirbyteConnectionStatus actual = new BigQueryDestination().check(config);
    final String actualMessage = actual.getMessage();
    LOGGER.info("Checking expected failure message:" + actualMessage);
    assertTrue(actualMessage.contains("Access Denied:"));
    final AirbyteConnectionStatus expected = new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage("");
    assertEquals(expected, actual.withMessage(""));
  }

  @Test
  void testWriteSuccess() throws Exception {
    final BigQueryDestination destination = new BigQueryDestination();
    final AirbyteMessageConsumer consumer = destination.getConsumer(config, catalog, Destination::defaultOutputRecordCollector);

    consumer.accept(MESSAGE_USERS1);
    consumer.accept(MESSAGE_TASKS1);
    consumer.accept(MESSAGE_USERS2);
    consumer.accept(MESSAGE_TASKS2);
    consumer.accept(MESSAGE_STATE);
    consumer.close();

    final List<JsonNode> usersActual = retrieveRecords(NAMING_RESOLVER.getRawTableName(USERS_STREAM_NAME));
    final List<JsonNode> expectedUsersJson = Lists.newArrayList(MESSAGE_USERS1.getRecord().getData(), MESSAGE_USERS2.getRecord().getData());
    assertEquals(expectedUsersJson.size(), usersActual.size());
    assertTrue(expectedUsersJson.containsAll(usersActual) && usersActual.containsAll(expectedUsersJson));

    final List<JsonNode> tasksActual = retrieveRecords(NAMING_RESOLVER.getRawTableName(TASKS_STREAM_NAME));
    final List<JsonNode> expectedTasksJson = Lists.newArrayList(MESSAGE_TASKS1.getRecord().getData(), MESSAGE_TASKS2.getRecord().getData());
    assertEquals(expectedTasksJson.size(), tasksActual.size());
    assertTrue(expectedTasksJson.containsAll(tasksActual) && tasksActual.containsAll(expectedTasksJson));

    assertTmpTablesNotPresent(catalog.getStreams()
        .stream()
        .map(ConfiguredAirbyteStream::getStream)
        .map(AirbyteStream::getName)
        .collect(Collectors.toList()));
  }

  @Test
  void testWriteFailure() throws Exception {
    // hack to force an exception to be thrown from within the consumer.
    final AirbyteMessage spiedMessage = spy(MESSAGE_USERS1);
    doThrow(new RuntimeException()).when(spiedMessage).getRecord();

    final AirbyteMessageConsumer consumer = spy(new BigQueryDestination().getConsumer(config, catalog, Destination::defaultOutputRecordCollector));

    assertThrows(RuntimeException.class, () -> consumer.accept(spiedMessage));
    consumer.accept(MESSAGE_USERS2);
    assertThrows(RuntimeException.class, () -> consumer.close()); // check if fails when data was not loaded to GCS bucket by some reason

    final List<String> tableNames = catalog.getStreams()
        .stream()
        .map(ConfiguredAirbyteStream::getStream)
        .map(AirbyteStream::getName)
        .collect(toList());
    assertTmpTablesNotPresent(catalog.getStreams()
        .stream()
        .map(ConfiguredAirbyteStream::getStream)
        .map(AirbyteStream::getName)
        .collect(Collectors.toList()));
    // assert that no tables were created.
    assertTrue(fetchNamesOfTablesInDb().stream().noneMatch(tableName -> tableNames.stream().anyMatch(tableName::startsWith)));
  }

  private Set<String> fetchNamesOfTablesInDb() throws InterruptedException {
    final QueryJobConfiguration queryConfig = QueryJobConfiguration
        .newBuilder(String.format("SELECT * FROM %s.INFORMATION_SCHEMA.TABLES;", dataset.getDatasetId().getDataset()))
        .setUseLegacySql(false)
        .build();

    return StreamSupport
        .stream(BigQueryUtils.executeQuery(bigquery, queryConfig).getLeft().getQueryResults().iterateAll().spliterator(), false)
        .map(v -> v.get("TABLE_NAME").getStringValue()).collect(Collectors.toSet());
  }

  private void assertTmpTablesNotPresent(List<String> tableNames) throws InterruptedException {
    final Set<String> tmpTableNamePrefixes = tableNames.stream().map(name -> name + "_").collect(Collectors.toSet());
    final Set<String> finalTableNames = tableNames.stream().map(name -> name + "_raw").collect(Collectors.toSet());
    // search for table names that have the tmp table prefix but are not raw tables.
    assertTrue(fetchNamesOfTablesInDb()
        .stream()
        .filter(tableName -> !finalTableNames.contains(tableName))
        .noneMatch(tableName -> tmpTableNamePrefixes.stream().anyMatch(tableName::startsWith)));
  }

  private List<JsonNode> retrieveRecords(String tableName) throws Exception {
    QueryJobConfiguration queryConfig =
        QueryJobConfiguration.newBuilder(String.format("SELECT * FROM %s.%s;", dataset.getDatasetId().getDataset(), tableName.toLowerCase()))
            .setUseLegacySql(false).build();

    BigQueryUtils.executeQuery(bigquery, queryConfig);

    return StreamSupport
        .stream(BigQueryUtils.executeQuery(bigquery, queryConfig).getLeft().getQueryResults().iterateAll().spliterator(), false)
        .map(v -> v.get(JavaBaseConstants.COLUMN_NAME_DATA).getStringValue())
        .map(Jsons::deserialize)
        .collect(Collectors.toList());
  }

}
