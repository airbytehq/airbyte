/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.avro;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.MoreIterators;
import java.util.Collections;
import java.util.stream.Stream;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.ArgumentsProvider;
import org.junit.jupiter.params.provider.ArgumentsSource;

class JsonToAvroSchemaConverterTest {

  @Test
  public void testGetSingleTypes() {
    JsonNode input1 = Jsons.deserialize("{ \"type\": \"number\" }");
    assertEquals(
        Collections.singletonList(JsonSchemaType.NUMBER),
        JsonToAvroSchemaConverter.getTypes("field", input1));
  }

  @Test
  public void testGetUnionTypes() {
    JsonNode input2 = Jsons.deserialize("{ \"type\": [\"null\", \"string\"] }");
    assertEquals(
        Lists.newArrayList(JsonSchemaType.NULL, JsonSchemaType.STRING),
        JsonToAvroSchemaConverter.getTypes("field", input2));
  }

  @Test
  public void testNoCombinedRestriction() {
    JsonNode input1 = Jsons.deserialize("{ \"type\": \"number\" }");
    assertTrue(JsonToAvroSchemaConverter.getCombinedRestriction(input1).isEmpty());
  }

  @Test
  public void testWithCombinedRestriction() {
    JsonNode input2 = Jsons.deserialize("{ \"anyOf\": [{ \"type\": \"string\" }, { \"type\": \"integer\" }] }");
    assertTrue(JsonToAvroSchemaConverter.getCombinedRestriction(input2).isPresent());
  }

  public static class GetFieldTypeTestCaseProvider implements ArgumentsProvider {

    @Override
    public Stream<? extends Arguments> provideArguments(ExtensionContext context) throws Exception {
      JsonNode testCases = Jsons.deserialize(MoreResources.readResource("parquet/json_schema_converter/get_field_type.json"));
      return MoreIterators.toList(testCases.elements()).stream().map(testCase -> Arguments.of(
          testCase.get("fieldName").asText(),
          testCase.get("jsonFieldSchema"),
          testCase.get("avroFieldType")));
    }

  }

  @ParameterizedTest
  @ArgumentsSource(GetFieldTypeTestCaseProvider.class)
  public void testGetFieldType(String fieldName, JsonNode jsonFieldSchema, JsonNode avroFieldType) {
    JsonToAvroSchemaConverter converter = new JsonToAvroSchemaConverter();
    assertEquals(
        avroFieldType,
        Jsons.deserialize(converter.getNullableFieldTypes(fieldName, jsonFieldSchema).toString()),
        String.format("Test for %s failed", fieldName));
  }

  public static class GetAvroSchemaTestCaseProvider implements ArgumentsProvider {

    @Override
    public Stream<? extends Arguments> provideArguments(ExtensionContext context) throws Exception {
      JsonNode testCases = Jsons.deserialize(MoreResources.readResource("parquet/json_schema_converter/get_avro_schema.json"));
      return MoreIterators.toList(testCases.elements()).stream().map(testCase -> Arguments.of(
          testCase.get("schemaName").asText(),
          testCase.get("namespace").asText(),
          testCase.get("appendAirbyteFields").asBoolean(),
          testCase.get("jsonSchema"),
          testCase.get("avroSchema")));
    }

  }

  @ParameterizedTest
  @ArgumentsSource(GetAvroSchemaTestCaseProvider.class)
  public void testGetAvroSchema(String schemaName, String namespace, boolean appendAirbyteFields, JsonNode jsonSchema, JsonNode avroSchema) {
    JsonToAvroSchemaConverter converter = new JsonToAvroSchemaConverter();
    assertEquals(
        avroSchema,
        Jsons.deserialize(converter.getAvroSchema(jsonSchema, schemaName, namespace, appendAirbyteFields).toString()),
        String.format("Test for %s failed", schemaName));
  }

}
