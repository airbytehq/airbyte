/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static io.airbyte.integrations.destination.bigquery.BigQueryDenormalizedTestConstants.AIRBYTE_COLUMNS;
import static io.airbyte.integrations.destination.bigquery.BigQueryDenormalizedTestConstants.BIGQUERY_DATETIME_FORMAT;
import static io.airbyte.integrations.destination.bigquery.BigQueryDenormalizedTestConstants.USERS_STREAM_NAME;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.configureBigQuery;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.createCommonConfig;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getAnyOfFormats;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getAnyOfFormatsWithEmptyList;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getAnyOfFormatsWithNull;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getAnyOfSchema;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getBigQueryDataSet;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getCommonCatalog;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getData;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getDataArrays;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getDataMaxNestedDepth;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getDataTooDeepNestedDepth;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getDataWithEmptyObjectAndArray;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getDataWithFormats;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getDataWithJSONDateTimeFormats;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getDataWithJSONWithReference;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getDataWithNestedDatetimeInsideNullObject;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getExpectedDataArrays;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getSchema;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getSchemaArrays;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getSchemaMaxNestedDepth;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getSchemaTooDeepNestedDepth;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getSchemaWithDateTime;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getSchemaWithFormats;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getSchemaWithInvalidArrayType;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getSchemaWithNestedDatetimeInsideNullObject;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getSchemaWithReferenceDefinition;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.runDestinationWrite;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.tearDownBigQuery;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.params.provider.Arguments.arguments;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.StandardSQLTypeName;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.io.IOException;
import java.time.Instant;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;
import org.assertj.core.util.Sets;
import org.joda.time.DateTime;
import org.joda.time.DateTimeZone;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInfo;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class BigQueryDenormalizedDestinationTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDenormalizedDestinationTest.class);
  protected static final Instant NOW = Instant.now();
  protected static final AirbyteMessage MESSAGE_USERS1 = createRecordMessage(USERS_STREAM_NAME, getData());
  protected static final AirbyteMessage MESSAGE_USERS2 = createRecordMessage(USERS_STREAM_NAME, getDataWithEmptyObjectAndArray());
  protected static final AirbyteMessage MESSAGE_USERS3 = createRecordMessage(USERS_STREAM_NAME, getDataWithFormats());
  protected static final AirbyteMessage MESSAGE_USERS4 = createRecordMessage(USERS_STREAM_NAME, getDataWithJSONDateTimeFormats());
  protected static final AirbyteMessage MESSAGE_USERS5 = createRecordMessage(USERS_STREAM_NAME, getDataWithJSONWithReference());
  protected static final AirbyteMessage MESSAGE_USERS6 = createRecordMessage(USERS_STREAM_NAME, Jsons.deserialize("{\"users\":null}"));
  protected static final AirbyteMessage MESSAGE_USERS7 = createRecordMessage(USERS_STREAM_NAME, getDataWithNestedDatetimeInsideNullObject());
  protected static final AirbyteMessage MESSAGE_USERS8 = createRecordMessage(USERS_STREAM_NAME, getAnyOfFormats());
  protected static final AirbyteMessage MESSAGE_USERS9 = createRecordMessage(USERS_STREAM_NAME, getAnyOfFormatsWithNull());
  protected static final AirbyteMessage MESSAGE_USERS10 = createRecordMessage(USERS_STREAM_NAME, getAnyOfFormatsWithEmptyList());
  protected static final AirbyteMessage MESSAGE_USERS11 = createRecordMessage(USERS_STREAM_NAME, getDataArrays());
  protected static final AirbyteMessage MESSAGE_USERS12 = createRecordMessage(USERS_STREAM_NAME, getDataTooDeepNestedDepth());
  protected static final AirbyteMessage MESSAGE_USERS13 = createRecordMessage(USERS_STREAM_NAME, getDataMaxNestedDepth());
  protected static final AirbyteMessage EMPTY_MESSAGE = createRecordMessage(USERS_STREAM_NAME, Jsons.deserialize("{}"));

  protected JsonNode config;
  protected BigQuery bigquery;
  protected Dataset dataset;
  protected String datasetId;

  protected JsonNode createConfig() throws IOException {
    return createCommonConfig();
  }

  @BeforeEach
  void setup(final TestInfo info) throws IOException {
    if (info.getDisplayName().equals("testSpec()")) {
      return;
    }

    config = createConfig();
    bigquery = configureBigQuery(config);
    dataset = getBigQueryDataSet(config, bigquery);
    datasetId = dataset.getDatasetId().getDataset();

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
    MESSAGE_USERS11.getRecord().setNamespace(datasetId);
    MESSAGE_USERS12.getRecord().setNamespace(datasetId);
    MESSAGE_USERS13.getRecord().setNamespace(datasetId);
    EMPTY_MESSAGE.getRecord().setNamespace(datasetId);

  }

  @AfterEach
  void tearDown(final TestInfo info) {
    if (info.getDisplayName().equals("testSpec()")) {
      return;
    }

    tearDownBigQuery(dataset, bigquery);
  }

  @ParameterizedTest
  @MethodSource("schemaAndDataProvider")
  void testNestedWrite(final JsonNode schema, final AirbyteMessage message) throws Exception {
    runDestinationWrite(getCommonCatalog(schema, datasetId), config, message);

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
    runDestinationWrite(getCommonCatalog(getSchemaWithNestedDatetimeInsideNullObject(), datasetId), config, MESSAGE_USERS7);

    final List<JsonNode> usersActual = retrieveRecordsAsJson(USERS_STREAM_NAME);
    final JsonNode expectedUsersJson = MESSAGE_USERS7.getRecord().getData();
    assertEquals(usersActual.size(), 1);
    final JsonNode resultJson = usersActual.get(0);
    assertEquals(extractJsonValues(resultJson, "name"), extractJsonValues(expectedUsersJson, "name"));
    assertEquals(extractJsonValues(resultJson, "appointment"), extractJsonValues(expectedUsersJson, "appointment"));
  }

  protected Schema getExpectedSchemaForWriteWithFormatTest() {
    return Schema.of(
        Field.of("name", StandardSQLTypeName.STRING),
        Field.of("date_of_birth", StandardSQLTypeName.DATE),
        Field.of("updated_at", StandardSQLTypeName.DATETIME),
        Field.of(JavaBaseConstants.COLUMN_NAME_AB_ID, StandardSQLTypeName.STRING),
        Field.of(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, StandardSQLTypeName.TIMESTAMP));
  }

  @Test
  void testWriteWithFormat() throws Exception {
    runDestinationWrite(getCommonCatalog(getSchemaWithFormats(), datasetId), config, MESSAGE_USERS3);

    final List<JsonNode> usersActual = retrieveRecordsAsJson(USERS_STREAM_NAME);
    final JsonNode expectedUsersJson = MESSAGE_USERS3.getRecord().getData();
    assertEquals(usersActual.size(), 1);
    final JsonNode resultJson = usersActual.get(0);
    assertEquals(extractJsonValues(resultJson, "name"), extractJsonValues(expectedUsersJson, "name"));
    assertEquals(extractJsonValues(resultJson, "date_of_birth"), extractJsonValues(expectedUsersJson, "date_of_birth"));

    // Bigquery's datetime type accepts multiple input format but always outputs the same, so we can't
    // expect to receive the value we sent.
    var expectedValue = LocalDate.parse(extractJsonValues(expectedUsersJson, "updated_at").stream().findFirst().get(),
        DateTimeFormatter.ofPattern(BIGQUERY_DATETIME_FORMAT));
    var actualValue =
        LocalDate.parse(extractJsonValues(resultJson, "updated_at").stream().findFirst().get(),
            DateTimeFormatter.ofPattern(BIGQUERY_DATETIME_FORMAT));
    assertEquals(expectedValue, actualValue);

    assertEquals(BigQueryUtils.getTableDefinition(bigquery, datasetId, USERS_STREAM_NAME).getSchema(), getExpectedSchemaForWriteWithFormatTest());
  }

  @Test
  @Disabled // Issue #5912 is reopened
  void testAnyOf() throws Exception {
    runDestinationWrite(getCommonCatalog(getAnyOfSchema(), datasetId), config, MESSAGE_USERS8);

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
  @Disabled // Issue #5912 is reopened
  void testAnyOfWithNull() throws Exception {
    runDestinationWrite(getCommonCatalog(getAnyOfSchema(), datasetId), config, MESSAGE_USERS9);

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
  @Disabled // Issue #5912 is reopened
  void testAnyOfWithEmptyList() throws Exception {
    runDestinationWrite(getCommonCatalog(getAnyOfSchema(), datasetId), config, MESSAGE_USERS10);

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
    runDestinationWrite(getCommonCatalog(getSchemaWithDateTime(), datasetId), config, MESSAGE_USERS4);

    final List<JsonNode> usersActual = retrieveRecordsAsJson(USERS_STREAM_NAME);
    assertEquals(usersActual.size(), 1);
    final JsonNode resultJson = usersActual.get(0);

    // BigQuery Accepts "YYYY-MM-DD HH:MM:SS[.SSSSSS]" format
    Set<String> actualValues = extractJsonValues(resultJson, "updated_at");
    assertEquals(Set.of(new DateTime("2021-10-11T06:36:53+00:00").withZone(DateTimeZone.UTC).toString(BIGQUERY_DATETIME_FORMAT)),
        actualValues);

    // check nested datetime
    actualValues = extractJsonValues(resultJson.get("items"), "nested_datetime");
    assertEquals(Set.of(new DateTime("2021-11-11T06:36:53+00:00").withZone(DateTimeZone.UTC).toString(BIGQUERY_DATETIME_FORMAT)),
        actualValues);
  }

  @Test
  void testJsonReferenceDefinition() throws Exception {
    runDestinationWrite(getCommonCatalog(getSchemaWithReferenceDefinition(), datasetId), config, MESSAGE_USERS5, MESSAGE_USERS6, EMPTY_MESSAGE);

    final Set<String> actual =
        retrieveRecordsAsJson(USERS_STREAM_NAME).stream().flatMap(x -> extractJsonValues(x, "users").stream()).collect(Collectors.toSet());

    final Set<String> expected = Sets.set(
        "\"{\\\"name\\\":\\\"John\\\",\\\"surname\\\":\\\"Adams\\\"}\"",
        null // we expect one record to have not had the users field set
    );

    assertEquals(2, actual.size());
    assertEquals(expected, actual);
  }

  @Test
  void testArrays() throws Exception {
    runDestinationWrite(getCommonCatalog(getSchemaArrays(), datasetId), config, MESSAGE_USERS11);

    assertEquals(getExpectedDataArrays(), retrieveRecordsAsJson(USERS_STREAM_NAME).get(0));
  }

  // Issue #14668
  @Test
  void testTooDeepNestedDepth() {
    try {
      runDestinationWrite(getCommonCatalog(getSchemaTooDeepNestedDepth(), datasetId), config, MESSAGE_USERS12);
    } catch (Exception e) {
      assert (e.getCause().getMessage().contains("nested too deeply"));
    }
  }

  // Issue #14668
  @Test
  void testMaxNestedDepth() throws Exception {
    runDestinationWrite(getCommonCatalog(getSchemaMaxNestedDepth(), datasetId), config, MESSAGE_USERS13);

    assertEquals(getDataMaxNestedDepth().findValue("str_value").asText(),
        retrieveRecordsAsJson(USERS_STREAM_NAME).get(0).findValue("str_value").asText());
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
    for (final String airbyteMetadataField : AIRBYTE_COLUMNS) {
      ((ObjectNode) record).remove(airbyteMetadataField);
    }
    return record;
  }

  private List<JsonNode> retrieveRecordsAsJson(final String tableName) throws Exception {
    final QueryJobConfiguration queryConfig =
        QueryJobConfiguration
            .newBuilder(
                String.format("select TO_JSON_STRING(t) as jsonValue from %s.%s t;", datasetId, tableName.toLowerCase()))
            .setUseLegacySql(false).build();
    BigQueryUtils.executeQuery(bigquery, queryConfig);

    var valuesStream = StreamSupport
        .stream(BigQueryUtils.executeQuery(bigquery, queryConfig).getLeft().getQueryResults().iterateAll().spliterator(), false)
        .map(v -> v.get("jsonValue").getStringValue());
    return formatDateValues(valuesStream)
        .map(Jsons::deserialize)
        .map(this::removeAirbyteMetadataFields)
        .collect(Collectors.toList());
  }

  /**
   * BigQuery returns date values in a different format based on the column type. Datetime :
   * YYYY-MM-DD'T'HH:MM:SS Timestamp : YYYY-MM-DD'T'HH:MM:SS'Z'
   *
   * This method formats all values as Airbite format to simplify test result validation.
   */
  private Stream<String> formatDateValues(Stream<String> values) {
    return values.map(s -> s.replaceAll("(\"\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2})(Z)(\")", "$1$3"));
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
