/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.salesforce.io.airbyte.integrations.destination.salesforce.http

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationOperation
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.command.SoftDelete
import io.airbyte.cdk.load.command.Update
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.Request
import io.airbyte.cdk.load.http.RequestMethod
import io.airbyte.cdk.load.http.Response
import io.airbyte.cdk.load.http.consumeBodyToString
import io.airbyte.cdk.load.http.decoder.JsonDecoder
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.util.function.Supplier
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.runBlocking

private val logger = KotlinLogging.logger {}

const val BASE64_TYPE = "base64"
const val BYTE_TYPE = "byte"
const val COMBOBOX_TYPE = "combobox"
const val COMPLEXVALUE_TYPE = "complexvalue"
const val DATACATEGORYGROUPREFERENCE_TYPE = "datacategorygroupreference"
const val EMAIL_TYPE = "email"
const val ENCRYPTEDSTRING_TYPE = "encryptedstring"
const val ID_TYPE = "id"
const val JSON_TYPE = "json"
const val MASTERRECORD_TYPE = "masterrecord"
const val MULTIPICKLIST_TYPE = "multipicklist"
const val PHONE_TYPE = "phone"
const val PICKLIST_TYPE = "picklist"
const val REFERENCE_TYPE = "reference"
const val STRING_TYPE = "string"
const val TEXTAREA_TYPE = "textarea"
const val TIME_TYPE = "time"
const val URL_TYPE = "url"
const val ANYTYPE_TYPE = "anyType"
const val CALCULATED_TYPE = "calculated"
const val LOCATION_TYPE = "location"
const val ADDRESS_TYPE = "address"
const val CURRENCY_TYPE = "currency"
const val DOUBLE_TYPE = "double"
const val LONG_TYPE = "long"
const val PERCENT_TYPE = "percent"

val SALESFORCE_STRING_TYPES: Set<String> =
    setOf(
        BASE64_TYPE,
        BYTE_TYPE,
        COMBOBOX_TYPE,
        COMPLEXVALUE_TYPE,
        DATACATEGORYGROUPREFERENCE_TYPE,
        EMAIL_TYPE,
        ENCRYPTEDSTRING_TYPE,
        ID_TYPE,
        JSON_TYPE,
        MASTERRECORD_TYPE,
        MULTIPICKLIST_TYPE,
        PHONE_TYPE,
        PICKLIST_TYPE,
        REFERENCE_TYPE,
        STRING_TYPE,
        TEXTAREA_TYPE,
        TIME_TYPE,
        URL_TYPE,
        // the following are considered "loose types"
        ANYTYPE_TYPE,
        CALCULATED_TYPE,
        LOCATION_TYPE,
        ADDRESS_TYPE,
    )
val SALESFORCE_NUMBER_TYPES: Set<String> =
    setOf(CURRENCY_TYPE, DOUBLE_TYPE, LONG_TYPE, PERCENT_TYPE)

@Singleton
class SalesforceOperationRepository(
    private val httpClient: HttpClient,
    private val baseUrl: Supplier<String>
) {
    private val decoder: JsonDecoder = JsonDecoder()
    private val coroutineScope = CoroutineScope(Dispatchers.IO)

    fun fetchAll(): List<DestinationOperation> {
        val response: Response =
            httpClient.send(
                Request(RequestMethod.GET, "${baseUrl.get()}/services/data/v62.0/sobjects")
            )

        return response.use {
            when (it.statusCode) {
                200 ->
                    it.body?.let { body ->
                        val sobjects = decoder.decode(body).get("sobjects").asIterable()
                        runBlocking {
                            sobjects
                                .map { sobject ->
                                    coroutineScope.async {
                                        fetchOperations(sobject.get("name").asText())
                                    }
                                }
                                .awaitAll()
                                .flatten()
                        }
                    }
                        ?: throw IllegalStateException(
                            "Response had proper status code 200 but had empty body"
                        )
                else -> {
                    throw IllegalStateException(
                        "Failed to get the list of objects from Salesforce API. HTTP response had status ${it.statusCode} and message is: ${response.consumeBodyToString()}",
                    )
                }
            }
        }
    }

    private fun fetchOperations(objectName: String): List<DestinationOperation> {
        val response: Response =
            httpClient.send(
                Request(
                    RequestMethod.GET,
                    "${baseUrl.get()}/services/data/v62.0/sobjects/$objectName/describe"
                )
            )
        val decodedResponse: JsonNode =
            response.use {
                when (it.statusCode) {
                    200 -> it.body?.let { body -> decoder.decode(body) }
                            ?: throw IllegalStateException(
                                "Response had proper status code 200 but had empty body"
                            )
                    else -> {
                        val responseBody = response.body?.reader(Charsets.UTF_8)?.readText() ?: ""
                        throw IllegalStateException(
                            "Failed to get the schema of objects $objectName from Salesforce API. HTTP response had status ${it.statusCode} and message is: $responseBody}",
                        )
                    }
                }
            }
        return getImportTypes(decodedResponse).mapNotNull {
            createDestinationOperation(decodedResponse, it)
        }
    }

    private fun createDestinationOperation(
        describeResponse: JsonNode,
        importType: ImportType
    ): DestinationOperation? {
        val objectName: String = describeResponse.get("name").asText()
        val matchingKeys = getMatchingKeys(importType, describeResponse.get("fields"))
        val matchingKeysFlattened = matchingKeys.flatten().toSet()
        val fieldsForSyncMode =
            describeResponse.get("fields").asIterable().filter {
                availableOnSyncMode(importType, it, matchingKeysFlattened)
            }

        if (fieldsForSyncMode.isEmpty()) {
            logger.warn {
                "Object $objectName has no fields and therefore will not be added to the catalog"
            }
            return null
        }
        return DestinationOperation(
            objectName,
            importType,
            getSchema(fieldsForSyncMode, matchingKeysFlattened),
            matchingKeys,
        )
    }

    private fun getImportTypes(sobject: JsonNode): Set<ImportType> {
        val createable = sobject.get("createable").asBoolean()
        val updateable = sobject.get("updateable").asBoolean()
        val hasExternalIds = !getMatchingKeys(createDedupe(), sobject.get("fields")).isEmpty()
        return buildSet {
            if (createable) {
                add(Append)
            }
            if (updateable) {
                add(Update)
            }
            if (createable && updateable && hasExternalIds) {
                add(createDedupe())
            }
            if (sobject.get("deletable").asBoolean()) {
                add(SoftDelete)
            }
        }
    }

    private fun getSchema(
        fieldsForSyncMode: List<JsonNode>,
        matchingKeysFlattened: Set<String>
    ): AirbyteType {
        return ObjectType(
            properties =
                fieldsForSyncMode.associateTo(LinkedHashMap()) {
                    it.get("name").asText() to getJsonSchemaField(it)
                },
            additionalProperties = false,
            required =
                fieldsForSyncMode
                    .filter { isFieldMandatory() }
                    .filter { it.get("name").asText() !in matchingKeysFlattened }
                    .map { it.get("name").asText() }
        )
    }

    private fun availableOnSyncMode(
        importType: ImportType,
        field: JsonNode,
        matchingKeysFlattened: Set<String>
    ): Boolean {
        if (field.get("name").asText() in matchingKeysFlattened) {
            return true
        }

        return when (importType) {
            is Append -> field.get("createable").asBoolean()
            is Update -> field.get("updateable").asBoolean()
            is Dedupe ->
                field.get("createable").asBoolean() &&
                    field
                        .get("updateable")
                        .asBoolean() // To be fair, I'm not sure about this logic so if a user has
            // an issue with this, we should re-evaluate this logic
            is SoftDelete -> false
            else -> throw IllegalArgumentException("unsupported DestinationSyncMode $importType")
        }
    }

    private fun isFieldMandatory(): Boolean {
        // Based on case https://help.salesforce.com/s/case-view?caseId=500Hx00000ruQVxIAM, the most
        // accurate solution was `F.isCreateable() && !F.isNillable() && !F.isDefaultedOnCreate() &&
        // F.isSortable()` but there were some false positives i.e. fields that would match this
        // criteria but would not be required. An Idea was posted to Salesforce
        // [here](https://ideas.salesforce.com/s/idea/a0BHp000016L3jKMAS/describe-api-return-isrequired) as a feature request. In the meanwhile, we will let users figure out what are the mandatory fields.
        return false
    }

    private fun getMatchingKeys(importType: ImportType, fields: JsonNode): List<List<String>> {
        return when (importType) {
            is Append -> emptyList()
            is Dedupe ->
                fields
                    .asIterable()
                    .filter { it.get("externalId").asBoolean() }
                    .map { it.get("name").asText() }
                    .map { listOf(it) }
            is Update,
            is SoftDelete -> listOf(listOf("Id"))
            else -> throw IllegalArgumentException("unsupported DestinationSyncMode $importType")
        }
    }

    private fun getJsonSchemaField(field: JsonNode): FieldType {
        val nullable: Boolean = field.get("nillable").asBoolean()
        return when (val type = field.get("type").asText()) {
            in SALESFORCE_STRING_TYPES -> FieldType(StringType, nullable)
            in SALESFORCE_NUMBER_TYPES -> FieldType(NumberType, nullable)
            "int" -> FieldType(IntegerType, nullable)
            "boolean" -> FieldType(BooleanType, nullable)
            "date" -> FieldType(DateType, nullable)
            "datetime" -> FieldType(TimestampTypeWithTimezone, nullable)
            else -> throw IllegalArgumentException("unsupported salesforce type $type")
        }
    }

    private fun createDedupe(): Dedupe {
        return Dedupe(emptyList(), emptyList())
    }
}
