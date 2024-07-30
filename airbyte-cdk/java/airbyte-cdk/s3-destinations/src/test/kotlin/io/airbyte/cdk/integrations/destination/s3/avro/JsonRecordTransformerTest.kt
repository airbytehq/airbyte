package io.airbyte.cdk.integrations.destination.s3.avro

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.commons.jackson.MoreMappers
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class JsonRecordTransformerTest {
    @Test
    fun testRecordNoopTransformation() {
        // Load resource file complex_records.json
        val schema = javaClass.getResource("/avro/complex_schema.json")?.readText()
        val records = javaClass.getResource("/avro/complex_records.json")?.readText()
        val jsonSchema = MoreMappers.initMapper().readTree(schema)
        val jsonRecords = MoreMappers.initMapper().readTree(records)

        var index = 1
        jsonRecords.elements().forEach { jsonRecord ->
            val transformer = JsonRecordTransformer(jsonSchema as ObjectNode)
            val transformedRecord = transformer.accept(jsonRecord as ObjectNode)

            // Assert transformedRecord is equal to jsonRecord
            Assertions.assertEquals(jsonRecord, transformedRecord, "Record $index")
        }
    }

    @Test
    fun testAvroRecordsCoerceSchemalessObjectsToStrings() {
        // Load resource file schemaless_records.json
        val schema = javaClass.getResource("/avro/schemaless_objects_schema.json")?.readText()
        val records = javaClass.getResource("/avro/schemaless_objects_records.json")?.readText()

        val jsonSchema = MoreMappers.initMapper().readTree(schema)
        val jsonRecords = MoreMappers.initMapper().readTree(records)

        var sawUnionChoice = 0
        var sawArrayUnionElement = 0

        jsonRecords.elements().forEach { jsonRecord ->

            val transformer = AvroJsonRecordPreprocessor(jsonSchema as ObjectNode)
            val transformedRecord = transformer.accept(jsonRecord as ObjectNode)
            println("here: $transformedRecord")
            Assertions.assertEquals(
                jsonRecord["object_without_schema"].toString(),
                transformedRecord["object_without_schema"].asText()
            )

            val objWithSchemaExpected = jsonRecord["object_with_schema"]
            val objWithSchemaActual = transformedRecord["object_with_schema"]
            Assertions.assertEquals(
                objWithSchemaExpected["nested_schemaless_object"].toString(),
                objWithSchemaActual["nested_schemaless_object"].asText()
            )

            val arrayOfSchemalessExpected =
                objWithSchemaExpected["nested_array_of_schemaless_objects"].map { it.toString() }
            val arrayOfSchemalessActual =
                objWithSchemaActual["nested_array_of_schemaless_objects"].map { it.asText() }
            Assertions.assertEquals(arrayOfSchemalessExpected, arrayOfSchemalessActual)

            val unionSchemalessNumericExpected =
                objWithSchemaExpected["union_of_schemaless_object_and_number"]
            val unionSchemalessNumericActual =
                objWithSchemaActual["union_of_schemaless_object_and_number"]
            if (unionSchemalessNumericActual.isTextual) {
                Assertions.assertEquals(
                    unionSchemalessNumericExpected.toString(),
                    unionSchemalessNumericActual.asText()
                )
                sawUnionChoice += 1
            }

            val arrayOfUnionSchemalessIntegralExpected =
                objWithSchemaExpected["array_of_union_of_schema_object_and_integer"]
            val arrayOfUnionSchemalessIntegralActual =
                objWithSchemaActual["array_of_union_of_schema_object_and_integer"]
            arrayOfUnionSchemalessIntegralExpected.forEachIndexed { index, expected ->
                val actual = arrayOfUnionSchemalessIntegralActual[index]
                if (actual.isTextual) {
                    Assertions.assertEquals(expected.toString(), actual.asText())
                    sawArrayUnionElement += 1
                }
            }
        }

        Assertions.assertNotEquals(0, sawUnionChoice)
        Assertions.assertNotEquals(0, sawArrayUnionElement)
    }
}
