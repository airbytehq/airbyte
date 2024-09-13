/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.common.annotations.VisibleForTesting
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.integrations.destination.async.deser.StreamAwareDataTransformer
import io.airbyte.commons.json.Jsons.emptyObject
import io.airbyte.commons.json.Jsons.jsonNode
import io.airbyte.commons.json.Jsons.serialize
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId
import io.airbyte.integrations.base.destination.typing_deduping.ImportType
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.charset.StandardCharsets
import java.util.*
import java.util.function.Predicate
import java.util.stream.Collectors
import org.apache.commons.lang3.tuple.ImmutablePair

private val log = KotlinLogging.logger {}

@SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
class RedshiftSuperLimitationTransformer(
    private val parsedCatalog: ParsedCatalog?,
    private val defaultNamespace: String
) : StreamAwareDataTransformer {
    private data class ScalarNodeModification(
        val size: Int,
        val removedSize: Int,
        val shouldNull: Boolean
    )

    data class TransformationInfo(
        val originalBytes: Int,
        val removedBytes: Int,
        val node: JsonNode?,
        val meta: AirbyteRecordMessageMeta
    )

    /*
     * This method walks the Json tree nodes and does the following
     *
     * 1. Collect the original bytes using UTF-8 charset. This is to avoid double walking the tree if
     * the total size > 16MB This is to optimize for best case (see worst case as 4 below) that most of
     * the data will be < 16MB and only few offending varchars > 64KB.
     *
     * 2. Replace all TextNodes with Null nodes if they are greater than 64K.
     *
     * 3. Verify if replacing the varchars with NULLs brought the record size down to < 16MB. This
     * includes verifying the original bytes and transformed bytes are below the record size limit.
     *
     * 4. If 3 is false, this is the worst case scenarios where we try to resurrect PKs and cursors and
     * trash the rest of the record.
     *
     */
    override fun transform(
        streamDescriptor: StreamDescriptor?,
        jsonNode: JsonNode?,
        airbyteRecordMessageMeta: AirbyteRecordMessageMeta?
    ): Pair<JsonNode?, AirbyteRecordMessageMeta?> {
        val startTime = System.currentTimeMillis()
        log.debug("Traversing the record to NULL fields for redshift size limitations")
        val namespace =
            if ((streamDescriptor!!.namespace != null && !streamDescriptor.namespace.isEmpty()))
                streamDescriptor.namespace
            else defaultNamespace!!
        val streamConfig = parsedCatalog!!.getStream(namespace, streamDescriptor.name)
        val cursorField = streamConfig.cursor.map(ColumnId::originalName)
        // convert List<ColumnId> to Set<ColumnId> for faster lookup
        val primaryKeys =
            streamConfig.primaryKey.stream().map(ColumnId::originalName).collect(Collectors.toSet())
        val syncMode = streamConfig.postImportAction
        val transformationInfo =
            transformNodes(jsonNode, DEFAULT_PREDICATE_VARCHAR_GREATER_THAN_64K)
        val originalBytes = transformationInfo.originalBytes
        val transformedBytes = transformationInfo.originalBytes - transformationInfo.removedBytes
        // We check if the transformedBytes has solved the record limit.
        log.debug("Traversal complete in {} ms", System.currentTimeMillis() - startTime)
        if (
            DEFAULT_PREDICATE_RECORD_SIZE_GT_THAN_16M.test(originalBytes) &&
                DEFAULT_PREDICATE_RECORD_SIZE_GT_THAN_16M.test(transformedBytes)
        ) {
            // If we have reached here with a bunch of small varchars constituted to becoming a
            // large record,
            // person using Redshift for this data should re-evaluate life choices.
            log.warn(
                "Record size before transformation {}, after transformation {} bytes exceeds 16MB limit",
                originalBytes,
                transformedBytes
            )
            val minimalNode = constructMinimalJsonWithPks(jsonNode, primaryKeys, cursorField)
            if (minimalNode.isEmpty && syncMode == ImportType.DEDUPE) {
                // Fail the sync if PKs are missing in DEDUPE, no point sending an empty record to
                // destination.
                throw RuntimeException(
                    "Record exceeds size limit, cannot transform without PrimaryKeys in DEDUPE sync"
                )
            }
            // Preserve original changes
            val changes: MutableList<AirbyteRecordMessageMetaChange> = ArrayList()
            changes.add(
                AirbyteRecordMessageMetaChange()
                    .withField("all")
                    .withChange(AirbyteRecordMessageMetaChange.Change.NULLED)
                    .withReason(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_RECORD_SIZE_LIMITATION
                    )
            )
            if (airbyteRecordMessageMeta != null && airbyteRecordMessageMeta.changes != null) {
                changes.addAll(airbyteRecordMessageMeta.changes)
            }
            return Pair(minimalNode, AirbyteRecordMessageMeta().withChanges(changes))
        }
        if (airbyteRecordMessageMeta != null && airbyteRecordMessageMeta.changes != null) {
            // The underlying list of AirbyteRecordMessageMeta is mutable
            transformationInfo.meta.changes.addAll(airbyteRecordMessageMeta.changes)
        }
        // We intentionally don't deep copy for transformation to avoid memory bloat.
        // The caller already has the reference of original jsonNode but returning again in
        // case we choose to deepCopy in future for thread-safety.
        return Pair(jsonNode, transformationInfo.meta)
    }

    private fun shouldTransformScalarNode(
        node: JsonNode?,
        textNodePredicate: Predicate<String>
    ): ScalarNodeModification {
        val bytes: Int
        if (node!!.isTextual) {
            val originalBytes = getByteSize(node.asText()) + 2 // for quotes
            if (textNodePredicate.test(node.asText())) {
                return ScalarNodeModification(
                    originalBytes, // size before nulling
                    originalBytes - 4, // account 4 bytes for null string
                    true
                )
            }
            bytes = originalBytes
        } else if (node.isNumber) {
            // Serialize exactly for numbers to account for Scientific notation converted to full
            // value.
            // This is what we send over wire for persistence.
            bytes = getByteSize(serialize<JsonNode?>(node))
        } else if (node.isBoolean) {
            bytes = getByteSize(node.toString())
        } else if (node.isNull) {
            bytes = 4 // for "null"
        } else {
            bytes = 0
        }
        return ScalarNodeModification(
            bytes, // For all other types, just return bytes
            0,
            false
        )
    }

    @VisibleForTesting
    fun transformNodes(
        rootNode: JsonNode?,
        textNodePredicate: Predicate<String>
    ): TransformationInfo {
        // Walk the tree and transform Varchars that exceed the limit
        // We are intentionally not checking the whole size upfront to check if it exceeds 16MB
        // limit to
        // optimize for best case.

        var originalBytes = 0
        var removedBytes = 0
        // We accumulate nested keys in jsonPath format for adding to airbyte changes.
        val stack: Deque<ImmutablePair<String, JsonNode?>> = ArrayDeque()
        val changes: MutableList<AirbyteRecordMessageMetaChange> = ArrayList()

        // This was intentionally done using Iterative DFS to avoid stack overflow for large
        // records.
        // This will ensure we are allocating on heap and not on stack.
        stack.push(ImmutablePair.of("$", rootNode))
        while (!stack.isEmpty()) {
            val jsonPathNodePair = stack.pop()
            val currentNode = jsonPathNodePair.right
            if (currentNode!!.isObject) {
                originalBytes += CURLY_BRACES_BYTE_SIZE
                val fields = currentNode.fields()
                while (fields.hasNext()) {
                    val field = fields.next()
                    originalBytes +=
                        getByteSize(field.key) +
                            OBJECT_COLON_QUOTES_COMMA_BYTE_SIZE // for quotes, colon, comma
                    val jsonPathKey = String.format("%s.%s", jsonPathNodePair.left, field.key)
                    // TODO: Little difficult to unify this logic in Object & Array, find a way
                    // later
                    // Push only non-scalar nodes to stack. For scalar nodes, we need reference of
                    // parent to do in-place
                    // update.
                    if (field.value.isContainerNode) {
                        stack.push(ImmutablePair.of(jsonPathKey, field.value))
                    } else {
                        val shouldTransform =
                            shouldTransformScalarNode(field.value, textNodePredicate)
                        if (shouldTransform.shouldNull) {
                            removedBytes += shouldTransform.removedSize
                            // DO NOT do this if this code every modified to a multithreading call
                            // stack
                            field.setValue(jsonNode<Any?>(null))
                            changes.add(
                                AirbyteRecordMessageMetaChange()
                                    .withField(jsonPathKey)
                                    .withChange(AirbyteRecordMessageMetaChange.Change.NULLED)
                                    .withReason(
                                        AirbyteRecordMessageMetaChange.Reason
                                            .DESTINATION_FIELD_SIZE_LIMITATION
                                    )
                            )
                        }
                        originalBytes += shouldTransform.size
                    }
                }
                originalBytes -= 1 // remove extra comma from last key-value pair
            } else if (currentNode.isArray) {
                originalBytes += SQUARE_BRACKETS_BYTE_SIZE
                val arrayNode = currentNode as ArrayNode?
                // We cannot use foreach here as we need to update the array in place.
                for (i in 0 until arrayNode!!.size()) {
                    val childNode = arrayNode[i]
                    val jsonPathKey = String.format("%s[%d]", jsonPathNodePair.left, i)
                    if (childNode.isContainerNode)
                        stack.push(ImmutablePair.of(jsonPathKey, childNode))
                    else {
                        val shouldTransform =
                            shouldTransformScalarNode(childNode, textNodePredicate)
                        if (shouldTransform.shouldNull) {
                            removedBytes += shouldTransform.removedSize
                            // DO NOT do this if this code every modified to a multithreading call
                            // stack
                            arrayNode[i] = jsonNode<Any?>(null)
                            changes.add(
                                AirbyteRecordMessageMetaChange()
                                    .withField(jsonPathKey)
                                    .withChange(AirbyteRecordMessageMetaChange.Change.NULLED)
                                    .withReason(
                                        AirbyteRecordMessageMetaChange.Reason
                                            .DESTINATION_FIELD_SIZE_LIMITATION
                                    )
                            )
                        }
                        originalBytes += shouldTransform.size
                    }
                }
                originalBytes +=
                    if (!currentNode.isEmpty) currentNode.size() - 1 else 0 // for commas
            } else { // Top level scalar node is a valid json
                originalBytes += shouldTransformScalarNode(currentNode, textNodePredicate).size
            }
        }

        if (removedBytes != 0) {
            log.info(
                "Original record size {} bytes, Modified record size {} bytes",
                originalBytes,
                (originalBytes - removedBytes)
            )
        }
        return TransformationInfo(
            originalBytes,
            removedBytes,
            rootNode,
            AirbyteRecordMessageMeta().withChanges(changes)
        )
    }

    private fun constructMinimalJsonWithPks(
        rootNode: JsonNode?,
        primaryKeys: Set<String>,
        cursorField: Optional<String>
    ): JsonNode {
        val minimalNode = emptyObject() as ObjectNode
        // We only iterate for top-level fields in the root object, since we only support PKs and
        // cursor in
        // top level keys.
        if (rootNode!!.isObject) {
            val fields = rootNode.fields()
            while (fields.hasNext()) {
                val field = fields.next()
                if (!field.value.isContainerNode) {
                    if (
                        primaryKeys.contains(field.key) ||
                            cursorField.isPresent && cursorField.get() == field.key
                    ) {
                        // Make a deepcopy into minimalNode of PKs and cursor fields and values,
                        // without deepcopy, we will re-reference the original Tree's nodes.
                        // god help us if someone set a PK on non-scalar field, and it reached this
                        // point, only do at root
                        // level
                        minimalNode.set<JsonNode>(field.key, field.value.deepCopy())
                    }
                }
            }
        } else {
            log.error(
                "Encountered {} as top level JSON field, this is not supported",
                rootNode.nodeType
            )
            // This should have caught way before it reaches here. Just additional safety.
            throw RuntimeException(
                "Encountered " +
                    rootNode.nodeType +
                    " as top level JSON field, this is not supported"
            )
        }
        return minimalNode
    }

    companion object {
        const val REDSHIFT_VARCHAR_MAX_BYTE_SIZE: Int = 65535
        const val REDSHIFT_SUPER_MAX_BYTE_SIZE: Int = 16 * 1024 * 1024

        val DEFAULT_PREDICATE_VARCHAR_GREATER_THAN_64K: Predicate<String> =
            Predicate { text: String ->
                getByteSize(text) > REDSHIFT_VARCHAR_MAX_BYTE_SIZE
            }
        val DEFAULT_PREDICATE_RECORD_SIZE_GT_THAN_16M: Predicate<Int> = Predicate { size: Int ->
            size > REDSHIFT_SUPER_MAX_BYTE_SIZE
        }

        private val CURLY_BRACES_BYTE_SIZE = getByteSize("{}")
        private val SQUARE_BRACKETS_BYTE_SIZE = getByteSize("[]")
        private val OBJECT_COLON_QUOTES_COMMA_BYTE_SIZE = getByteSize("\"\":,")

        private fun getByteSize(value: String): Int {
            return value.toByteArray(StandardCharsets.UTF_8).size
        }
    }
}
