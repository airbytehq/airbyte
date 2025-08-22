/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.customerio.io.airbyte.integrations.destination.customerio.batch

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.util.Jsons

class PersonEventBatchEntryAssembler : BatchEntryAssembler {

    companion object {
        val EXPECTED_PROPERTIES: Set<String> =
            setOf<String>(
                "person_email",
                "event_name",
                "event_id",
                "timestamp",
            )
    }

    override fun assemble(record: DestinationRecordRaw): ObjectNode {
        val recordAsJson = record.asJsonRecord()
        val personEmail =
            recordAsJson.get("person_email")?.asText()
                ?: throw IllegalArgumentException("person_email field cannot be empty")
        val eventName =
            recordAsJson.get("event_name")?.asText()
                ?: throw IllegalArgumentException("event_name field cannot be empty")
        val batchEntry =
            Jsons.objectNode().put("type", "person").put("action", "event").put("name", eventName)

        batchEntry.putObject("identifiers").put("email", personEmail)

        recordAsJson.get("event_id")?.let { batchEntry.put("id", it.asText()) }
        recordAsJson.get("timestamp")?.let { batchEntry.put("timestamp", it.asText()) }

        val attributes = batchEntry.putObject("attributes")
        (recordAsJson as ObjectNode).fields().forEach { (key, value) ->
            if (key !in EXPECTED_PROPERTIES) {
                attributes.replace(key, value)
            }
        }

        return batchEntry
    }
}
