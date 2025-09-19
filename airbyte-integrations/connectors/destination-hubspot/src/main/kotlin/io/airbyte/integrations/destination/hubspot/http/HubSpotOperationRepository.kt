/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.hubspot.http

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationOperation
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.discoverer.destinationobject.DynamicDestinationObjectProvider
import io.airbyte.cdk.load.discoverer.destinationobject.StaticDestinationObjectProvider
import io.airbyte.cdk.load.discoverer.operation.CompositeOperationProvider
import io.airbyte.cdk.load.discoverer.operation.DestinationOperationAssembler
import io.airbyte.cdk.load.discoverer.operation.DynamicOperationProvider
import io.airbyte.cdk.load.discoverer.operation.InsertionMethod
import io.airbyte.cdk.load.discoverer.operation.JsonNodePredicate
import io.airbyte.cdk.load.discoverer.operation.OperationProvider
import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.HttpRequester
import io.airbyte.cdk.load.http.RequestMethod
import io.airbyte.cdk.load.http.Retriever
import java.util.function.Predicate
import kotlin.collections.List

/*
HubSpot process in a way that fetching schemas for standard objects is different from custom ones. This community member documented a list of standard objects: https://community.hubspot.com/t5/APIs-Integrations/Object-Schemas-GET-All-Custom-and-Standard/m-p/881573/highlight/true#M69167
 */
class HubSpotOperationRepository(
    httpClient: HttpClient,
) {
    private val operationProvider: OperationProvider =
        CompositeOperationProvider(
            listOf(
                DynamicOperationProvider(
                    objectsSupplier = StaticDestinationObjectProvider(listOf("CONTACT")),
                    operationAssembler =
                        DestinationOperationAssembler(
                            propertiesPath = PROPERTIES_PATH,
                            insertionMethods =
                                listOf(
                                    InsertionMethod(
                                        importType = upsertOperation(),
                                        namePath = PROPERTY_NAME_PATH,
                                        typePath = PROPERTY_TYPE_PATH,
                                        matchingKeyPredicate =
                                            JsonNodePredicate(
                                                """{{ property["name"] == "email" }}"""
                                            ),
                                        availabilityPredicate = UPSERT_AVAILABILITY_PREDICATE,
                                        requiredPredicate = NEVER_REQUIRED_PREDICATE,
                                        typeMapper = TYPE_MAPPER,
                                    ),
                                ),
                            schemaRequester =
                                HttpRequester(
                                    httpClient,
                                    RequestMethod.GET,
                                    STANDARD_OBJECT_SCHEMA_URL
                                ),
                        )
                ),
                DynamicOperationProvider(
                    objectsSupplier =
                        StaticDestinationObjectProvider(listOf("COMPANY", "DEAL", "PRODUCT")),
                    operationAssembler =
                        DestinationOperationAssembler(
                            propertiesPath = PROPERTIES_PATH,
                            insertionMethods = listOf(UPSERT_UNIQUE_VALUE_INSERTION_METHOD),
                            schemaRequester =
                                HttpRequester(
                                    httpClient,
                                    RequestMethod.GET,
                                    STANDARD_OBJECT_SCHEMA_URL
                                ),
                        )
                ),
                DynamicOperationProvider(
                    objectsSupplier =
                        DynamicDestinationObjectProvider(
                            retriever =
                                Retriever(
                                    requester =
                                        HttpRequester(
                                            httpClient,
                                            RequestMethod.GET,
                                            "https://api.hubapi.com/crm/v3/schemas"
                                        ),
                                    selector = listOf("results"),
                                ),
                            namePath = OBJECT_NAME_PATH,
                        ),
                    operationAssembler =
                        DestinationOperationAssembler(
                            propertiesPath = PROPERTIES_PATH,
                            insertionMethods = listOf(UPSERT_UNIQUE_VALUE_INSERTION_METHOD),
                            schemaRequester = null,
                        ),
                ),
            )
        )

    companion object {
        val TYPE_MAPPER =
            mapOf(
                "string" to StringType,
                "enumeration" to StringType,
                "phone_number" to StringType,
                "number" to NumberType,
                "bool" to BooleanType,
                "date" to DateType,
                "datetime" to TimestampTypeWithTimezone,
            )
        val OBJECT_NAME_PATH = listOf("name")
        val PROPERTIES_PATH = listOf("properties")
        val PROPERTY_NAME_PATH = listOf("name")
        val PROPERTY_TYPE_PATH = listOf("type")
        val UPSERT_AVAILABILITY_PREDICATE =
            JsonNodePredicate(
                """{{ property["type"] != "object_coordinates" && property["modificationMetadata"]["readOnlyValue"] == false && property["calculated"] == false }}"""
            )
        val NEVER_REQUIRED_PREDICATE: Predicate<JsonNode> = Predicate { _ -> false }
        const val STANDARD_OBJECT_SCHEMA_URL =
            """https://api.hubapi.com/crm/v3/schemas/{{ object["name"] }}"""
        val UPSERT_UNIQUE_VALUE_INSERTION_METHOD =
            InsertionMethod(
                importType = upsertOperation(),
                namePath = PROPERTY_NAME_PATH,
                typePath = PROPERTY_TYPE_PATH,
                matchingKeyPredicate =
                    JsonNodePredicate(
                        """{{ property["hasUniqueValue"] && property["modificationMetadata"]["readOnlyValue"] == false }}"""
                    ),
                availabilityPredicate = UPSERT_AVAILABILITY_PREDICATE,
                requiredPredicate = NEVER_REQUIRED_PREDICATE,
                typeMapper = TYPE_MAPPER,
            )

        private fun upsertOperation(): Dedupe = Dedupe(emptyList(), emptyList())
    }

    fun fetchAll(): List<DestinationOperation> {
        return operationProvider.get()
    }
}
