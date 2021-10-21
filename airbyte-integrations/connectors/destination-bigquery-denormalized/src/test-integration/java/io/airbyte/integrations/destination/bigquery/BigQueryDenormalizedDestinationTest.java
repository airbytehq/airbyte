/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.params.provider.Arguments.arguments;

import com.fasterxml.jackson.databind.JsonNode;
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
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;
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

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDenormalizedDestinationTest.class);

  private static final String BIG_QUERY_CLIENT_CHUNK_SIZE = "big_query_client_buffer_size_mb";
  private static final Instant NOW = Instant.now();
  private static final String USERS_STREAM_NAME = "users";
  private static final AirbyteMessage MESSAGE_USERS1 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
      .withRecord(new AirbyteRecordMessage().withStream(USERS_STREAM_NAME)
          .withData(getData())
          .withEmittedAt(NOW.toEpochMilli()));
  private static final AirbyteMessage MESSAGE_USERS2 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
      .withRecord(new AirbyteRecordMessage().withStream(USERS_STREAM_NAME)
          .withData(getDataWithEmptyObjectAndArray())
          .withEmittedAt(NOW.toEpochMilli()));
  private static final AirbyteMessage MESSAGE_USERS3 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
      .withRecord(new AirbyteRecordMessage().withStream(USERS_STREAM_NAME)
          .withData(getDataWithFormats())
          .withEmittedAt(NOW.toEpochMilli()));

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
          "Must provide path to a big query credentials file. By default {module-root}/config/credentials.json. Override by setting setting path with the CREDENTIALS_PATH constant.");
    }
    final String credentialsJsonString = new String(Files.readAllBytes(CREDENTIALS_PATH));
    final JsonNode credentialsJson = Jsons.deserialize(credentialsJsonString);

    final String projectId = credentialsJson.get(BigQueryConsts.CONFIG_PROJECT_ID).asText();
    final ServiceAccountCredentials credentials = ServiceAccountCredentials.fromStream(new ByteArrayInputStream(credentialsJsonString.getBytes()));
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

    final DatasetInfo datasetInfo = DatasetInfo.newBuilder(datasetId).setLocation(datasetLocation).build();
    dataset = bigquery.create(datasetInfo);

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(BigQueryConsts.CONFIG_PROJECT_ID, projectId)
        .put(BigQueryConsts.CONFIG_CREDS, credentialsJsonString)
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
    assertEquals(extractJsonValues(resultJson, "updated_at"), Set.of("2018-08-19T12:11:35.220"));

    final Schema expectedSchema = Schema.of(
        Field.of("name", StandardSQLTypeName.STRING),
        Field.of("date_of_birth", StandardSQLTypeName.DATE),
        Field.of("updated_at", StandardSQLTypeName.DATETIME),
        Field.of(JavaBaseConstants.COLUMN_NAME_AB_ID, StandardSQLTypeName.STRING),
        Field.of(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, StandardSQLTypeName.TIMESTAMP));

    assertEquals(BigQueryUtils.getTableDefinition(bigquery, dataset.getDatasetId().getDataset(), USERS_STREAM_NAME).getSchema(), expectedSchema);
  }

  private Set<String> extractJsonValues(final JsonNode node, final String attributeName) {
    final List<JsonNode> valuesNode = node.findValues(attributeName);
    final Set<String> resultSet = new HashSet<>();
    valuesNode.forEach(jsonNode -> {
      if (jsonNode.isArray()) {
        jsonNode.forEach(arrayNodeValue -> resultSet.add(arrayNodeValue.textValue()));
      } else if (jsonNode.isObject()) {
        resultSet.addAll(extractJsonValues(jsonNode, "value"));
      } else {
        resultSet.add(jsonNode.textValue());
      }
    });

    return resultSet;
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
        .collect(Collectors.toList());
  }

  private static Stream<Arguments> schemaAndDataProvider() {
    return Stream.of(
        arguments(getSchema(), MESSAGE_USERS1),
        arguments(getSchemaWithInvalidArrayType(), MESSAGE_USERS1),
        arguments(getSchema(), MESSAGE_USERS2));
  }

  private static JsonNode getSchema() {
    return Jsons.deserialize(
        "{\n"
            + "  \"type\": [\n"
            + "    \"object\"\n"
            + "  ],\n"
            + "  \"properties\": {\n"
            + "    \"name\": {\n"
            + "      \"type\": [\n"
            + "        \"string\"\n"
            + "      ]\n"
            + "    },\n"
            + "    \"permissions\": {\n"
            + "      \"type\": [\n"
            + "        \"array\"\n"
            + "      ],\n"
            + "      \"items\": {\n"
            + "        \"type\": [\n"
            + "          \"object\"\n"
            + "        ],\n"
            + "        \"properties\": {\n"
            + "          \"domain\": {\n"
            + "            \"type\": [\n"
            + "              \"string\"\n"
            + "            ]\n"
            + "          },\n"
            + "          \"grants\": {\n"
            + "            \"type\": [\n"
            + "              \"array\"\n"
            + "            ],\n"
            + "            \"items\": {\n"
            + "              \"type\": [\n"
            + "                \"string\"\n"
            + "              ]\n"
            + "            }\n"
            + "          }\n"
            + "        }\n"
            + "      }\n"
            + "    }\n"
            + "  }\n"
            + "}");

  }

  private static JsonNode getSchemaWithFormats() {
    return Jsons.deserialize(
        "{\n"
            + "  \"type\": [\n"
            + "    \"object\"\n"
            + "  ],\n"
            + "  \"properties\": {\n"
            + "    \"name\": {\n"
            + "      \"type\": [\n"
            + "        \"string\"\n"
            + "      ]\n"
            + "    },\n"
            + "    \"date_of_birth\": {\n"
            + "      \"type\": [\n"
            + "        \"string\"\n"
            + "      ],\n"
            + "      \"format\": \"date\"\n"
            + "    },\n"
            + "    \"updated_at\": {\n"
            + "      \"type\": [\n"
            + "        \"string\"\n"
            + "      ],\n"
            + "      \"format\": \"date-time\"\n"
            + "    }\n"
            + "  }\n"
            + "}");
  }

  private static JsonNode getSchemaWithInvalidArrayType() {
    return Jsons.deserialize(
        "{\n"
            + "  \"type\": [\n"
            + "    \"object\"\n"
            + "  ],\n"
            + "  \"properties\": {\n"
            + "    \"name\": {\n"
            + "      \"type\": [\n"
            + "        \"string\"\n"
            + "      ]\n"
            + "    },\n"
            + "    \"permissions\": {\n"
            + "      \"type\": [\n"
            + "        \"array\"\n"
            + "      ],\n"
            + "      \"items\": {\n"
            + "        \"type\": [\n"
            + "          \"object\"\n"
            + "        ],\n"
            + "        \"properties\": {\n"
            + "          \"domain\": {\n"
            + "            \"type\": [\n"
            + "              \"string\"\n"
            + "            ]\n"
            + "          },\n"
            + "          \"grants\": {\n"
            + "            \"type\": [\n"
            + "              \"array\"\n" // missed "items" element
            + "            ]\n"
            + "          }\n"
            + "        }\n"
            + "      }\n"
            + "    }\n"
            + "  }\n"
            + "}");

  }

  private static JsonNode getData() {
    return Jsons.deserialize(
        "{\n"
            + "  \"name\": \"Andrii\",\n"
            + "  \"permissions\": [\n"
            + "    {\n"
            + "      \"domain\": \"abs\",\n"
            + "      \"grants\": [\n"
            + "        \"admin\"\n"
            + "      ]\n"
            + "    },\n"
            + "    {\n"
            + "      \"domain\": \"tools\",\n"
            + "      \"grants\": [\n"
            + "        \"read\", \"write\"\n"
            + "      ]\n"
            + "    }\n"
            + "  ]\n"
            + "}");
  }

  private static JsonNode getDataWithFormats() {
    return Jsons.deserialize(
        "{\n"
            + "  \"name\": \"Andrii\",\n"
            + "  \"date_of_birth\": \"1996-01-25\",\n"
            + "  \"updated_at\": \"2018-08-19 12:11:35.22\"\n"
            + "}");
  }

  private static JsonNode getDataWithEmptyObjectAndArray() {
    return Jsons.deserialize(
        "{\n"
            + "  \"name\": \"Andrii\",\n"
            + "  \"permissions\": [\n"
            + "    {\n"
            + "      \"domain\": \"abs\",\n"
            + "      \"items\": {},\n" // empty object
            + "      \"grants\": [\n"
            + "        \"admin\"\n"
            + "      ]\n"
            + "    },\n"
            + "    {\n"
            + "      \"domain\": \"tools\",\n"
            + "      \"grants\": [],\n" // empty array
            + "      \"items\": {\n" // object with empty array and object
            + "        \"object\": {},\n"
            + "        \"array\": []\n"
            + "      }\n"
            + "    }\n"
            + "  ]\n"
            + "}");

  }

}
