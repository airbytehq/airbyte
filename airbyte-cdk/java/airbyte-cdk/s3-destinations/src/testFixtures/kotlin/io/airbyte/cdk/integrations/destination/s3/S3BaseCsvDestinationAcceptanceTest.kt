/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3

import com.amazonaws.services.s3.model.S3Object
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.s3.util.Flattening
import io.airbyte.commons.jackson.MoreMappers
import io.airbyte.commons.json.Jsons
import java.io.IOException
import java.io.InputStreamReader
import java.io.Reader
import java.nio.charset.StandardCharsets
import java.util.*
import java.util.stream.StreamSupport
import org.apache.commons.csv.CSVFormat
import org.apache.commons.csv.CSVRecord
import org.apache.commons.csv.QuoteMode

abstract class S3BaseCsvDestinationAcceptanceTest :
    S3DestinationAcceptanceTest(FileUploadFormat.CSV, supportsChangeCapture = false) {
    override val formatConfig: JsonNode?
        get() =
            Jsons.jsonNode(
                java.util.Map.of(
                    "format_type",
                    outputFormat,
                    "flattening",
                    Flattening.ROOT_LEVEL.value,
                    "compression",
                    Jsons.jsonNode(java.util.Map.of("compression_type", "No Compression"))
                )
            )

    @Throws(IOException::class)
    override fun retrieveRecords(
        testEnv: TestDestinationEnv?,
        streamName: String,
        namespace: String,
        streamSchema: JsonNode
    ): List<JsonNode> {
        val objectSummaries = getAllSyncedObjects(streamName, namespace)

        val fieldTypes = getFieldTypes(streamSchema)
        val jsonRecords: MutableList<JsonNode> = LinkedList()

        for (objectSummary in objectSummaries) {
            s3Client!!.getObject(objectSummary.bucketName, objectSummary.key).use { `object` ->
                getReader(`object`).use { `in` ->
                    val records: Iterable<CSVRecord> =
                        CSVFormat.Builder.create()
                            .setHeader()
                            .setSkipHeaderRecord(true)
                            .setQuoteMode(QuoteMode.NON_NUMERIC)
                            .build()
                            .parse(`in`)
                    StreamSupport.stream(records.spliterator(), false).forEach { r: CSVRecord ->
                        jsonRecords.add(getJsonNode(r.toMap(), fieldTypes))
                    }
                }
            }
        }

        return jsonRecords
    }

    @Throws(IOException::class)
    protected open fun getReader(s3Object: S3Object): Reader {
        return InputStreamReader(s3Object.objectContent, StandardCharsets.UTF_8)
    }

    companion object {
        /** Convert json_schema to a map from field name to field types. */
        private fun getFieldTypes(streamSchema: JsonNode): Map<String, String> {
            val fieldTypes: MutableMap<String, String> = HashMap()
            val fieldDefinitions = streamSchema["properties"]
            val iterator = fieldDefinitions.fields()
            while (iterator.hasNext()) {
                val entry = iterator.next()
                val fieldValue = entry.value
                val typeValue =
                    if (fieldValue.has("type")) fieldValue["type"]
                    else if (fieldValue.has("\$ref")) fieldValue["\$ref"]
                    else if (fieldValue.has("oneOf")) {
                        val typeArray = MoreMappers.initMapper().createArrayNode()
                        fieldValue["oneOf"].forEach { typeArray.add(it["type"]) }
                        typeArray
                    } else {
                        throw IllegalStateException("Field type $fieldValue not recognized.")
                    }
                fieldTypes[entry.key] = typeValue.asText()
            }
            return fieldTypes
        }

        private fun getJsonNode(
            input: Map<String, String>,
            fieldTypes: Map<String, String>
        ): JsonNode {
            val json: ObjectNode = MAPPER.createObjectNode()

            for ((key, value) in input) {
                if (
                    key == JavaBaseConstants.COLUMN_NAME_AB_ID ||
                        (key == JavaBaseConstants.COLUMN_NAME_EMITTED_AT) ||
                        (key == JavaBaseConstants.COLUMN_NAME_AB_RAW_ID) ||
                        (key == JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT) ||
                        (key == JavaBaseConstants.COLUMN_NAME_AB_META) ||
                        (key == JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID) ||
                        (key == JavaBaseConstants.COLUMN_NAME_DATA)
                ) {
                    json.put(key, value)
                }

                val type = fieldTypes[key]
                if (value == "") {
                    when (type) {
                        "WellKnownTypes.json#/definitions/Boolean" ->
                            json.put(key, null as Boolean?)
                        "WellKnownTypes.json#/definitions/Integer" -> json.put(key, null as Int?)
                        "WellKnownTypes.json#/definitions/Number" -> json.put(key, null as Double?)
                        "boolean" -> json.put(key, null as Boolean?)
                        "integer" -> json.put(key, null as Int?)
                        "number" -> json.put(key, null as Double?)
                        "" -> addNoTypeValue(json, key, value)
                        else -> json.put(key, value)
                    }
                } else {
                    try {
                        when (type) {
                            "WellKnownTypes.json#/definitions/Boolean" ->
                                json.put(key, value.toBoolean())
                            "WellKnownTypes.json#/definitions/Integer" ->
                                json.put(key, value.toInt())
                            "WellKnownTypes.json#/definitions/Number" ->
                                json.put(key, value.toDouble())
                            "boolean" -> json.put(key, value.toBoolean())
                            "integer" -> json.put(key, value.toInt())
                            "number" -> json.put(key, value.toDouble())
                            "" -> addNoTypeValue(json, key, value)
                            else -> json.put(key, value)
                        }
                    } catch (e: Exception) {
                        // We expect this to fail in the bad field case.
                        json.put(key, value)
                    }
                }
            }
            return json
        }

        private fun addNoTypeValue(json: ObjectNode, key: String, value: String?) {
            if (
                value != null && (value.matches("^\\[.*\\]$".toRegex())) ||
                    value!!.matches("^\\{.*\\}$".toRegex())
            ) {
                val newNode = Jsons.deserialize(value)
                json.set<JsonNode>(key, newNode)
            } else {
                json.put(key, value)
            }
        }
    }
}
