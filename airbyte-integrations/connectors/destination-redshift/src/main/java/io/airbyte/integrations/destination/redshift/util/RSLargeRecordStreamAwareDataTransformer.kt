/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.util

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.JsonNodeFactory
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.destination_async.deser.StreamAwareDataTransformer
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.nio.charset.StandardCharsets
import kotlinx.coroutines.cancelChildren
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.channels.SendChannel
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import org.apache.commons.lang3.tuple.ImmutablePair

const val MAX_RECORD_SIZE_BYTES = 16 * 1024 * 1024
const val REDSHIFT_VARCHAR_MAX_BYTE_SIZE = 65535

class RSLargeRecordStreamAwareDataTransformer : StreamAwareDataTransformer {
    private val emptyNode: ObjectNode = JsonNodeFactory.instance.objectNode()

    override fun transform(
        streamDescriptor: StreamDescriptor?,
        data: JsonNode?,
        meta: AirbyteRecordMessageMeta?
    ): ImmutablePair<JsonNode, AirbyteRecordMessageMeta> {
        return if (isTooLarge(data)) return ImmutablePair.of(emptyNode, appendChanges(meta))
        else ImmutablePair.of(data, meta)
    }

    /*
     * A node can be too large if either:
     * 1. The entire record is larger than the max row size
     * 2. Any field in the record (at any depth) is larger than the max varchar size
     */
    private fun isTooLarge(data: JsonNode?): Boolean = runBlocking {
        val channel = Channel<Boolean>(50)
        val nodeSize = nodeToBytes(data)
        // If the entire record is smaller than the varchar limit, there is nothing to do here
        if (nodeSize <= REDSHIFT_VARCHAR_MAX_BYTE_SIZE) {
            return@runBlocking false
        }
        // Check if the entire record is larger than the max row size
        launch { channel.send(nodeSize > MAX_RECORD_SIZE_BYTES) }
        // When the node is smaller than the max row size,
        // Walk the node and only check fields that are larger than the max varchar size
        launch { walkNode(channel, data) }
        for (result in channel) {
            if (result) {
                // If any value is larger than the max varchar size, stop walking the node
                coroutineContext.cancelChildren()
                return@runBlocking true
            }
        }
        return@runBlocking false
    }

    private fun nodeToBytes(data: JsonNode?): Int {
        return data.toString().toByteArray(StandardCharsets.UTF_8).size
    }

    /*
     * Walks the json node and checks if any field is too large
     * This method does not check whether the node is larger than the max row size
     */
    private suspend fun walkNode(
        channel: SendChannel<Boolean>,
        node: JsonNode?,
    ) = runBlocking {
        val filteredFields = Channel<JsonNode>(50)

        /*
        For object nodes, walk the fields and add any fields that are larger than the
        max varchar size to the filteredFields channel
         */
        suspend fun queueObjectFields(node: JsonNode?) {
            if (node != null) {
                for (field in node.fields()) {
                    if (nodeToBytes(node) > REDSHIFT_VARCHAR_MAX_BYTE_SIZE) {
                        filteredFields.send(node)
                    }
                }
            }
        }

        /*
        For array nodes, iterate through the array and add any fields that are larger than the
        REDSHIFT_VARCHAR_MAX_BYTE_SIZE to the filteredFields channel
         */
        suspend fun queueArrayFields(node: JsonNode?) {
            if (node != null) {
                for (item in node) {
                    if (nodeToBytes(item) > REDSHIFT_VARCHAR_MAX_BYTE_SIZE) {
                        if (item.isObject) queueObjectFields(item)
                        else if (item.isArray) queueArrayFields(item) else channel.send(true)
                    }
                }
            }
        }

        queueObjectFields(node)

        for (field: JsonNode in filteredFields) {
            if (field.isObject) {
                queueObjectFields(field)
            } else if (field.isArray) {
                queueArrayFields(field)
            } else {
                // All the nodes sent to this channel are larger than the max varchar size
                // If they are not containers, they are larger than the max varchar size
                channel.send(true)
            }
        }
    }
    private fun appendChanges(meta: AirbyteRecordMessageMeta?): AirbyteRecordMessageMeta {
        val newMeta = meta ?: AirbyteRecordMessageMeta()
        // TODO update field from all ?
        newMeta.changes.add(
            AirbyteRecordMessageMetaChange()
                .withField("all")
                .withChange(Change.NULLED)
                .withReason(
                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_RECORD_SIZE_LIMITATION
                )
        )
        return newMeta
    }
}
