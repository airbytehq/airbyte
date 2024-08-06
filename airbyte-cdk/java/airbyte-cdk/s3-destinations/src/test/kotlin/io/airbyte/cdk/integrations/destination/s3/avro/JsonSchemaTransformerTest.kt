/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.avro

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.destination.s3.jsonschema.JsonSchemaIdentityMapper
import io.airbyte.cdk.integrations.destination.s3.jsonschema.JsonSchemaUnionMerger
import io.airbyte.cdk.integrations.destination.s3.parquet.JsonSchemaParquetPreprocessor
import io.airbyte.commons.jackson.MoreMappers
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class JsonSchemaTransformerTest {
    private fun mangleAltCombined(node: ObjectNode) {
        val oneOf = MoreMappers.initMapper().createArrayNode()

        val option1 = MoreMappers.initMapper().createObjectNode()
        option1.put("type", "integer")
        oneOf.add(option1)

        val option2 = MoreMappers.initMapper().createObjectNode()
        option2.put("type", "string")
        oneOf.add(option2)

        node.remove("type")
        node.replace("oneOf", oneOf)
    }

    @Test
    fun testSchemaNoopTransformation() {
        // Load resource file complex_schema.json
        val schema = javaClass.getResource("/avro/complex_schema.json")?.readText()
        val jsonSchema = MoreMappers.initMapper().readTree(schema)

        // Create a JsonSchemaTransformer object
        val transformer = JsonSchemaIdentityMapper()
        val transformedSchema = transformer.mapSchema(jsonSchema as ObjectNode) as ObjectNode

        // Assert transformedSchema is equal to jsonSchema, accounting for a little normalization
        transformedSchema.remove("type")
        mangleAltCombined(jsonSchema["properties"]["combined_type_alt"] as ObjectNode)
        Assertions.assertEquals(jsonSchema, transformedSchema)
    }

    @Test
    fun testAvroSchemasCoerceSchemalessObjectsToStrings() {
        // Load resource file schemaless_object.json
        val schema = javaClass.getResource("/avro/schemaless_objects_schema.json")?.readText()
        val jsonSchema = MoreMappers.initMapper().readTree(schema)

        // Create a JsonSchemaAvroPreprocessor object
        val transformer = JsonSchemaAvroPreprocessor()
        val transformedSchema = transformer.mapSchema(jsonSchema as ObjectNode)

        // Assert transformedSchema is equal to expectedSchema
        val properties = transformedSchema["properties"]
        val objectWithoutSchema = properties["object_without_schema"]
        Assertions.assertEquals("string", objectWithoutSchema["type"].asText())

        val objectWithSchema = properties["object_with_schema"]
        val objectWithSchemaProperties = objectWithSchema["properties"]
        val nestedSchemaless = objectWithSchemaProperties["nested_schemaless_object"]
        Assertions.assertEquals("string", nestedSchemaless["type"].asText())

        val nestedArrayOfSchemalessObjects =
            objectWithSchemaProperties["nested_array_of_schemaless_objects"]
        val nestedArrayItemSchema = nestedArrayOfSchemalessObjects["items"]
        Assertions.assertEquals("string", nestedArrayItemSchema["type"].asText())

        val unionOfSchemaless = objectWithSchemaProperties["union_of_schemaless_object_and_number"]
        val unionOptions = unionOfSchemaless["oneOf"]
        val optionTypeSet = unionOptions.map { it["type"].asText() }.toSet()
        Assertions.assertEquals(setOf("string", "number"), optionTypeSet)

        val arrayOfOneSchemaless =
            objectWithSchemaProperties["array_of_union_of_schema_object_and_integer"]
        val arrayItems = arrayOfOneSchemaless["items"].elements()
        val itemSet = arrayItems.asSequence().map { it["type"].asText() }.toSet()
        Assertions.assertEquals(setOf("string", "integer"), itemSet)
    }

    @Test
    fun testParquetSchemasPromoteUnionsToDisjointRecords() {
        val inputSchemaStr =
            javaClass.getResource("/avro/parquet_disjoint_union_schema_in.json")?.readText()
        val inputSchema = MoreMappers.initMapper().readTree(inputSchemaStr) as ObjectNode
        val expectedSchemaStr =
            javaClass.getResource("/avro/parquet_disjoint_union_schema_out.json")?.readText()
        val expectedSchema = MoreMappers.initMapper().readTree(expectedSchemaStr) as ObjectNode

        val transformedSchema = JsonSchemaParquetPreprocessor().mapSchema(inputSchema)

        Assertions.assertEquals(expectedSchema, transformedSchema)
    }

    @Test
    fun testComposingAvroAndParquet() {
        val inputSchemaStr =
            javaClass.getResource("/avro/parquet_disjoint_union_schema_in.json")?.readText()
        val inputSchema = MoreMappers.initMapper().readTree(inputSchemaStr) as ObjectNode
        val expectedSchemaStr =
            javaClass.getResource("/avro/parquet_avro_schema_disjoint_union_out.json")?.readText()
        val expectedSchema = MoreMappers.initMapper().readTree(expectedSchemaStr) as ObjectNode

        val avroTransformed = JsonSchemaAvroPreprocessor().mapSchema(inputSchema)
        val transformedSchema =
            JsonSchemaParquetPreprocessor().mapSchema(avroTransformed as ObjectNode)

        Assertions.assertEquals(expectedSchema, transformedSchema)
    }

    @Test
    fun testUnionsOfObjects() {
        val inputSchemaStr = javaClass.getResource("/avro/object_unions_schema_in.json")?.readText()
        val inputSchema = MoreMappers.initMapper().readTree(inputSchemaStr) as ObjectNode
        val outputSchemaStr =
            javaClass.getResource("/avro/object_unions_schema_out.json")?.readText()
        val outputSchema = MoreMappers.initMapper().readTree(outputSchemaStr) as ObjectNode

        val transformedSchema = JsonSchemaUnionMerger().mapSchema(inputSchema)
        Assertions.assertEquals(outputSchema, transformedSchema)
    }
}
