/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.customerio.io.airbyte.integrations.destination.customerio.batch

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.util.Jsons

class PersonIdentifyBatchEntryAssembler(
    private val identifierType: IdentifierType = IdentifierType.EMAIL
) : BatchEntryAssembler {

    companion object {
        val IDENTIFIER_PROPERTIES: Set<String> =
            setOf("person_email", "person_id", "person_cio_id")
    }

    override fun assemble(record: DestinationRecordRaw): ObjectNode {
        val recordAsJson = record.asJsonRecord()
        val identifierValue =
            recordAsJson.get(identifierType.recordField)?.asText()
                ?: throw IllegalArgumentException("${identifierType.recordField} field cannot be empty")
        val batchEntry = Jsons.objectNode().put("type", "person").put("action", "identify")

        batchEntry.putObject("identifiers").put(identifierType.apiField, identifierValue)

        val attributes = batchEntry.putObject("attributes")
        (recordAsJson as ObjectNode).properties().forEach { (key, value) ->
            if (key !in IDENTIFIER_PROPERTIES) {
                attributes.replace(key, value)
            }
        }

        return batchEntry
    }
}
