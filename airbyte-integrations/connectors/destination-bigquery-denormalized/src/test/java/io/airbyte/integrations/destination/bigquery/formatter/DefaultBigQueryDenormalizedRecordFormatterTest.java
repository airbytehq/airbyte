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

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.JsonNodeType;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.Field.Mode;
import com.google.cloud.bigquery.FieldList;
import com.google.cloud.bigquery.LegacySQLTypeName;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.StandardSQLTypeName;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.bigquery.BigQuerySQLNameTransformer;
import io.airbyte.protocol.models.AirbyteRecordMessage;
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

    final Schema bigQuerySchema = rf.getBigQuerySchema(jsonNodeSchema);

    final FieldList fields = bigQuerySchema.getFields();

    assertEquals(5, fields.size());
    // test field _airbyte_ab_id
    assertEquals(LegacySQLTypeName.STRING, fields.get("_airbyte_ab_id").getType());
    // test field _airbyte_emitted_at
    assertEquals(LegacySQLTypeName.TIMESTAMP, fields.get("_airbyte_emitted_at").getType());

    // test field accepts_marketing_updated_at
    assertEquals(LegacySQLTypeName.DATETIME, fields.get("accepts_marketing_updated_at").getType());
    // test field name
    assertEquals(LegacySQLTypeName.STRING, fields.get("name").getType());

    // test field permission_list
    final Field permission_list = fields.get("permission_list");
    assertEquals(LegacySQLTypeName.RECORD, permission_list.getType());
    final Field bigQueryArray = permission_list.getSubFields().get("big_query_array");

    assertEquals(LegacySQLTypeName.RECORD, bigQueryArray.getType());
    assertEquals(Mode.REPEATED, bigQueryArray.getMode());

    final FieldList subFieldsBigQueryArray = bigQueryArray.getSubFields();
    assertEquals(LegacySQLTypeName.STRING, subFieldsBigQueryArray.get("domain").getType());

    final Field grants = subFieldsBigQueryArray.get("grants");
    assertEquals(LegacySQLTypeName.RECORD, grants.getType());
    assertEquals(1, grants.getSubFields().size());
    assertEquals(LegacySQLTypeName.STRING, grants.getSubFields().get("big_query_array").getType());
    assertEquals(Mode.REPEATED, grants.getSubFields().get("big_query_array").getMode());
  }

  @Test
  void testSchemaWithFormats() {
    final JsonNode jsonNodeSchema = getSchemaWithFormats();
    DefaultBigQueryDenormalizedRecordFormatter rf = new DefaultBigQueryDenormalizedRecordFormatter(
        jsonNodeSchema, new BigQuerySQLNameTransformer());

    final Schema bigQuerySchema = rf.getBigQuerySchema(jsonNodeSchema);

    final FieldList fields = bigQuerySchema.getFields();

    assertEquals(5, fields.size());
    // test field _airbyte_ab_id
    assertEquals(LegacySQLTypeName.STRING, fields.get("_airbyte_ab_id").getType());
    // test field _airbyte_emitted_at
    assertEquals(LegacySQLTypeName.TIMESTAMP, fields.get("_airbyte_emitted_at").getType());

    // test field updated_at
    assertEquals(LegacySQLTypeName.DATETIME, fields.get("updated_at").getType());
    // test field name
    assertEquals(LegacySQLTypeName.STRING, fields.get("name").getType());
    // test field date_of_birth
    assertEquals(LegacySQLTypeName.DATE, fields.get("date_of_birth").getType());
  }

  @Test
  void testSchemaWithBigInteger() {
    final JsonNode jsonNodeSchema = getSchemaWithBigInteger();
    DefaultBigQueryDenormalizedRecordFormatter rf = new DefaultBigQueryDenormalizedRecordFormatter(
        jsonNodeSchema, new BigQuerySQLNameTransformer());

    final Schema bigQuerySchema = rf.getBigQuerySchema(jsonNodeSchema);

    final FieldList fields = bigQuerySchema.getFields();

    assertEquals(4, fields.size());
    // test field _airbyte_ab_id
    assertEquals(LegacySQLTypeName.STRING, fields.get("_airbyte_ab_id").getType());
    // test field _airbyte_emitted_at
    assertEquals(LegacySQLTypeName.TIMESTAMP, fields.get("_airbyte_emitted_at").getType());

    // test field updated_at
    assertEquals(LegacySQLTypeName.DATETIME, fields.get("updated_at").getType());
    // test field salary
    assertEquals(StandardSQLTypeName.INT64, fields.get("salary").getType().getStandardType());
  }

  @Test
  void testSchemaWithDateTime() {
    final JsonNode jsonNodeSchema = getSchemaWithDateTime();
    DefaultBigQueryDenormalizedRecordFormatter rf = new DefaultBigQueryDenormalizedRecordFormatter(
        jsonNodeSchema, new BigQuerySQLNameTransformer());

    final Schema bigQuerySchema = rf.getBigQuerySchema(jsonNodeSchema);

    final FieldList fields = bigQuerySchema.getFields();

    assertEquals(4, fields.size());
    // test field _airbyte_ab_id
    assertEquals(LegacySQLTypeName.STRING, fields.get("_airbyte_ab_id").getType());
    // test field _airbyte_emitted_at
    assertEquals(LegacySQLTypeName.TIMESTAMP, fields.get("_airbyte_emitted_at").getType());

    // test field updated_at
    assertEquals(LegacySQLTypeName.DATETIME, fields.get("updated_at").getType());

    // test field items
    final Field items = fields.get("items");
    assertEquals(1, items.getSubFields().size());
    assertEquals(LegacySQLTypeName.RECORD, items.getType());
    assertEquals(LegacySQLTypeName.DATETIME,
        items.getSubFields().get("nested_datetime").getType());
  }

  @Test
  void testSchemaWithInvalidArrayType() {
    final JsonNode jsonNodeSchema = getSchemaWithInvalidArrayType();
    DefaultBigQueryDenormalizedRecordFormatter rf = new DefaultBigQueryDenormalizedRecordFormatter(
        jsonNodeSchema, new BigQuerySQLNameTransformer());

    final Schema bigQuerySchema = rf.getBigQuerySchema(jsonNodeSchema);

    final FieldList fields = bigQuerySchema.getFields();

    assertEquals(4, fields.size());
    // test field _airbyte_ab_id
    assertEquals(LegacySQLTypeName.STRING, fields.get("_airbyte_ab_id").getType());
    // test field _airbyte_emitted_at
    assertEquals(LegacySQLTypeName.TIMESTAMP, fields.get("_airbyte_emitted_at").getType());

    // test field name
    assertEquals(LegacySQLTypeName.STRING, fields.get("name").getType());

    // test field permission_list
    final Field permissionList = fields.get("permission_list");
    assertEquals(2, permissionList.getSubFields().size());
    assertEquals(LegacySQLTypeName.RECORD, permissionList.getType());
    assertEquals(Mode.REPEATED, permissionList.getMode());
    assertEquals(LegacySQLTypeName.STRING, permissionList.getSubFields().get("domain").getType());

    assertEquals(LegacySQLTypeName.STRING, permissionList.getSubFields().get("grants").getType());
    assertEquals(Mode.REPEATED, permissionList.getSubFields().get("grants").getMode());
  }

  @Test
  void testSchemaWithReferenceDefinition() {
    final JsonNode jsonNodeSchema = getSchemaWithReferenceDefinition();
    DefaultBigQueryDenormalizedRecordFormatter rf = new DefaultBigQueryDenormalizedRecordFormatter(
        jsonNodeSchema, new BigQuerySQLNameTransformer());

    final Schema bigQuerySchema = rf.getBigQuerySchema(jsonNodeSchema);

    final FieldList fields = bigQuerySchema.getFields();

    assertEquals(3, fields.size());
    // test field _airbyte_ab_id
    assertEquals(LegacySQLTypeName.STRING, fields.get("_airbyte_ab_id").getType());
    // test field _airbyte_emitted_at
    assertEquals(LegacySQLTypeName.TIMESTAMP, fields.get("_airbyte_emitted_at").getType());

    // test field users
    assertEquals(LegacySQLTypeName.STRING, fields.get("users").getType());
  }

  @Test
  void testSchemaWithNestedDatetimeInsideNullObject() {
    final JsonNode jsonNodeSchema = getSchemaWithNestedDatetimeInsideNullObject();
    DefaultBigQueryDenormalizedRecordFormatter rf = new DefaultBigQueryDenormalizedRecordFormatter(
        jsonNodeSchema, new BigQuerySQLNameTransformer());

    final Schema bigQuerySchema = rf.getBigQuerySchema(jsonNodeSchema);

    final FieldList fields = bigQuerySchema.getFields();

    assertEquals(4, fields.size());
    // test field _airbyte_ab_id
    assertEquals(LegacySQLTypeName.STRING, fields.get("_airbyte_ab_id").getType());
    // test field _airbyte_emitted_at
    assertEquals(LegacySQLTypeName.TIMESTAMP, fields.get("_airbyte_emitted_at").getType());

    // test field name
    assertEquals(LegacySQLTypeName.STRING, fields.get("name").getType());

    // test field appointment
    final Field appointment = fields.get("appointment");
    assertEquals(2, appointment.getSubFields().size());
    assertEquals(LegacySQLTypeName.RECORD, appointment.getType());
    assertEquals(Mode.NULLABLE, appointment.getMode());

    assertEquals(LegacySQLTypeName.STRING, appointment.getSubFields().get("street").getType());
    assertEquals(Mode.NULLABLE, appointment.getSubFields().get("street").getMode());

    assertEquals(LegacySQLTypeName.DATETIME, appointment.getSubFields().get("expTime").getType());
    assertEquals(Mode.NULLABLE, appointment.getSubFields().get("expTime").getMode());

  }

  @Test
  public void testEmittedAtTimeConversion() {
    final DefaultBigQueryDenormalizedRecordFormatter mockedFormatter = Mockito.mock(
        DefaultBigQueryDenormalizedRecordFormatter.class, Mockito.CALLS_REAL_METHODS);

    final ObjectMapper mapper = new ObjectMapper();
    final ObjectNode objectNode = mapper.createObjectNode();

    final AirbyteRecordMessage airbyteRecordMessage = new AirbyteRecordMessage();
    airbyteRecordMessage.setEmittedAt(1602637589000L);
    mockedFormatter.addAirbyteColumns(objectNode, airbyteRecordMessage);

    assertEquals("2020-10-14 01:06:29.000000+00:00",
        objectNode.get(JavaBaseConstants.COLUMN_NAME_EMITTED_AT).textValue());
  }

  @Test
  void formatJsonSchema() {}

  @Test
  void formatRecord_objectType() {
    final JsonNode jsonNodeSchema = getSchema();
    DefaultBigQueryDenormalizedRecordFormatter rf = new DefaultBigQueryDenormalizedRecordFormatter(
        jsonNodeSchema, new BigQuerySQLNameTransformer());
    final ObjectNode objectNode = mapper.createObjectNode().put("name", "data");
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
  void formatRecord_containsRefDefinition() {
    final JsonNode jsonNodeSchema = getSchema();
    DefaultBigQueryDenormalizedRecordFormatter rf = new DefaultBigQueryDenormalizedRecordFormatter(
        jsonNodeSchema, new BigQuerySQLNameTransformer());
    rf.fieldsContainRefDefinitionValue.add("name");
    final ObjectNode objectNode = mapper.createObjectNode().put("name", "data");
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
  void formatRecord_objectWithArray() {
    final JsonNode jsonNodeSchema = getSchemaArrays();
    DefaultBigQueryDenormalizedRecordFormatter rf = new DefaultBigQueryDenormalizedRecordFormatter(
        jsonNodeSchema, new BigQuerySQLNameTransformer());
    final ArrayNode arrayNode = mapper.createArrayNode().add("array_3");
    final ObjectNode objectNode = mapper.createObjectNode().set("object_with_arrays", arrayNode);
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
  void formatRecordNotObject_thenThrowsError() {
    final JsonNode jsonNodeSchema = getSchema();
    DefaultBigQueryDenormalizedRecordFormatter rf = new DefaultBigQueryDenormalizedRecordFormatter(
        jsonNodeSchema, new BigQuerySQLNameTransformer());
    final ObjectMapper mapper = new ObjectMapper();
    final ArrayNode arrayNode = mapper.createArrayNode().add("one");

    final AirbyteRecordMessage airbyteRecordMessage = new AirbyteRecordMessage();
    airbyteRecordMessage.setEmittedAt(1602637589000L);
    airbyteRecordMessage.setData(arrayNode);

    assertThrows(IllegalArgumentException.class, () -> rf.formatRecord(airbyteRecordMessage));
  }

  // @Test
  // void formatRecord_objectType2() {
  // final JsonNode jsonNodeSchema = getSchemaWithAllOf();
  // DefaultBigQueryDenormalizedRecordFormatter rf = new DefaultBigQueryDenormalizedRecordFormatter(
  // jsonNodeSchema, new BigQuerySQLNameTransformer());
  // final ObjectNode objectNode = mapper.createObjectNode().put("title", "test");
  // final AirbyteRecordMessage airbyteRecordMessage = new AirbyteRecordMessage();
  // airbyteRecordMessage.setEmittedAt(1602637589000L);
  // airbyteRecordMessage.setData(objectNode);
  //
  // final JsonNode result = rf.formatRecord(airbyteRecordMessage);
  //
  // assertNotNull(result);
  // assertTrue(result.has("name"));
  // assertEquals("data", result.get("name").textValue());
  // assertEquals(JsonNodeType.STRING, result.get("name").getNodeType());
  // }

  @Test
  void addAirbyteColumns() {}

  @Test
  void formatDateTimeFields() {

  }

  @Test
  void getBigQuerySchema() {}

}
