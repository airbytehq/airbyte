/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.customerio.io.airbyte.integrations.destination.customerio.batch

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.util.Jsons

class PersonIdentifyBatchEntryAssembler : BatchEntryAssembler {

    companion object {
        val EXPECTED_PROPERTIES: Set<String> =
            setOf<String>(
                "person_email",
            )
    }

    override fun assemble(record: DestinationRecordRaw): ObjectNode {
        val recordAsJson = record.asJsonRecord()
        val personEmail =
            recordAsJson.get("person_email")?.asText()
                ?: throw IllegalArgumentException("person_email field cannot be empty")
        val batchEntry = Jsons.objectNode().put("type", "person").put("action", "identify")

        batchEntry.putObject("identifiers").put("email", personEmail)

        val attributes = batchEntry.putObject("attributes")
        (recordAsJson as ObjectNode).fields().forEach { (key, value) ->
            if (key !in EXPECTED_PROPERTIES) {
                attributes.replace(key, value)
            }
        }

        return batchEntry
    }
}
