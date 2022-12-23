/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter;

import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestSchemaUtils.getExpectedSchemaWithReferenceDefinition;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestSchemaUtils.getSchemaWithDateTime;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestSchemaUtils.getSchemaWithReferenceDefinition;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.LegacySQLTypeName;
import com.google.cloud.bigquery.Schema;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.bigquery.BigQuerySQLNameTransformer;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

class GcsBigQueryDenormalizedRecordFormatterTest {

  @Test
  void refReplacement() {
    final JsonNode jsonNodeSchema = getSchemaWithReferenceDefinition();
    final JsonNode expectedResult = getExpectedSchemaWithReferenceDefinition();
    final GcsBigQueryDenormalizedRecordFormatter rf = new GcsBigQueryDenormalizedRecordFormatter(
        jsonNodeSchema, new BigQuerySQLNameTransformer());

    final JsonNode result = rf.formatJsonSchema(jsonNodeSchema);

    assertEquals(expectedResult, result);
  }

  @Test
  void dataTimeReplacement() {
    final JsonNode jsonNodeSchema = getSchemaWithDateTime();
    final GcsBigQueryDenormalizedRecordFormatter rf = new GcsBigQueryDenormalizedRecordFormatter(
        jsonNodeSchema, new BigQuerySQLNameTransformer());
    final Schema expectedResult = Schema.of(
        Field.of("updated_at", LegacySQLTypeName.TIMESTAMP),
        Field.of("items", LegacySQLTypeName.RECORD, Field.of("nested_datetime", LegacySQLTypeName.TIMESTAMP)),
        Field.of("_airbyte_ab_id", LegacySQLTypeName.STRING),
        Field.of("_airbyte_emitted_at", LegacySQLTypeName.TIMESTAMP));

    final Schema result = rf.getBigQuerySchema(jsonNodeSchema);

    assertEquals(expectedResult, result);
  }

  @Test
  public void testEmittedAtTimeConversion() {
    final GcsBigQueryDenormalizedRecordFormatter mockedFormatter = Mockito.mock(
        GcsBigQueryDenormalizedRecordFormatter.class, Mockito.CALLS_REAL_METHODS);

    final ObjectMapper mapper = new ObjectMapper();
    final ObjectNode objectNode = mapper.createObjectNode();

    final AirbyteRecordMessage airbyteRecordMessage = new AirbyteRecordMessage();
    airbyteRecordMessage.setEmittedAt(1602637589000L);
    mockedFormatter.addAirbyteColumns(objectNode, airbyteRecordMessage);

    assertEquals("1602637589000",
        objectNode.get(JavaBaseConstants.COLUMN_NAME_EMITTED_AT).asText());
  }

}
