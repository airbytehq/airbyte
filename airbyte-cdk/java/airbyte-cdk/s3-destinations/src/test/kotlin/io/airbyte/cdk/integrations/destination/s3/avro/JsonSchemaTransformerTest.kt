package io.airbyte.cdk.integrations.destination.s3.avro

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.commons.jackson.MoreMappers
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class JsonSchemaTransformerTest {
    @Test
    fun testSchemaNoopTransformation() {
        // Load resource file complex_schema.json
        val schema = javaClass.getResource("/avro/complex_schema.json")?.readText()
        val jsonSchema = MoreMappers.initMapper().readTree(schema)

        // Create a JsonSchemaTransformer object
        val transformer = JsonSchemaTransformer()
        val transformedSchema = transformer.accept(jsonSchema as ObjectNode)

        // Assert transformedSchema is equal to jsonSchema
        Assertions.assertEquals(jsonSchema, transformedSchema)
    }

    @Test
    fun testAvroSchemasCoerceSchemalessObjectsToStrings() {
        // Load resource file schemaless_object.json
        val schema = javaClass.getResource("/avro/schemaless_objects.json")?.readText()
        val jsonSchema = MoreMappers.initMapper().readTree(schema)

        // Create a JsonSchemaAvroPreprocessor object
        val transformer = JsonSchemaAvroPreprocessor()
        val transformedSchema = transformer.accept(jsonSchema as ObjectNode)

        // Assert transformedSchema is equal to expectedSchema
        val properties = transformedSchema["properties"]
        val objectWithoutSchema = properties["object_without_schema"]
        Assertions.assertEquals("string", objectWithoutSchema["type"].asText())

        val objectWithSchema = properties["object_with_schema"]
        val objectWithSchemaProperties = objectWithSchema["properties"]
        val nestedSchemaless = objectWithSchemaProperties["nested_schemaless_object"]
        Assertions.assertEquals("string", nestedSchemaless["type"].asText())

        val nestedArrayOfSchemalessObjects = objectWithSchemaProperties["nested_array_of_schemaless_objects"]
        val nestedArrayItemSchema = nestedArrayOfSchemalessObjects["items"]
        Assertions.assertEquals("string", nestedArrayItemSchema["type"].asText())

        val unionOfSchemaless = objectWithSchemaProperties["union_of_schemaless_object_and_number"]
        val unionOptions = unionOfSchemaless["oneOf"]
        val optionTypeSet = unionOptions.map { it["type"].asText() }.toSet()
        Assertions.assertEquals(setOf("string", "number"), optionTypeSet)

        val arrayOfOneSchemaless = objectWithSchemaProperties["array_of_two_object_types_one_containing_schemaless_object"]
        val arrayItems = arrayOfOneSchemaless["items"].elements()
        val itemSet = arrayItems.asSequence().map { it["type"].asText() }.toSet()
        Assertions.assertEquals(setOf("string", "integer"), itemSet)
    }
}
