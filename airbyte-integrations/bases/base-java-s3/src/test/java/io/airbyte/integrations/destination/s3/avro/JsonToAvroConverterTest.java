/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.avro;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectWriter;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.MoreIterators;
import java.util.Collections;
import java.util.stream.Stream;
import org.apache.avro.Schema;
import org.apache.avro.generic.GenericData;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.ArgumentsProvider;
import org.junit.jupiter.params.provider.ArgumentsSource;

class JsonToAvroConverterTest {

  private static final ObjectWriter WRITER = MoreMappers.initMapper().writer();
  private static final JsonToAvroSchemaConverter SCHEMA_CONVERTER = new JsonToAvroSchemaConverter();

  @Test
  public void testGetSingleTypes() {
    final JsonNode input1 = Jsons.deserialize("""
                                              {"$ref": "WellKnownTypes.json#/definitions/Number"}"
                                              """);

    assertEquals(
        Collections.singletonList(JsonSchemaType.NUMBER_V1),
        JsonToAvroSchemaConverter.getTypes("field", input1));
  }

  @Test
  public void testNoCombinedRestriction() {
    final JsonNode input1 = Jsons.deserialize("""
                                              {"$ref": "WellKnownTypes.json#/definitions/String"}"
                                              """);
    assertTrue(JsonToAvroSchemaConverter.getCombinedRestriction(input1).isEmpty());
  }

  @Test
  public void testWithCombinedRestriction() {
    final JsonNode input2 = Jsons.deserialize("{ \"anyOf\": [{ \"type\": \"string\" }, { \"type\": \"integer\" }] }");
    assertTrue(JsonToAvroSchemaConverter.getCombinedRestriction(input2).isPresent());
  }

  @Deprecated
  public static class GetFieldTypeTestCaseProviderV0 implements ArgumentsProvider {

    @Override
    public Stream<? extends Arguments> provideArguments(final ExtensionContext context) throws Exception {
      final JsonNode testCases =
          Jsons.deserialize(MoreResources.readResource("parquet/json_schema_converter/type_conversion_test_cases_v0.json"));
      return MoreIterators.toList(testCases.elements()).stream().map(testCase -> Arguments.of(
          testCase.get("fieldName").asText(),
          testCase.get("jsonFieldSchema"),
          testCase.get("avroFieldType")));
    }

  }

  public static class GetFieldTypeTestCaseProviderV1 implements ArgumentsProvider {

    @Override
    public Stream<? extends Arguments> provideArguments(final ExtensionContext context) throws Exception {
      final JsonNode testCases =
          Jsons.deserialize(MoreResources.readResource("parquet/json_schema_converter/type_conversion_test_cases_v1.json"));
      return MoreIterators.toList(testCases.elements()).stream().map(testCase -> Arguments.of(
          testCase.get("fieldName").asText(),
          testCase.get("jsonFieldSchema"),
          testCase.get("avroFieldType")));
    }

  }

  @ParameterizedTest
  @ArgumentsSource(GetFieldTypeTestCaseProviderV0.class)
  public void testFieldTypeConversionV0(final String fieldName, final JsonNode jsonFieldSchema, final JsonNode avroFieldType) {
    assertEquals(
        avroFieldType,
        Jsons.deserialize(SCHEMA_CONVERTER.parseJsonField(fieldName, null, jsonFieldSchema, true, true).toString()),
        String.format("Test for %s failed", fieldName));
  }

  @ParameterizedTest
  @ArgumentsSource(GetFieldTypeTestCaseProviderV1.class)
  public void testFieldTypeConversionV1(final String fieldName, final JsonNode jsonFieldSchema, final JsonNode avroFieldType) {
    assertEquals(
        avroFieldType,
        Jsons.deserialize(SCHEMA_CONVERTER.parseJsonField(fieldName, null, jsonFieldSchema, true, true).toString()),
        String.format("Test for %s failed", fieldName));
  }

  @Deprecated
  public static class GetAvroSchemaTestCaseProviderV0 implements ArgumentsProvider {

    @Override
    public Stream<? extends Arguments> provideArguments(final ExtensionContext context) throws Exception {
      final JsonNode testCases = Jsons.deserialize(MoreResources.readResource("parquet/json_schema_converter/json_conversion_test_cases_v0.json"));
      return MoreIterators.toList(testCases.elements()).stream().map(testCase -> Arguments.of(
          testCase.get("schemaName").asText(),
          testCase.get("namespace").asText(),
          testCase.get("appendAirbyteFields").asBoolean(),
          testCase.get("jsonSchema"),
          testCase.get("jsonObject"),
          testCase.get("avroSchema"),
          testCase.get("avroObject")));
    }

  }

  public static class GetAvroSchemaTestCaseProviderV1 implements ArgumentsProvider {

    @Override
    public Stream<? extends Arguments> provideArguments(final ExtensionContext context) throws Exception {
      final JsonNode testCases = Jsons.deserialize(MoreResources.readResource("parquet/json_schema_converter/json_conversion_test_cases_v1.json"));
      return MoreIterators.toList(testCases.elements()).stream().map(testCase -> Arguments.of(
          testCase.get("schemaName").asText(),
          testCase.get("namespace").asText(),
          testCase.get("appendAirbyteFields").asBoolean(),
          testCase.get("jsonSchema"),
          testCase.get("jsonObject"),
          testCase.get("avroSchema"),
          testCase.get("avroObject")));
    }

  }

  /**
   * This test verifies both the schema and object conversion.
   */
  @ParameterizedTest
  @ArgumentsSource(GetAvroSchemaTestCaseProviderV0.class)
  public void testJsonAvroConversionV0(final String schemaName,
                                       final String namespace,
                                       final boolean appendAirbyteFields,
                                       final JsonNode jsonSchema,
                                       final JsonNode jsonObject,
                                       final JsonNode avroSchema,
                                       final JsonNode avroObject)
      throws Exception {
    final Schema actualAvroSchema = SCHEMA_CONVERTER.getAvroSchema(jsonSchema, schemaName, namespace, appendAirbyteFields, true, true, true);
    assertEquals(
        avroSchema,
        Jsons.deserialize(actualAvroSchema.toString()),
        String.format("Schema conversion for %s failed", schemaName));

    final Schema.Parser schemaParser = new Schema.Parser();
    final GenericData.Record actualAvroObject = AvroConstants.JSON_CONVERTER.convertToGenericDataRecord(
        WRITER.writeValueAsBytes(jsonObject),
        schemaParser.parse(Jsons.serialize(avroSchema)));
    assertEquals(
        avroObject,
        Jsons.deserialize(actualAvroObject.toString()),
        String.format("Object conversion for %s failed", schemaName));
  }

  @ParameterizedTest
  @ArgumentsSource(GetAvroSchemaTestCaseProviderV1.class)
  public void testJsonAvroConversionV1(final String schemaName,
                                       final String namespace,
                                       final boolean appendAirbyteFields,
                                       final JsonNode jsonSchema,
                                       final JsonNode jsonObject,
                                       final JsonNode avroSchema,
                                       final JsonNode avroObject)
      throws Exception {
    final Schema actualAvroSchema = SCHEMA_CONVERTER.getAvroSchema(jsonSchema, schemaName, namespace, appendAirbyteFields, true, true, true);
    assertEquals(
        avroSchema,
        Jsons.deserialize(actualAvroSchema.toString()),
        String.format("Schema conversion for %s failed", schemaName));

    final Schema.Parser schemaParser = new Schema.Parser();
    final GenericData.Record actualAvroObject = AvroConstants.JSON_CONVERTER.convertToGenericDataRecord(
        WRITER.writeValueAsBytes(jsonObject),
        schemaParser.parse(Jsons.serialize(avroSchema)));
    assertEquals(
        avroObject,
        Jsons.deserialize(actualAvroObject.toString()),
        String.format("Object conversion for %s failed", schemaName));
  }

}
