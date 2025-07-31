/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.hubspot.io.airbyte.integrations.destination.hubspot.http

import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.Request
import io.airbyte.cdk.load.http.RequestMethod
import io.airbyte.cdk.load.http.consumeBodyToString
import io.airbyte.cdk.load.http.decoder.JsonDecoder
import io.airbyte.cdk.load.http.getBodyOrEmpty

/**
 * To query the HubSpot API for batch on custom objects, we need the ObjectTypeId as the object name
 * does not work like standard objects. This class loads once a mapping of (objectName,
 * objectTypeId) for all the customer objects.
 *
 * Note that this does not fit in the future low-code pattern. In order to solve that, we have two
 * potential solutions:
 * * Create a low-code component that could fetch additional data during the write command;
 * * Assuming this data is always available during the discover command, populate this as part of
 * the catalog. This would require a protocol change to have this information flow from the discover
 * to the write. It seems like this should be the preferable solution as it's easy to populate a new
 * field in the catalog and it wouldn't require re-specifying the query to get the information in
 * the write command in low-code.
 */
class HubSpotObjectTypeIdMapper(private val httpClient: HttpClient) {
    private val decoder: JsonDecoder = JsonDecoder()
    // This assumes there can't be twice the same object name for different object type ids.
    // I assume this is not possible because when trying to do so through the UI, I get `An object
    // with the singular label <object name> already exists.` and the `Create` button is greyed out.
    private var objectTypeIdByObjectName: Map<String, String>? = null

    /**
     * Note that even if a standard object is passed, the cache will be built. We could optimize
     * that by maintaining a list of standard objects here.
     */
    fun fetchObjectTypeId(objectName: String): String {
        if (objectTypeIdByObjectName == null) {
            buildCache()
        }

        return objectTypeIdByObjectName!![objectName] ?: objectName
    }

    private fun buildCache() {
        httpClient.send(Request(RequestMethod.GET, "https://api.hubapi.com/crm/v3/schemas")).use {
            when (it.statusCode) {
                200 ->
                    objectTypeIdByObjectName =
                        decoder
                            .decode(it.getBodyOrEmpty())
                            .get("results")
                            .asSequence()
                            .map { it.get("name").asText() to it.get("objectTypeId").asText() }
                            .toMap()
                else -> {
                    throw IllegalStateException(
                        "Failed to get the object types from HubSpot API. HTTP response had status ${it.statusCode} and message is: ${it.consumeBodyToString()}",
                    )
                }
            }
        }
    }
}
