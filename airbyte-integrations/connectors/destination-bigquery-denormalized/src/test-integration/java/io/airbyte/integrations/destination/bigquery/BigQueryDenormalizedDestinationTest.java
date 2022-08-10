/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getAnyOfFormats;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getAnyOfFormatsWithEmptyList;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getAnyOfFormatsWithNull;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getAnyOfSchema;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getData;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getDataWithEmptyObjectAndArray;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getDataWithFormats;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getDataWithJSONDateTimeFormats;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getDataWithJSONWithReference;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getDataWithNestedDatetimeInsideNullObject;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getSchema;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getSchemaWithDateTime;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getSchemaWithFormats;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getSchemaWithInvalidArrayType;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getSchemaWithNestedDatetimeInsideNullObject;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getSchemaWithReferenceDefinition;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.params.provider.Arguments.arguments;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.auth.oauth2.ServiceAccountCredentials;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.DatasetInfo;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.SyncMode;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;
import org.assertj.core.util.Sets;
import org.joda.time.DateTime;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInfo;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class BigQueryDenormalizedDestinationTest {

  private static final Path CREDENTIALS_PATH = Path.of("secrets/credentials.json");
  private static final Set<String> AIRBYTE_METADATA_FIELDS = Set.of(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, JavaBaseConstants.COLUMN_NAME_AB_ID);

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDenormalizedDestinationTest.class);

  private static final String BIG_QUERY_CLIENT_CHUNK_SIZE = "big_query_client_buffer_size_mb";
  private static final Instant NOW = Instant.now();
  private static final String USERS_STREAM_NAME = "users";
  private static final AirbyteMessage MESSAGE_USERS1 = createRecordMessage(USERS_STREAM_NAME, getData());
  private static final AirbyteMessage MESSAGE_USERS2 = createRecordMessage(USERS_STREAM_NAME, getDataWithEmptyObjectAndArray());
  private static final AirbyteMessage MESSAGE_USERS3 = createRecordMessage(USERS_STREAM_NAME, getDataWithFormats());
  private static final AirbyteMessage MESSAGE_USERS4 = createRecordMessage(USERS_STREAM_NAME, getDataWithJSONDateTimeFormats());
  private static final AirbyteMessage MESSAGE_USERS5 = createRecordMessage(USERS_STREAM_NAME, getDataWithJSONWithReference());
  private static final AirbyteMessage MESSAGE_USERS6 = createRecordMessage(USERS_STREAM_NAME, Jsons.deserialize("{\"users\":null}"));
  private static final AirbyteMessage MESSAGE_USERS7 = createRecordMessage(USERS_STREAM_NAME, getDataWithNestedDatetimeInsideNullObject());
  private static final AirbyteMessage MESSAGE_USERS8 = createRecordMessage(USERS_STREAM_NAME, getAnyOfFormats());
  private static final AirbyteMessage MESSAGE_USERS9 = createRecordMessage(USERS_STREAM_NAME, getAnyOfFormatsWithNull());
  private static final AirbyteMessage MESSAGE_USERS10 = createRecordMessage(USERS_STREAM_NAME, getAnyOfFormatsWithEmptyList());
  private static final AirbyteMessage EMPTY_MESSAGE = createRecordMessage(USERS_STREAM_NAME, Jsons.deserialize("{}"));

  private JsonNode config;

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
    MESSAGE_USERS7.getRecord().setNamespace(datasetId);
    MESSAGE_USERS8.getRecord().setNamespace(datasetId);
    MESSAGE_USERS9.getRecord().setNamespace(datasetId);
    MESSAGE_USERS10.getRecord().setNamespace(datasetId);
    EMPTY_MESSAGE.getRecord().setNamespace(datasetId);

    final DatasetInfo datasetInfo = DatasetInfo.newBuilder(datasetId).setLocation(datasetLocation).build();
    dataset = bigquery.create(datasetInfo);

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(BigQueryConsts.CONFIG_PROJECT_ID, projectId)
        .put(BigQueryConsts.CONFIG_CREDS, credentialsJson.toString())
        .put(BigQueryConsts.CONFIG_DATASET_ID, datasetId)
        .put(BigQueryConsts.CONFIG_DATASET_LOCATION, datasetLocation)
        .put(BIG_QUERY_CLIENT_CHUNK_SIZE, 10)
        .build());

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
  void tearDown(final TestInfo info) {
    if (info.getDisplayName().equals("testSpec()")) {
      return;
    }

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

  @ParameterizedTest
  @MethodSource("schemaAndDataProvider")
  void testNestedWrite(final JsonNode schema, final AirbyteMessage message) throws Exception {
    catalog = new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(new ConfiguredAirbyteStream()
        .withStream(new AirbyteStream().withName(USERS_STREAM_NAME).withNamespace(datasetId).withJsonSchema(schema))
        .withSyncMode(SyncMode.FULL_REFRESH).withDestinationSyncMode(DestinationSyncMode.OVERWRITE)));

    final BigQueryDestination destination = new BigQueryDenormalizedDestination();
    final AirbyteMessageConsumer consumer = destination.getConsumer(config, catalog, Destination::defaultOutputRecordCollector);

    consumer.accept(message);
    consumer.close();

    final List<JsonNode> usersActual = retrieveRecordsAsJson(USERS_STREAM_NAME);
    final JsonNode expectedUsersJson = message.getRecord().getData();
    assertEquals(usersActual.size(), 1);
    final JsonNode resultJson = usersActual.get(0);
    assertEquals(extractJsonValues(resultJson, "name"), extractJsonValues(expectedUsersJson, "name"));
    assertEquals(extractJsonValues(resultJson, "grants"), extractJsonValues(expectedUsersJson, "grants"));
    assertEquals(extractJsonValues(resultJson, "domain"), extractJsonValues(expectedUsersJson, "domain"));
  }

  @Test
  void testNestedDataTimeInsideNullObject() throws Exception {
    catalog = new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(new ConfiguredAirbyteStream()
        .withStream(
            new AirbyteStream().withName(USERS_STREAM_NAME).withNamespace(datasetId).withJsonSchema(getSchemaWithNestedDatetimeInsideNullObject()))
        .withSyncMode(SyncMode.FULL_REFRESH).withDestinationSyncMode(DestinationSyncMode.OVERWRITE)));

    final BigQueryDestination destination = new BigQueryDenormalizedDestination();
    final AirbyteMessageConsumer consumer = destination.getConsumer(config, catalog, Destination::defaultOutputRecordCollector);

    consumer.accept(MESSAGE_USERS7);
    consumer.close();

    final List<JsonNode> usersActual = retrieveRecordsAsJson(USERS_STREAM_NAME);
    final JsonNode expectedUsersJson = MESSAGE_USERS7.getRecord().getData();
    assertEquals(usersActual.size(), 1);
    final JsonNode resultJson = usersActual.get(0);
    assertEquals(extractJsonValues(resultJson, "name"), extractJsonValues(expectedUsersJson, "name"));
    assertEquals(extractJsonValues(resultJson, "appointment"), extractJsonValues(expectedUsersJson, "appointment"));
  }

  @Test
  void testWriteWithFormat() throws Exception {
    catalog = new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(new ConfiguredAirbyteStream()
        .withStream(new AirbyteStream().withName(USERS_STREAM_NAME).withNamespace(datasetId).withJsonSchema(getSchemaWithFormats()))
        .withSyncMode(SyncMode.FULL_REFRESH).withDestinationSyncMode(DestinationSyncMode.OVERWRITE)));

    final BigQueryDestination destination = new BigQueryDenormalizedDestination();
    final AirbyteMessageConsumer consumer = destination.getConsumer(config, catalog, Destination::defaultOutputRecordCollector);

    consumer.accept(MESSAGE_USERS3);
    consumer.close();

    final List<JsonNode> usersActual = retrieveRecordsAsJson(USERS_STREAM_NAME);
    final JsonNode expectedUsersJson = MESSAGE_USERS3.getRecord().getData();
    assertEquals(usersActual.size(), 1);
    final JsonNode resultJson = usersActual.get(0);
    assertEquals(extractJsonValues(resultJson, "name"), extractJsonValues(expectedUsersJson, "name"));
    assertEquals(extractJsonValues(resultJson, "date_of_birth"), extractJsonValues(expectedUsersJson, "date_of_birth"));

    // Bigquery's datetime type accepts multiple input format but always outputs the same, so we can't
    // expect to receive the value we sent.
    assertEquals(Set.of("2021-10-11T06:36:53"), extractJsonValues(resultJson, "updated_at"));

    final Schema expectedSchema = Schema.of(
        Field.of("name", StandardSQLTypeName.STRING),
        Field.of("date_of_birth", StandardSQLTypeName.DATE),
        Field.of("updated_at", StandardSQLTypeName.DATETIME),
        Field.of(JavaBaseConstants.COLUMN_NAME_AB_ID, StandardSQLTypeName.STRING),
        Field.of(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, StandardSQLTypeName.TIMESTAMP));

    assertEquals(BigQueryUtils.getTableDefinition(bigquery, dataset.getDatasetId().getDataset(), USERS_STREAM_NAME).getSchema(), expectedSchema);
  }

  @Test
  void testAnyOf() throws Exception {
    catalog = new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(new ConfiguredAirbyteStream()
        .withStream(new AirbyteStream().withName(USERS_STREAM_NAME).withNamespace(datasetId).withJsonSchema(getAnyOfSchema()))
        .withSyncMode(SyncMode.FULL_REFRESH).withDestinationSyncMode(DestinationSyncMode.OVERWRITE)));

    final BigQueryDenormalizedDestination destination = new BigQueryDenormalizedDestination();
    final AirbyteMessageConsumer consumer = destination.getConsumer(config, catalog, Destination::defaultOutputRecordCollector);

    consumer.accept(MESSAGE_USERS8);
    consumer.close();

    final List<JsonNode> usersActual = retrieveRecordsAsJson(USERS_STREAM_NAME);
    final JsonNode expectedUsersJson = MESSAGE_USERS8.getRecord().getData();
    assertEquals(usersActual.size(), 1);
    final JsonNode resultJson = usersActual.get(0);
    assertEquals(extractJsonValues(resultJson, "id"), extractJsonValues(expectedUsersJson, "id"));
    assertEquals(extractJsonValues(resultJson, "name"), extractJsonValues(expectedUsersJson, "name"));
    assertEquals(extractJsonValues(resultJson, "type"), extractJsonValues(expectedUsersJson, "type"));
    assertEquals(extractJsonValues(resultJson, "email"), extractJsonValues(expectedUsersJson, "email"));
    assertEquals(extractJsonValues(resultJson, "avatar"), extractJsonValues(expectedUsersJson, "avatar"));
    assertEquals(extractJsonValues(resultJson, "team_ids"), extractJsonValues(expectedUsersJson, "team_ids"));
    assertEquals(extractJsonValues(resultJson, "admin_ids"), extractJsonValues(expectedUsersJson, "admin_ids"));
    assertEquals(extractJsonValues(resultJson, "all_of_field"), extractJsonValues(expectedUsersJson, "all_of_field"));
    assertEquals(extractJsonValues(resultJson, "job_title"), extractJsonValues(expectedUsersJson, "job_title"));
    assertEquals(extractJsonValues(resultJson, "has_inbox_seat"), extractJsonValues(expectedUsersJson, "has_inbox_seat"));
    assertEquals(extractJsonValues(resultJson, "away_mode_enabled"), extractJsonValues(expectedUsersJson, "away_mode_enabled"));
    assertEquals(extractJsonValues(resultJson, "away_mode_reassign"), extractJsonValues(expectedUsersJson, "away_mode_reassign"));
  }

  @Test
  void testAnyOfWithNull() throws Exception {
    catalog = new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(new ConfiguredAirbyteStream()
        .withStream(new AirbyteStream().withName(USERS_STREAM_NAME).withNamespace(datasetId).withJsonSchema(getAnyOfSchema()))
        .withSyncMode(SyncMode.FULL_REFRESH).withDestinationSyncMode(DestinationSyncMode.OVERWRITE)));

    final BigQueryDenormalizedDestination destination = new BigQueryDenormalizedDestination();
    final AirbyteMessageConsumer consumer = destination.getConsumer(config, catalog, Destination::defaultOutputRecordCollector);

    consumer.accept(MESSAGE_USERS9);
    consumer.close();

    final List<JsonNode> usersActual = retrieveRecordsAsJson(USERS_STREAM_NAME);
    final JsonNode expectedUsersJson = MESSAGE_USERS9.getRecord().getData();
    assertEquals(usersActual.size(), 1);
    final JsonNode resultJson = usersActual.get(0);
    assertEquals(extractJsonValues(resultJson, "name"), extractJsonValues(expectedUsersJson, "name"));
    assertEquals(extractJsonValues(resultJson, "team_ids"), extractJsonValues(expectedUsersJson, "team_ids"));
    assertEquals(extractJsonValues(resultJson, "all_of_field"), extractJsonValues(expectedUsersJson, "all_of_field"));
    assertEquals(extractJsonValues(resultJson, "avatar"), extractJsonValues(expectedUsersJson, "avatar"));
  }

  @Test
  void testAnyOfWithEmptyList() throws Exception {
    catalog = new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(new ConfiguredAirbyteStream()
        .withStream(new AirbyteStream().withName(USERS_STREAM_NAME).withNamespace(datasetId).withJsonSchema(getAnyOfSchema()))
        .withSyncMode(SyncMode.FULL_REFRESH).withDestinationSyncMode(DestinationSyncMode.OVERWRITE)));

    final BigQueryDenormalizedDestination destination = new BigQueryDenormalizedDestination();
    final AirbyteMessageConsumer consumer = destination.getConsumer(config, catalog, Destination::defaultOutputRecordCollector);

    consumer.accept(MESSAGE_USERS10);
    consumer.close();

    final List<JsonNode> usersActual = retrieveRecordsAsJson(USERS_STREAM_NAME);
    final JsonNode expectedUsersJson = MESSAGE_USERS10.getRecord().getData();
    assertEquals(usersActual.size(), 1);
    final JsonNode resultJson = usersActual.get(0);
    assertEquals(extractJsonValues(resultJson, "name"), extractJsonValues(expectedUsersJson, "name"));
    assertEquals(extractJsonValues(resultJson, "team_ids"), extractJsonValues(expectedUsersJson, "team_ids"));
    assertEquals(extractJsonValues(resultJson, "all_of_field"), extractJsonValues(expectedUsersJson, "all_of_field"));
  }

  @Test
  void testIfJSONDateTimeWasConvertedToBigQueryFormat() throws Exception {
    catalog = new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(new ConfiguredAirbyteStream()
        .withStream(new AirbyteStream().withName(USERS_STREAM_NAME).withNamespace(datasetId).withJsonSchema(getSchemaWithDateTime()))
        .withSyncMode(SyncMode.FULL_REFRESH).withDestinationSyncMode(DestinationSyncMode.OVERWRITE)));

    final BigQueryDestination destination = new BigQueryDenormalizedDestination();
    final AirbyteMessageConsumer consumer = destination.getConsumer(config, catalog, Destination::defaultOutputRecordCollector);

    consumer.accept(MESSAGE_USERS4);
    consumer.close();

    final List<JsonNode> usersActual = retrieveRecordsAsJson(USERS_STREAM_NAME);
    assertEquals(usersActual.size(), 1);
    final JsonNode resultJson = usersActual.get(0);

    // BigQuery Accepts "YYYY-MM-DD HH:MM:SS[.SSSSSS]" format
    // returns "yyyy-MM-dd'T'HH:mm:ss" format
    assertEquals(Set.of(new DateTime("2021-10-11T06:36:53+00:00").toString("yyyy-MM-dd'T'HH:mm:ss")), extractJsonValues(resultJson, "updated_at"));
    // check nested datetime
    assertEquals(Set.of(new DateTime("2021-11-11T06:36:53+00:00").toString("yyyy-MM-dd'T'HH:mm:ss")),
        extractJsonValues(resultJson.get("items"), "nested_datetime"));
  }

  @Test
  void testJsonReferenceDefinition() throws Exception {
    catalog = new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(new ConfiguredAirbyteStream()
        .withStream(new AirbyteStream().withName(USERS_STREAM_NAME).withNamespace(datasetId).withJsonSchema(getSchemaWithReferenceDefinition()))
        .withSyncMode(SyncMode.FULL_REFRESH).withDestinationSyncMode(DestinationSyncMode.OVERWRITE)));

    final BigQueryDestination destination = new BigQueryDenormalizedDestination();
    final AirbyteMessageConsumer consumer = destination.getConsumer(config, catalog, Destination::defaultOutputRecordCollector);

    consumer.accept(MESSAGE_USERS5);
    consumer.accept(MESSAGE_USERS6);
    consumer.accept(EMPTY_MESSAGE);
    consumer.close();

    final Set<String> actual =
        retrieveRecordsAsJson(USERS_STREAM_NAME).stream().flatMap(x -> extractJsonValues(x, "users").stream()).collect(Collectors.toSet());

    final Set<String> expected = Sets.set(
        "{\"name\":\"John\",\"surname\":\"Adams\"}",
        null // we expect one record to have not had the users field set
    );

    assertEquals(2, actual.size());
    assertEquals(expected, actual);
  }

  private Set<String> extractJsonValues(final JsonNode node, final String attributeName) {
    final List<JsonNode> valuesNode = node.findValues(attributeName);
    final Set<String> resultSet = new HashSet<>();
    valuesNode.forEach(jsonNode -> {
      if (jsonNode.isArray()) {
        jsonNode.forEach(arrayNodeValue -> resultSet.add(arrayNodeValue.textValue()));
      } else if (jsonNode.isObject()) {
        resultSet.addAll(extractJsonValues(jsonNode, "big_query_array"));
      } else {
        resultSet.add(jsonNode.textValue());
      }
    });

    return resultSet;
  }

  private JsonNode removeAirbyteMetadataFields(final JsonNode record) {
    for (final String airbyteMetadataField : AIRBYTE_METADATA_FIELDS) {
      ((ObjectNode) record).remove(airbyteMetadataField);
    }
    return record;
  }

  private List<JsonNode> retrieveRecordsAsJson(final String tableName) throws Exception {
    final QueryJobConfiguration queryConfig =
        QueryJobConfiguration
            .newBuilder(
                String.format("select TO_JSON_STRING(t) as jsonValue from %s.%s t;", dataset.getDatasetId().getDataset(), tableName.toLowerCase()))
            .setUseLegacySql(false).build();
    BigQueryUtils.executeQuery(bigquery, queryConfig);

    return StreamSupport
        .stream(BigQueryUtils.executeQuery(bigquery, queryConfig).getLeft().getQueryResults().iterateAll().spliterator(), false)
        .map(v -> v.get("jsonValue").getStringValue())
        .map(Jsons::deserialize)
        .map(this::removeAirbyteMetadataFields)
        .collect(Collectors.toList());
  }

  private static Stream<Arguments> schemaAndDataProvider() {
    return Stream.of(
        arguments(getSchema(), MESSAGE_USERS1),
        arguments(getSchemaWithInvalidArrayType(), MESSAGE_USERS1),
        arguments(getSchema(), MESSAGE_USERS2));
  }

  private static AirbyteMessage createRecordMessage(final String stream, final JsonNode data) {
    return new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(stream)
            .withData(data)
            .withEmittedAt(NOW.toEpochMilli()));
  }

}
