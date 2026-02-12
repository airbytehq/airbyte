/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.export

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.JsonNodeFactory
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.json.toJson
import io.airbyte.cdk.load.message.Meta.Change
import java.time.Instant
import java.util.UUID

data class ExportedRecord(
    val rawId: UUID?,
    val extractedAt: Instant,
    val loadedAt: Instant?,
    val generationId: Long?,
    val data: ObjectValue,
    val airbyteMeta: Meta?,
) {
    data class Meta(
        val changes: List<Change> = listOf(),
        val syncId: Long? = null,
    )

    constructor(
        rawId: String,
        extractedAt: Long,
        loadedAt: Long?,
        generationId: Long?,
        data: Map<String, Any?>,
        airbyteMeta: Meta?,
    ) : this(
        rawId,
        extractedAt,
        loadedAt,
        generationId,
        ObjectValue.from(data),
        airbyteMeta,
    )

    constructor(
        rawId: String,
        extractedAt: Long,
        loadedAt: Long?,
        generationId: Long?,
        data: AirbyteValue,
        airbyteMeta: Meta?,
    ) : this(
        UUID.fromString(rawId),
        Instant.ofEpochMilli(extractedAt),
        loadedAt?.let { Instant.ofEpochMilli(it) },
        generationId,
        data as ObjectValue,
        airbyteMeta,
    )

    constructor(
        extractedAt: Long,
        generationId: Long?,
        data: Map<String, Any?>,
        airbyteMeta: Meta?,
    ) : this(
        null,
        Instant.ofEpochMilli(extractedAt),
        loadedAt = null,
        generationId,
        ObjectValue.from(data),
        airbyteMeta,
    )

    fun toJsonNode(): JsonNode {
        val node = JsonNodeFactory.instance.objectNode()
        rawId?.let { node.put("_airbyte_raw_id", it.toString()) }
        node.put("_airbyte_extracted_at", extractedAt.toEpochMilli())
        loadedAt?.let { node.put("_airbyte_loaded_at", it.toEpochMilli()) }
        generationId?.let { node.put("_airbyte_generation_id", it) }
        node.set<JsonNode>("_airbyte_data", data.toJson())
        airbyteMeta?.let { meta ->
            val metaNode = JsonNodeFactory.instance.objectNode()
            meta.syncId?.let { metaNode.put("sync_id", it) }
            val changesArray = JsonNodeFactory.instance.arrayNode()
            meta.changes.forEach { change ->
                val changeNode = JsonNodeFactory.instance.objectNode()
                changeNode.put("field", change.field)
                changeNode.put("change", change.change.value())
                changeNode.put("reason", change.reason.value())
                changesArray.add(changeNode)
            }
            metaNode.set<JsonNode>("changes", changesArray)
            node.set<JsonNode>("_airbyte_meta", metaNode)
        }
        return node
    }

    fun toJsonLine(): String = OBJECT_MAPPER.writeValueAsString(toJsonNode())

    companion object {
        private val OBJECT_MAPPER = ObjectMapper()
    }
}
