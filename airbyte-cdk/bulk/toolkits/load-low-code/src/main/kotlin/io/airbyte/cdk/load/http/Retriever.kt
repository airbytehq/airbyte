/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.http

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.discoverer.operation.extractArray
import io.airbyte.cdk.load.http.decoder.JsonDecoder

/**
 * This class has not been used yet but the value of addition functionality on top of HttpRequester
 * for uses cases like DynamicDestinationObjectSupplier
 *
 * Eventually should support other types of decoders (for example, destination-salesforce failed
 * results), pagination (no case identified yet), etc...
 */
class Retriever(
    private val requester: HttpRequester,
    private val selector: List<String>,
) {
    // FIXME eventually generify decoders
    val decoder: JsonDecoder = JsonDecoder()

    fun getAll(): List<JsonNode> {
        return requester.send().use {
            decoder.decode(it.getBodyOrEmpty()).extractArray(selector).asSequence().toList()
        }
    }
}
