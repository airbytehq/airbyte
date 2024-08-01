package io.airbyte.cdk.integrations.destination.s3.avro

import com.fasterxml.jackson.databind.node.JsonNodeFactory
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
            val transformer = JsonRecordIdentityMapper()
            val transformedRecord = transformer.mapRecordWithSchema(jsonRecord, jsonSchema as ObjectNode)

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

            val transformer = JsonRecordAvroPreprocessor()
            val transformedRecord = transformer.mapRecordWithSchema(jsonRecord as ObjectNode, jsonSchema as ObjectNode)
            println("here: $transformedRecord")
            Assertions.assertEquals(
                jsonRecord["object_without_schema"].toString(),
                transformedRecord?.get("object_without_schema")?.asText()
            )

            val objWithSchemaExpected = jsonRecord["object_with_schema"]
            val objWithSchemaActual = transformedRecord?.get("object_with_schema")
            Assertions.assertEquals(
                objWithSchemaExpected["nested_schemaless_object"].toString(),
                objWithSchemaActual?.get("nested_schemaless_object")?.asText()
            )

            val arrayOfSchemalessExpected =
                objWithSchemaExpected["nested_array_of_schemaless_objects"].map { it.toString() }
            val arrayOfSchemalessActual =
                objWithSchemaActual?.get("nested_array_of_schemaless_objects")?.map { it.asText() }
            Assertions.assertEquals(arrayOfSchemalessExpected, arrayOfSchemalessActual)

            val unionSchemalessNumericExpected =
                objWithSchemaExpected["union_of_schemaless_object_and_number"]
            val unionSchemalessNumericActual =
                objWithSchemaActual?.get("union_of_schemaless_object_and_number")
            if (unionSchemalessNumericActual?.isTextual == true) {
                Assertions.assertEquals(
                    unionSchemalessNumericExpected.toString(),
                    unionSchemalessNumericActual.asText()
                )
                sawUnionChoice += 1
            }

            val arrayOfUnionSchemalessIntegralExpected =
                objWithSchemaExpected["array_of_union_of_schema_object_and_integer"]
            val arrayOfUnionSchemalessIntegralActual =
                objWithSchemaActual?.get("array_of_union_of_schema_object_and_integer")
            arrayOfUnionSchemalessIntegralExpected.forEachIndexed { index, expected ->
                val actual = arrayOfUnionSchemalessIntegralActual?.get(index)
                if (actual?.isTextual == true) {
                    Assertions.assertEquals(expected.toString(), actual.asText())
                    sawArrayUnionElement += 1
                }
            }
        }

        Assertions.assertNotEquals(0, sawUnionChoice)
        Assertions.assertNotEquals(0, sawArrayUnionElement)
    }

    @Test
    fun testParquetRecordsPromoteUnionsToDisjointRecords() {
        val schema = javaClass.getResource("/avro/parquet_disjoint_union_schema_in.json")?.readText()
        val recordsIn = javaClass.getResource("/avro/parquet_disjoint_union_records_in.json")?.readText()
        val expectedRecordsOut = javaClass.getResource("/avro/parquet_disjoint_union_records_out.json")?.readText()

        val jsonSchema = MoreMappers.initMapper().readTree(schema)
        val jsonRecordsIn = MoreMappers.initMapper().readTree(recordsIn)
        val expectedJsonRecordsOut = MoreMappers.initMapper().readTree(expectedRecordsOut)

        val transformer = JsonRecordParquetPreprocessor()
        for ((index, jsonRecord) in jsonRecordsIn.withIndex()) {
            println("IN: $jsonRecord")
            val transformedRecord = transformer.mapRecordWithSchema(jsonRecord, jsonSchema as ObjectNode)
            println("OUT: $transformedRecord")
            Assertions.assertEquals(expectedJsonRecordsOut[index], transformedRecord)
        }
    }

    @Test
    fun testComposingAvroAndParquet() {
        val schemaIn = javaClass.getResource("/avro/parquet_disjoint_union_schema_in.json")?.readText()
        val recordsIn = javaClass.getResource("/avro/parquet_disjoint_union_records_in.json")?.readText()
        val expectedOut = javaClass.getResource("/avro/parquet_disjoint_union_records_out.json")?.readText()

        val jsonSchema = MoreMappers.initMapper().readTree(schemaIn)
        val jsonRecordsIn = MoreMappers.initMapper().readTree(recordsIn)
        val jsonExpectedOut = MoreMappers.initMapper().readTree(expectedOut)

        // Remove the old object and serialize it to a string
        val objNode = (jsonExpectedOut[0] as ObjectNode)["union_of_schemaless_object_and_array"] as ObjectNode
        val oldValue = objNode.remove("object")
        val newValue = MoreMappers.initMapper().writeValueAsString(oldValue)
        val strNode = JsonNodeFactory.instance.textNode(newValue)
        objNode.put("_airbyte_type", "string")
        objNode.replace("string", strNode)

        val avroRecordTransformer = AvroJsonRecordPreprocessor(jsonSchema as ObjectNode) // Use original schema
        val avroSchemaOut = AvroJsonSchemaPreprocessor().accept(jsonSchema)
        val parquetRecordTransformer = ParquetJsonRecordPreprocessor(avroSchemaOut) // Use schema produced by AvroJsonSchemaPreprocessor
        val avroRecordsOut = jsonRecordsIn.map { avroRecordTransformer.accept(it as ObjectNode) }

        for ((index, jsonRecord) in avroRecordsOut.withIndex()) {
            println("AVRO OUT: $jsonRecord")
            val transformedRecord = parquetRecordTransformer.accept(jsonRecord as ObjectNode)
            println("PARQUET OUT: $transformedRecord")
            Assertions.assertEquals(jsonExpectedOut[index], transformedRecord)
        }
    }
}
