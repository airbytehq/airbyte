/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestSchemaUtils.*;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.params.provider.Arguments.arguments;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.Field.Mode;
import com.google.cloud.bigquery.FieldList;
import com.google.cloud.bigquery.LegacySQLTypeName;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.StandardSQLTypeName;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.bigquery.formatter.GcsBigQueryDenormalizedRecordFormatter;
import io.airbyte.integrations.destination.bigquery.util.TestBigQueryDenormalizedRecordFormatter;
import io.airbyte.integrations.destination.bigquery.util.TestGcsBigQueryDenormalizedRecordFormatter;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.util.stream.Stream;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.mockito.Mockito;

public class BigQueryDenormalizedUtilsTest {

  @ParameterizedTest
  @MethodSource("actualAndExpectedSchemasProvider")
  void testGcsSchema(final JsonNode schemaToProcess, final JsonNode expectedSchema) {
    TestGcsBigQueryDenormalizedRecordFormatter rf = new TestGcsBigQueryDenormalizedRecordFormatter(
        schemaToProcess, new BigQuerySQLNameTransformer());

    assertEquals(expectedSchema, rf.formatJsonSchema(schemaToProcess));
  }

  @Test
  void testSchema() {
    final JsonNode jsonNodeSchema = getSchema();
    GcsBigQueryDenormalizedRecordFormatter rf = new GcsBigQueryDenormalizedRecordFormatter(
        jsonNodeSchema, new BigQuerySQLNameTransformer());

    final Schema bigQuerySchema = rf.getBigQuerySchema(jsonNodeSchema);

    final FieldList fields = bigQuerySchema.getFields();

    assertEquals(5, fields.size());
    // test field _airbyte_ab_id
    assertEquals(LegacySQLTypeName.STRING, fields.get("_airbyte_ab_id").getType());
    // test field _airbyte_emitted_at
    assertEquals(LegacySQLTypeName.TIMESTAMP, fields.get("_airbyte_emitted_at").getType());

    // test field accepts_marketing_updated_at
    assertEquals(LegacySQLTypeName.TIMESTAMP, fields.get("accepts_marketing_updated_at").getType());
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
    GcsBigQueryDenormalizedRecordFormatter rf = new GcsBigQueryDenormalizedRecordFormatter(
        jsonNodeSchema, new BigQuerySQLNameTransformer());

    final Schema bigQuerySchema = rf.getBigQuerySchema(jsonNodeSchema);

    final FieldList fields = bigQuerySchema.getFields();

    assertEquals(5, fields.size());
    // test field _airbyte_ab_id
    assertEquals(LegacySQLTypeName.STRING, fields.get("_airbyte_ab_id").getType());
    // test field _airbyte_emitted_at
    assertEquals(LegacySQLTypeName.TIMESTAMP, fields.get("_airbyte_emitted_at").getType());

    // test field updated_at
    assertEquals(LegacySQLTypeName.TIMESTAMP, fields.get("updated_at").getType());
    // test field name
    assertEquals(LegacySQLTypeName.STRING, fields.get("name").getType());
    // test field date_of_birth
    assertEquals(LegacySQLTypeName.DATE, fields.get("date_of_birth").getType());
  }

  @Test
  void testSchemaWithBigInteger() {
    final JsonNode jsonNodeSchema = getSchemaWithBigInteger();
    GcsBigQueryDenormalizedRecordFormatter rf = new GcsBigQueryDenormalizedRecordFormatter(
        jsonNodeSchema, new BigQuerySQLNameTransformer());

    final Schema bigQuerySchema = rf.getBigQuerySchema(jsonNodeSchema);

    final FieldList fields = bigQuerySchema.getFields();

    assertEquals(4, fields.size());
    // test field _airbyte_ab_id
    assertEquals(LegacySQLTypeName.STRING, fields.get("_airbyte_ab_id").getType());
    // test field _airbyte_emitted_at
    assertEquals(LegacySQLTypeName.TIMESTAMP, fields.get("_airbyte_emitted_at").getType());

    // test field updated_at
    assertEquals(LegacySQLTypeName.TIMESTAMP, fields.get("updated_at").getType());
    // test field salary
    assertEquals(StandardSQLTypeName.INT64, fields.get("salary").getType().getStandardType());
  }

  @Test
  void testSchemaWithDateTime() {
    final JsonNode jsonNodeSchema = getSchemaWithDateTime();
    GcsBigQueryDenormalizedRecordFormatter rf = new GcsBigQueryDenormalizedRecordFormatter(
        jsonNodeSchema, new BigQuerySQLNameTransformer());

    final Schema bigQuerySchema = rf.getBigQuerySchema(jsonNodeSchema);

    final FieldList fields = bigQuerySchema.getFields();

    assertEquals(4, fields.size());
    // test field _airbyte_ab_id
    assertEquals(LegacySQLTypeName.STRING, fields.get("_airbyte_ab_id").getType());
    // test field _airbyte_emitted_at
    assertEquals(LegacySQLTypeName.TIMESTAMP, fields.get("_airbyte_emitted_at").getType());

    // test field updated_at
    assertEquals(LegacySQLTypeName.TIMESTAMP, fields.get("updated_at").getType());

    // test field items
    final Field items = fields.get("items");
    assertEquals(1, items.getSubFields().size());
    assertEquals(LegacySQLTypeName.RECORD, items.getType());
    assertEquals(LegacySQLTypeName.TIMESTAMP,
        items.getSubFields().get("nested_datetime").getType());
  }

  @Test
  void testSchemaWithInvalidArrayType() {
    final JsonNode jsonNodeSchema = getSchemaWithInvalidArrayType();
    GcsBigQueryDenormalizedRecordFormatter rf = new GcsBigQueryDenormalizedRecordFormatter(
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
    GcsBigQueryDenormalizedRecordFormatter rf = new GcsBigQueryDenormalizedRecordFormatter(
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
    GcsBigQueryDenormalizedRecordFormatter rf = new GcsBigQueryDenormalizedRecordFormatter(
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

    assertEquals(LegacySQLTypeName.TIMESTAMP, appointment.getSubFields().get("expTime").getType());
    assertEquals(Mode.NULLABLE, appointment.getSubFields().get("expTime").getMode());

  }

  @Test
  public void testEmittedAtTimeConversion() {
    final TestBigQueryDenormalizedRecordFormatter mockedFormatter = Mockito.mock(
        TestBigQueryDenormalizedRecordFormatter.class, Mockito.CALLS_REAL_METHODS);

    final ObjectMapper mapper = new ObjectMapper();
    final ObjectNode objectNode = mapper.createObjectNode();

    final AirbyteRecordMessage airbyteRecordMessage = new AirbyteRecordMessage();
    airbyteRecordMessage.setEmittedAt(1602637589000L);
    mockedFormatter.addAirbyteColumns(objectNode, airbyteRecordMessage);

    assertEquals("2020-10-14 01:06:29.000000+00:00",
        objectNode.get(JavaBaseConstants.COLUMN_NAME_EMITTED_AT).textValue());
  }

  private static Stream<Arguments> actualAndExpectedSchemasProvider() {
    return Stream.of(
        arguments(getSchema(), getExpectedSchema()),
        arguments(getSchemaWithFormats(), getExpectedSchemaWithFormats()),
        arguments(getSchemaWithDateTime(), getExpectedSchemaWithDateTime()),
        arguments(getSchemaWithInvalidArrayType(), getExpectedSchemaWithInvalidArrayType()),
        arguments(getSchemaWithReferenceDefinition(), getExpectedSchemaWithReferenceDefinition()),
        arguments(getSchemaWithNestedDatetimeInsideNullObject(),
            getExpectedSchemaWithNestedDatetimeInsideNullObject()));
  }

}
