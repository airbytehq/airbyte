package io.airbyte.integrations.destination.shelby.http.discover

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.Request
import io.airbyte.cdk.load.http.RequestMethod
import io.airbyte.cdk.load.http.Response
import io.airbyte.cdk.load.http.decoder.JsonDecoder
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.DestinationOperation
import io.airbyte.protocol.models.v0.DestinationSyncMode

val SALESFORCE_STRING_TYPES: Set<String> = setOf(
    "base64",
    "byte",
    "combobox",
    "complexvalue",
    "datacategorygroupreference",
    "email",
    "encryptedstring",
    "id",
    "json",
    "masterrecord",
    "multipicklist",
    "phone",
    "picklist",
    "reference",
    "string",
    "textarea",
    "time",
    "url",
    // the following are considered "loose types"
    "anyType",
    "calculated",
    "location",
    "address",
)
val SALESFORCE_NUMBER_TYPES: Set<String> = setOf("currency", "double", "long", "percent")
val SUPPORTED_SYNC_MODES: Set<DestinationSyncMode> = setOf(DestinationSyncMode.APPEND, DestinationSyncMode.UPDATE, DestinationSyncMode.APPEND_DEDUP, DestinationSyncMode.SOFT_DELETE)


class SalesforceOperationRepository(httpClient: HttpClient, baseUrl: String) {
    private val httpClient: HttpClient = httpClient
    private val baseUrl: String = baseUrl
    private val decoder: JsonDecoder = JsonDecoder()

    fun fetchAll(): List<DestinationOperation> {
        val response: Response = httpClient.sendRequest(
            Request(
                RequestMethod.GET,
                "${baseUrl}/services/data/v62.0/sobjects"
            )
        )
        return decoder.decode(response).get("sobjects").asIterable().flatMap { fetchOperations(it.get("name").asText()) }  // FIXME in python, we added threading here since most of the time is spent on I/O
    }

    fun fetchOperations(objectName: String): List<DestinationOperation> {
        val response: Response = httpClient.sendRequest(
            Request(
                RequestMethod.GET,
                "${baseUrl}/services/data/v62.0/sobjects/$objectName/describe"
            )
        )
        val decodedResponse: JsonNode = decoder.decode(response)
        return SUPPORTED_SYNC_MODES.map { createDestinationOperation(decodedResponse, it) }
    }

    private fun createDestinationOperation(describeResponse: JsonNode, syncMode: DestinationSyncMode) : DestinationOperation {
        val objectName: String = describeResponse.get("name").asText()
        val fieldsForSyncMode = describeResponse.get("fields").asIterable().filter { availableOnSyncMode(syncMode, it) }
        val jsonSchema = Jsons.objectNode().also { schema: ObjectNode ->
            schema.put("type", "object")
            schema.put("additionalProperties", false)
            schema.put("\$schema", "http://json-schema.org/schema#")
            schema.putArray("required").apply {
                for (requiredProperty: String in fieldsForSyncMode.filter {
                    isFieldMandatory(syncMode, it)
                }.map { it.get("name").asText() })
                    add(requiredProperty)
            }
            schema.putObject("properties").apply {
                for(field in fieldsForSyncMode) {
                    replace(field.get("name").asText(), getJsonSchemaField(field))
                }
            }
        }
        return DestinationOperation()
                .withObjectName(objectName)
                .withSyncMode(syncMode)
                .withMatchingKeys(getMatchingKeys(syncMode, describeResponse.get("fields")))
                .withJsonSchema(jsonSchema)
    }

    private fun availableOnSyncMode(syncMode: DestinationSyncMode, field: JsonNode): Boolean {
        return when(syncMode) {
            DestinationSyncMode.APPEND -> field.get("createable").asBoolean()
            DestinationSyncMode.UPDATE -> field.get("updateable").asBoolean()
            DestinationSyncMode.APPEND_DEDUP -> field.get("createable").asBoolean() && field.get("updateable").asBoolean()
            DestinationSyncMode.SOFT_DELETE -> field.get("name").asText() == "Id"
            else -> throw IllegalArgumentException("unsupported DestinationSyncMode ${syncMode.value()}")
        }
    }

    private fun isFieldMandatory(syncMode: DestinationSyncMode, field: JsonNode) : Boolean {
        return when(syncMode) {
            DestinationSyncMode.APPEND, DestinationSyncMode.APPEND_DEDUP -> !field.get("defaultedOnCreate").asBoolean() && !field.get("nillable").asBoolean()
            DestinationSyncMode.UPDATE, DestinationSyncMode.SOFT_DELETE -> false
            else -> throw IllegalArgumentException("unsupported DestinationSyncMode ${syncMode.value()}")
        }
    }

    private fun getMatchingKeys(syncMode: DestinationSyncMode, fields: JsonNode): List<List<String>> {
        return when(syncMode) {
            DestinationSyncMode.UPDATE, DestinationSyncMode.SOFT_DELETE -> listOf(listOf("Id"))
            DestinationSyncMode.APPEND_DEDUP -> listOf(fields.asIterable().filter { it.get("externalId").asBoolean() }.map { it.get("name").asText() })
            DestinationSyncMode.APPEND -> listOf(emptyList())
            else -> throw IllegalArgumentException("unsupported DestinationSyncMode ${syncMode.value()}")
        }
    }

    private fun getJsonSchemaField(field: JsonNode): JsonNode {
        val property: ObjectNode = when (val type = field.get("type").asText()) {
            in SALESFORCE_STRING_TYPES -> createPropertyNode("string")
            in SALESFORCE_NUMBER_TYPES -> createPropertyNode("number")
            "int" -> createPropertyNode("integer")
            "boolean" -> createPropertyNode("boolean")
            "date" -> createPropertyNode("date")
            "datetime" -> createPropertyNode("string", "date-time", "timestamp_with_timezone")
            else -> throw IllegalArgumentException("unsupported salesforce type $type")
        }

        if (field.get("nillable").asBoolean()) {
            val type: String = property.get("type").asText()
            property.remove("type")
            property.withArrayProperty("type").add(type).add("null")
        }
        return property
    }

    private fun createPropertyNode(type: String, format: String? = null, airbyteType: String? = null): ObjectNode {
        return Jsons.objectNode().apply {
            put("type", type)
            format?.let { put("format", format) }
            airbyteType?.let { put("airbyte_type", airbyteType) }
        }
    }
}
