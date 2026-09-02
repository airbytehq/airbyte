/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.customerio.io.airbyte.integrations.destination.customerio.batch

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.util.Jsons

class PersonEventBatchEntryAssembler(
    private val identifierType: IdentifierType = IdentifierType.EMAIL
) : BatchEntryAssembler {

    companion object {
        val EVENT_PROPERTIES: Set<String> = setOf("event_name", "event_id", "timestamp")
        val IDENTIFIER_PROPERTIES: Set<String> = setOf("person_email", "person_id", "person_cio_id")
    }

    override fun assemble(record: DestinationRecordRaw): ObjectNode {
        val recordAsJson = record.asJsonRecord()
        val identifierValue =
            recordAsJson.get(identifierType.recordField)?.asText()
                ?: throw IllegalArgumentException(
                    "${identifierType.recordField} field cannot be empty"
                )
        val eventName =
            recordAsJson.get("event_name")?.asText()
                ?: throw IllegalArgumentException("event_name field cannot be empty")
        val batchEntry =
            Jsons.objectNode().put("type", "person").put("action", "event").put("name", eventName)

        batchEntry.putObject("identifiers").put(identifierType.apiField, identifierValue)

        recordAsJson.get("event_id")?.let { batchEntry.put("id", it.asText()) }
        recordAsJson.get("timestamp")?.let { batchEntry.put("timestamp", it.asText()) }

        val excludedProperties = EVENT_PROPERTIES + IDENTIFIER_PROPERTIES
        val attributes = batchEntry.putObject("attributes")
        (recordAsJson as ObjectNode).properties().forEach { (key, value) ->
            if (key !in excludedProperties) {
                attributes.replace(key, value)
            }
        }

        return batchEntry
    }
}
