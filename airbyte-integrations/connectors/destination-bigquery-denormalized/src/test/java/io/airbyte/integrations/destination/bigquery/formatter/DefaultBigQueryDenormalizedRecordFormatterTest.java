/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter;

import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestSchemaUtils.getExpectedSchema;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestSchemaUtils.getExpectedSchemaArrays;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestSchemaUtils.getExpectedSchemaWithDateTime;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestSchemaUtils.getExpectedSchemaWithFormats;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestSchemaUtils.getExpectedSchemaWithInvalidArrayType;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestSchemaUtils.getExpectedSchemaWithNestedDatetimeInsideNullObject;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestSchemaUtils.getSchema;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestSchemaUtils.getSchemaArrays;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestSchemaUtils.getSchemaWithBigInteger;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestSchemaUtils.getSchemaWithDateTime;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestSchemaUtils.getSchemaWithFormats;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestSchemaUtils.getSchemaWithInvalidArrayType;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestSchemaUtils.getSchemaWithNestedDatetimeInsideNullObject;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestSchemaUtils.getSchemaWithReferenceDefinition;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.params.provider.Arguments.arguments;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.JsonNodeType;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.Field.Mode;
import com.google.cloud.bigquery.LegacySQLTypeName;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.StandardSQLTypeName;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.bigquery.BigQuerySQLNameTransformer;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.util.stream.Stream;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.mockito.Mockito;

class DefaultBigQueryDenormalizedRecordFormatterTest {

  private final ObjectMapper mapper = new ObjectMapper();

  private static Stream<Arguments> actualAndExpectedSchemasProvider() {
    return Stream.of(
        arguments(getSchema(), getExpectedSchema()),
        arguments(getSchemaWithFormats(), getExpectedSchemaWithFormats()),
        arguments(getSchemaWithDateTime(), getExpectedSchemaWithDateTime()),
        arguments(getSchemaWithInvalidArrayType(), getExpectedSchemaWithInvalidArrayType()),
        arguments(getSchemaWithNestedDatetimeInsideNullObject(),
            getExpectedSchemaWithNestedDatetimeInsideNullObject()),
        arguments(getSchemaArrays(), getExpectedSchemaArrays()));
  }

  @ParameterizedTest
  @MethodSource("actualAndExpectedSchemasProvider")
  void testDefaultSchema(final JsonNode schemaToProcess, final JsonNode expectedSchema) {
    DefaultBigQueryDenormalizedRecordFormatter rf = new DefaultBigQueryDenormalizedRecordFormatter(
        schemaToProcess, new BigQuerySQLNameTransformer());

    assertEquals(expectedSchema, rf.formatJsonSchema(schemaToProcess));
  }

  @Test
  void testSchema() {
    final JsonNode jsonNodeSchema = getSchema();
    DefaultBigQueryDenormalizedRecordFormatter rf = new DefaultBigQueryDenormalizedRecordFormatter(
        jsonNodeSchema, new BigQuerySQLNameTransformer());
    final Field subFields = Field.newBuilder("big_query_array", LegacySQLTypeName.RECORD,
        Field.of("domain", LegacySQLTypeName.STRING),
        Field.of("grants", LegacySQLTypeName.RECORD,
            Field.newBuilder("big_query_array", StandardSQLTypeName.STRING).setMode(Mode.REPEATED).build()))
        .setMode(Mode.REPEATED).build();
    final Schema expectedResult = Schema.of(
        Field.newBuilder("accepts_marketing_updated_at", LegacySQLTypeName.DATETIME).setMode(Mode.NULLABLE).build(),
        Field.of("name", LegacySQLTypeName.STRING),
        Field.of("permission_list", LegacySQLTypeName.RECORD, subFields),
        Field.of("_airbyte_ab_id", LegacySQLTypeName.STRING),
        Field.of("_airbyte_emitted_at", LegacySQLTypeName.TIMESTAMP));

    final Schema result = rf.getBigQuerySchema(jsonNodeSchema);

    assertEquals(expectedResult, result);
  }

  @Test
  void testSchemaWithFormats() {
    final JsonNode jsonNodeSchema = getSchemaWithFormats();
    DefaultBigQueryDenormalizedRecordFormatter rf = new DefaultBigQueryDenormalizedRecordFormatter(
        jsonNodeSchema, new BigQuerySQLNameTransformer());
    final Schema expectedResult = Schema.of(
        Field.of("name", LegacySQLTypeName.STRING),
        Field.of("date_of_birth", LegacySQLTypeName.DATE),
        Field.of("updated_at", LegacySQLTypeName.DATETIME),
        Field.of("_airbyte_ab_id", LegacySQLTypeName.STRING),
        Field.of("_airbyte_emitted_at", LegacySQLTypeName.TIMESTAMP));

    final Schema result = rf.getBigQuerySchema(jsonNodeSchema);

    assertEquals(expectedResult, result);
  }

  @Test
  void testSchemaWithBigInteger() {
    final JsonNode jsonNodeSchema = getSchemaWithBigInteger();
    DefaultBigQueryDenormalizedRecordFormatter rf = new DefaultBigQueryDenormalizedRecordFormatter(
        jsonNodeSchema, new BigQuerySQLNameTransformer());
    final Schema expectedResult = Schema.of(
        Field.of("salary", LegacySQLTypeName.INTEGER),
        Field.of("updated_at", LegacySQLTypeName.DATETIME),
        Field.of("_airbyte_ab_id", LegacySQLTypeName.STRING),
        Field.of("_airbyte_emitted_at", LegacySQLTypeName.TIMESTAMP));

    final Schema result = rf.getBigQuerySchema(jsonNodeSchema);

    assertEquals(expectedResult, result);
  }

  @Test
  void testSchemaWithDateTime() {
    final JsonNode jsonNodeSchema = getSchemaWithDateTime();
    DefaultBigQueryDenormalizedRecordFormatter rf = new DefaultBigQueryDenormalizedRecordFormatter(
        jsonNodeSchema, new BigQuerySQLNameTransformer());
    final Schema expectedResult = Schema.of(
        Field.of("updated_at", LegacySQLTypeName.DATETIME),
        Field.of("items", LegacySQLTypeName.RECORD, Field.of("nested_datetime", LegacySQLTypeName.DATETIME)),
        Field.of("_airbyte_ab_id", LegacySQLTypeName.STRING),
        Field.of("_airbyte_emitted_at", LegacySQLTypeName.TIMESTAMP));

    final Schema result = rf.getBigQuerySchema(jsonNodeSchema);

    assertEquals(expectedResult, result);
  }

  @Test
  void testSchemaWithInvalidArrayType() {
    final JsonNode jsonNodeSchema = getSchemaWithInvalidArrayType();
    DefaultBigQueryDenormalizedRecordFormatter rf = new DefaultBigQueryDenormalizedRecordFormatter(
        jsonNodeSchema, new BigQuerySQLNameTransformer());
    final Schema expectedResult = Schema.of(
        Field.of("name", LegacySQLTypeName.STRING),
        Field.newBuilder("permission_list", LegacySQLTypeName.RECORD,
            Field.of("domain", LegacySQLTypeName.STRING),
            Field.newBuilder("grants", LegacySQLTypeName.STRING).setMode(Mode.REPEATED).build())
            .setMode(Mode.REPEATED).build(),
        Field.of("_airbyte_ab_id", LegacySQLTypeName.STRING),
        Field.of("_airbyte_emitted_at", LegacySQLTypeName.TIMESTAMP));

    final Schema result = rf.getBigQuerySchema(jsonNodeSchema);

    assertEquals(expectedResult, result);
  }

  @Test
  void testSchemaWithReferenceDefinition() {
    final JsonNode jsonNodeSchema = getSchemaWithReferenceDefinition();
    DefaultBigQueryDenormalizedRecordFormatter rf = new DefaultBigQueryDenormalizedRecordFormatter(
        jsonNodeSchema, new BigQuerySQLNameTransformer());
    final Schema expectedResult = Schema.of(
        Field.of("users", LegacySQLTypeName.STRING),
        Field.of("_airbyte_ab_id", LegacySQLTypeName.STRING),
        Field.of("_airbyte_emitted_at", LegacySQLTypeName.TIMESTAMP));

    final Schema result = rf.getBigQuerySchema(jsonNodeSchema);

    assertEquals(expectedResult, result);
  }

  @Test
  void testSchemaWithNestedDatetimeInsideNullObject() {
    final JsonNode jsonNodeSchema = getSchemaWithNestedDatetimeInsideNullObject();
    DefaultBigQueryDenormalizedRecordFormatter rf = new DefaultBigQueryDenormalizedRecordFormatter(
        jsonNodeSchema, new BigQuerySQLNameTransformer());
    final Schema expectedResult = Schema.of(
        Field.newBuilder("name", LegacySQLTypeName.STRING).setMode(Mode.NULLABLE).build(),
        Field.newBuilder("appointment", LegacySQLTypeName.RECORD,
            Field.newBuilder("street", LegacySQLTypeName.STRING).setMode(Mode.NULLABLE).build(),
            Field.newBuilder("expTime", LegacySQLTypeName.DATETIME).setMode(Mode.NULLABLE).build())
            .setMode(Mode.NULLABLE).build(),
        Field.of("_airbyte_ab_id", LegacySQLTypeName.STRING),
        Field.of("_airbyte_emitted_at", LegacySQLTypeName.TIMESTAMP));

    final Schema result = rf.getBigQuerySchema(jsonNodeSchema);

    assertEquals(expectedResult, result);
  }

  @Test
  public void testEmittedAtTimeConversion() {
    final DefaultBigQueryDenormalizedRecordFormatter mockedFormatter = Mockito.mock(
        DefaultBigQueryDenormalizedRecordFormatter.class, Mockito.CALLS_REAL_METHODS);

    final ObjectNode objectNode = mapper.createObjectNode();

    final AirbyteRecordMessage airbyteRecordMessage = new AirbyteRecordMessage();
    airbyteRecordMessage.setEmittedAt(1602637589000L);
    mockedFormatter.addAirbyteColumns(objectNode, airbyteRecordMessage);

    assertEquals("2020-10-14 01:06:29.000000+00:00",
        objectNode.get(JavaBaseConstants.COLUMN_NAME_EMITTED_AT).textValue());
  }

  @Test
  void formatRecord_objectType() throws JsonProcessingException {
    final JsonNode jsonNodeSchema = getSchema();
    final DefaultBigQueryDenormalizedRecordFormatter rf = new DefaultBigQueryDenormalizedRecordFormatter(
        jsonNodeSchema, new BigQuerySQLNameTransformer());
    final JsonNode objectNode = mapper.readTree("""
                                                {"name":"data"}
                                                """);
    final AirbyteRecordMessage airbyteRecordMessage = new AirbyteRecordMessage();
    airbyteRecordMessage.setEmittedAt(1602637589000L);
    airbyteRecordMessage.setData(objectNode);

    final JsonNode result = rf.formatRecord(airbyteRecordMessage);

    assertNotNull(result);
    assertTrue(result.has("name"));
    assertEquals("data", result.get("name").textValue());
    assertEquals(JsonNodeType.STRING, result.get("name").getNodeType());
  }

  @Test
  void formatRecord_containsRefDefinition() throws JsonProcessingException {
    final JsonNode jsonNodeSchema = getSchema();
    DefaultBigQueryDenormalizedRecordFormatter rf = new DefaultBigQueryDenormalizedRecordFormatter(
        jsonNodeSchema, new BigQuerySQLNameTransformer());
    rf.fieldsContainRefDefinitionValue.add("name");
    final JsonNode objectNode = mapper.readTree("""
                                                {"name":"data"}
                                                """);
    final AirbyteRecordMessage airbyteRecordMessage = new AirbyteRecordMessage();
    airbyteRecordMessage.setEmittedAt(1602637589000L);
    airbyteRecordMessage.setData(objectNode);

    final JsonNode result = rf.formatRecord(airbyteRecordMessage);

    assertNotNull(result);
    assertTrue(result.has("name"));
    assertEquals("\"data\"", result.get("name").textValue());
    assertEquals(JsonNodeType.STRING, result.get("name").getNodeType());
  }

  @Test
  void formatRecord_objectWithArray() throws JsonProcessingException {
    final JsonNode jsonNodeSchema = getSchemaArrays();
    DefaultBigQueryDenormalizedRecordFormatter rf = new DefaultBigQueryDenormalizedRecordFormatter(
        jsonNodeSchema, new BigQuerySQLNameTransformer());
    final JsonNode objectNode = mapper.readTree("""
                                                {"object_with_arrays":["array_3"]}
                                                """);
    final AirbyteRecordMessage airbyteRecordMessage = new AirbyteRecordMessage();
    airbyteRecordMessage.setEmittedAt(1602637589000L);
    airbyteRecordMessage.setData(objectNode);

    final JsonNode result = rf.formatRecord(airbyteRecordMessage);

    assertNotNull(result);
    assertTrue(result.has("object_with_arrays"));
    result.has("object_with_arrays");
    assertEquals(JsonNodeType.ARRAY, result.get("object_with_arrays").getNodeType());
    assertNotNull(result.get("object_with_arrays").get(0));
    assertEquals(JsonNodeType.STRING, result.get("object_with_arrays").get(0).getNodeType());
  }

  @Test
  void formatRecordNotObject_thenThrowsError() throws JsonProcessingException {
    final JsonNode jsonNodeSchema = getSchema();
    DefaultBigQueryDenormalizedRecordFormatter rf = new DefaultBigQueryDenormalizedRecordFormatter(
        jsonNodeSchema, new BigQuerySQLNameTransformer());
    final JsonNode arrayNode = mapper.readTree("""
                                               ["one"]""");

    final AirbyteRecordMessage airbyteRecordMessage = new AirbyteRecordMessage();
    airbyteRecordMessage.setEmittedAt(1602637589000L);
    airbyteRecordMessage.setData(arrayNode);

    assertThrows(IllegalArgumentException.class, () -> rf.formatRecord(airbyteRecordMessage));
  }

}
