/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.commons.json.Jsons
import io.debezium.engine.ChangeEvent

class ChangeEventWithMetadata(private val event: ChangeEvent<String?, String?>) {
    private val eventKeyAsJson: JsonNode = Jsons.deserialize(event.key())
    private val eventValueAsJson: JsonNode = Jsons.deserialize(event.value())
    private val snapshotMetadata: SnapshotMetadata? =
        SnapshotMetadata.Companion.fromString(eventValueAsJson["source"]["snapshot"].asText())

    fun event(): ChangeEvent<String?, String?> {
        return event
    }

    fun eventKeyAsJson(): JsonNode {
        return eventKeyAsJson
    }

    fun eventValueAsJson(): JsonNode {
        return eventValueAsJson
    }

    val isSnapshotEvent: Boolean
        get() = SnapshotMetadata.Companion.isSnapshotEventMetadata(snapshotMetadata)

    fun snapshotMetadata(): SnapshotMetadata? {
        return snapshotMetadata
    }
}
