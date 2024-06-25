/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.avro

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectWriter
import io.airbyte.commons.jackson.MoreMappers
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.resources.MoreResources
import io.airbyte.commons.util.MoreIterators
import java.util.stream.Stream
import org.apache.avro.Schema
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtensionContext
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.ArgumentsProvider
import org.junit.jupiter.params.provider.ArgumentsSource

class JsonToAvroConverterTest {

    companion object {
        private val WRITER: ObjectWriter = MoreMappers.initMapper().writer()
        private val SCHEMA_CONVERTER = JsonToAvroSchemaConverter()
    }

    @Test
    internal fun testGetSingleTypes() {
        val input1 =
            Jsons.deserialize(
                """
                                              {"${'$'}ref": "WellKnownTypes.json#/definitions/Number"}"
                                              
                                              """.trimIndent(),
            )

        assertEquals(
            listOf(JsonSchemaType.NUMBER_V1),
            JsonToAvroSchemaConverter.getTypes("field", input1),
        )
    }

    @Test
    internal fun testNoCombinedRestriction() {
        val input1 =
            Jsons.deserialize(
                """
                                              {"${'$'}ref": "WellKnownTypes.json#/definitions/String"}"
                                              
                                              """.trimIndent(),
            )
        assertTrue(JsonToAvroSchemaConverter.getCombinedRestriction(input1).isEmpty)
    }

    @Test
    internal fun testWithCombinedRestriction() {
        val input2 =
            Jsons.deserialize(
                "{ \"anyOf\": [{ \"type\": \"string\" }, { \"type\": \"integer\" }] }"
            )
        assertTrue(JsonToAvroSchemaConverter.getCombinedRestriction(input2).isPresent)
    }

    @Deprecated("")
    internal class GetFieldTypeTestCaseProviderV0 : ArgumentsProvider {
        @Throws(Exception::class)
        override fun provideArguments(context: ExtensionContext): Stream<out Arguments> {
            val testCases =
                Jsons.deserialize(
                    MoreResources.readResource(
                        "parquet/json_schema_converter/type_conversion_test_cases_v0.json"
                    )
                )
            return MoreIterators.toList(testCases.elements())
                .map { testCase: JsonNode ->
                    Arguments.of(
                        testCase["fieldName"].asText(),
                        testCase["jsonFieldSchema"],
                        testCase["avroFieldType"],
                    )
                }
                .stream()
        }
    }

    internal class GetFieldTypeTestCaseProviderV1 : ArgumentsProvider {
        @Throws(Exception::class)
        override fun provideArguments(context: ExtensionContext): Stream<out Arguments> {
            val testCases =
                Jsons.deserialize(
                    MoreResources.readResource(
                        "parquet/json_schema_converter/type_conversion_test_cases_v1.json"
                    )
                )
            return MoreIterators.toList(testCases.elements())
                .map { testCase: JsonNode ->
                    Arguments.of(
                        testCase["fieldName"].asText(),
                        testCase["jsonFieldSchema"],
                        testCase["avroFieldType"],
                    )
                }
                .stream()
        }
    }

    @Suppress("DEPRECATION")
    @ParameterizedTest
    @ArgumentsSource(
        GetFieldTypeTestCaseProviderV0::class,
    )
    internal fun testFieldTypeConversionV0(
        fieldName: String,
        jsonFieldSchema: JsonNode,
        avroFieldType: JsonNode
    ) {
        assertEquals(
            avroFieldType,
            Jsons.deserialize(
                SCHEMA_CONVERTER.parseJsonField(
                        fieldName,
                        fieldNamespace = null,
                        jsonFieldSchema,
                        appendExtraProps = true,
                        addStringToLogicalTypes = true,
                    )
                    .toString(),
            ),
            "Test for $fieldName failed",
        )
    }

    @ParameterizedTest
    @ArgumentsSource(
        GetFieldTypeTestCaseProviderV1::class,
    )
    internal fun testFieldTypeConversionV1(
        fieldName: String,
        jsonFieldSchema: JsonNode,
        avroFieldType: JsonNode?
    ) {
        assertEquals(
            avroFieldType,
            Jsons.deserialize(
                SCHEMA_CONVERTER.parseJsonField(
                        fieldName = fieldName,
                        fieldNamespace = null,
                        fieldDefinition = jsonFieldSchema,
                        appendExtraProps = true,
                        addStringToLogicalTypes = true,
                    )
                    .toString(),
            ),
            "Test for $fieldName failed",
        )
    }

    @Deprecated("")
    internal class GetAvroSchemaTestCaseProviderV0 : ArgumentsProvider {
        @Throws(Exception::class)
        override fun provideArguments(context: ExtensionContext): Stream<out Arguments> {
            val testCases =
                Jsons.deserialize(
                    MoreResources.readResource(
                        "parquet/json_schema_converter/json_conversion_test_cases_v0.json"
                    )
                )
            return MoreIterators.toList(testCases.elements())
                .map { testCase: JsonNode ->
                    Arguments.of(
                        testCase["schemaName"].asText(),
                        testCase["namespace"].asText(),
                        testCase["appendAirbyteFields"].asBoolean(),
                        testCase["jsonSchema"],
                        testCase["jsonObject"],
                        testCase["avroSchema"],
                        testCase["avroObject"],
                    )
                }
                .stream()
        }
    }

    internal class GetAvroSchemaTestCaseProviderV1 : ArgumentsProvider {
        @Throws(Exception::class)
        override fun provideArguments(context: ExtensionContext): Stream<out Arguments> {
            val testCases =
                Jsons.deserialize(
                    MoreResources.readResource(
                        "parquet/json_schema_converter/json_conversion_test_cases_v1.json"
                    )
                )
            return MoreIterators.toList(testCases.elements())
                .map { testCase: JsonNode ->
                    Arguments.of(
                        testCase["schemaName"].asText(),
                        testCase["namespace"].asText(),
                        testCase["appendAirbyteFields"].asBoolean(),
                        testCase["jsonSchema"],
                        testCase["jsonObject"],
                        testCase["avroSchema"],
                        testCase["avroObject"],
                    )
                }
                .stream()
        }
    }

    /** This test verifies both the schema and object conversion. */
    @Suppress("DEPRECATION")
    @ParameterizedTest
    @ArgumentsSource(
        GetAvroSchemaTestCaseProviderV0::class,
    )
    @Throws(Exception::class)
    internal fun testJsonAvroConversionV0(
        schemaName: String,
        namespace: String?,
        appendAirbyteFields: Boolean,
        jsonSchema: JsonNode,
        jsonObject: JsonNode?,
        avroSchema: JsonNode,
        avroObject: JsonNode?
    ) {
        val actualAvroSchema =
            SCHEMA_CONVERTER.getAvroSchema(
                jsonSchema,
                schemaName,
                namespace,
                appendAirbyteFields,
                appendExtraProps = true,
                addStringToLogicalTypes = true,
                isRootNode = true,
            )
        assertEquals(
            avroSchema,
            Jsons.deserialize(actualAvroSchema.toString()),
            "Schema conversion for $schemaName failed",
        )

        val schemaParser = Schema.Parser()
        val actualAvroObject =
            AvroConstants.JSON_CONVERTER.convertToGenericDataRecord(
                WRITER.writeValueAsBytes(jsonObject),
                schemaParser.parse(Jsons.serialize(avroSchema)),
            )
        assertEquals(
            avroObject,
            Jsons.deserialize(actualAvroObject.toString()),
            "Object conversion for $schemaName failed",
        )
    }

    @ParameterizedTest
    @ArgumentsSource(
        GetAvroSchemaTestCaseProviderV1::class,
    )
    @Throws(Exception::class)
    internal fun testJsonAvroConversionV1(
        schemaName: String,
        namespace: String?,
        appendAirbyteFields: Boolean,
        jsonSchema: JsonNode,
        jsonObject: JsonNode?,
        avroSchema: JsonNode,
        avroObject: JsonNode?
    ) {
        val actualAvroSchema =
            SCHEMA_CONVERTER.getAvroSchema(
                jsonSchema,
                schemaName,
                namespace,
                appendAirbyteFields,
                appendExtraProps = true,
                addStringToLogicalTypes = true,
                isRootNode = true,
            )
        assertEquals(
            avroSchema,
            Jsons.deserialize(actualAvroSchema.toString()),
            "Schema conversion for $schemaName failed",
        )

        val schemaParser = Schema.Parser()
        val actualAvroObject =
            AvroConstants.JSON_CONVERTER.convertToGenericDataRecord(
                WRITER.writeValueAsBytes(jsonObject),
                schemaParser.parse(Jsons.serialize(avroSchema)),
            )
        assertEquals(
            avroObject,
            Jsons.deserialize(actualAvroObject.toString()),
            "Object conversion for $schemaName failed",
        )
    }
}
