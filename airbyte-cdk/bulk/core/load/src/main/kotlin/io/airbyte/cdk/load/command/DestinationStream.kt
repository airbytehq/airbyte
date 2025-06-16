/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValueProxy
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.json.AirbyteTypeToJsonSchema
import io.airbyte.cdk.load.data.json.JsonSchemaToAirbyteType
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.StreamDescriptor
import jakarta.inject.Singleton

/**
 * Internal representation of destination streams. This is intended to be a case class specialized
 * for usability.
 *
 * NOTE ON NAMESPACE MAPPING:
 *
 * When run in speed mode ([io.airbyte.cdk.load.config.DataChannelMedium] = [SOCKET]), namespace
 * mapping will be applied in the destination instead of in the orchestrator. The entails
 * - the platform will give the destination a catalog with an unmapped namespace and stream names
 * - the source will send the destination records and control messages with unmapped namespace and
 * stream names
 * - the destination will apply the namespace mapping as soon as it receives these messages (all of
 * its written data/table names/object paths will use the mapped namespace and names, same as in a
 * non-speed sync)
 * - when the destination emits control messages (state, stats), it must use the *unmapped*
 * namespace and names More generally: all inter-application communication will be unmapped, all
 * communication between the connector and the destination, or between the CDK and the connector
 * code, will be mapped.
 *
 * TO MAKE THIS AS ERROR-PROOF AS POSSIBLE:
 * - every DestinationStream must be instantiated with an [unmappedName], [unmappedNamespace], AND a
 * [NamespaceMapper]
 * - the default namespace mapper will be identity, and will work as expected for standard syncs
 * - [DestinationStream.Descriptor] will ALWAYS be MAPPED. (All code and tests should follow this
 * pattern.)
 * - [NamespaceMapper] is treated as data for the purpose of equality checks (ie, same unmapped
 * names + and same mapping rules => same stream)
 * - currently this won't impact the ordering of stream names for [AirbyteValueProxy.FieldAccessor]
 * s, but only because the only stream name mapping currently supported is prepending a uniform
 * prefix. IF THAT CHANGES, PROXY FIELD ORDERING WILL BREAK.
 */
data class DestinationStream(
    val unmappedNamespace: String?,
    val unmappedName: String,
    val importType: ImportType,
    val schema: AirbyteType,
    val generationId: Long,
    val minimumGenerationId: Long,
    val syncId: Long,
    // whether the stream corresponds to a series of files and their metadata
    val isFileBased: Boolean = false,
    // whether we will move the file (in addition to the metadata)
    val includeFiles: Boolean = false,
    val destinationObjectName: String? = null,
    val matchingKey: List<String>? = null,
    private val namespaceMapper: NamespaceMapper
) {
    val descriptor = namespaceMapper.map(namespace = unmappedNamespace, name = unmappedName)

    data class Descriptor(val namespace: String?, val name: String) {
        fun asProtocolObject(): StreamDescriptor =
            StreamDescriptor().withName(name).also {
                if (namespace != null) {
                    it.namespace = namespace
                }
            }

        fun toPrettyString(): String {
            return if (namespace == null) name else "$namespace.$name"
        }
    }

    /**
     * Provides the schema in a stable order, which can be used to query the AirbyteValueProxy
     * representation of the data provided by DestinationRecordRaw. This can also be used to build a
     * header/ordered schema as needed.
     *
     * NOTE: That for sockets this will align with the wire order of the files. This relies on that
     * source and destination will receive the same schema. (Either because mappers will be applied
     * in the CDK, or because mappers that can't be will trigger a fallback to the old path.)
     *
     * Connector Devs who build against this are guaranteed to get the best possible performance for
     * sockets, possibly at the expense of performance on non-socket syncs.
     */
    val airbyteValueProxyFieldAccessors: Array<AirbyteValueProxy.FieldAccessor> by lazy {
        if (schema is ObjectType) {
            schema.properties
                .toList()
                .sortedBy { (name, _) -> name }
                .mapIndexed { index, namedType ->
                    AirbyteValueProxy.FieldAccessor(
                        index = index,
                        name = namedType.first,
                        type = namedType.second.type
                    )
                }
                .toTypedArray()
        } else {
            emptyArray()
        }
    }

    /**
     * This is the schema of what we currently write to destinations, but this might not reflect
     * what actually exists, as many destinations have legacy data from before this schema was
     * adopted.
     */

    /**
     * This is not fully round-trippable. Destinations don't care about most of the stuff in an
     * AirbyteStream (e.g. we don't care about defaultCursorField, we only care about the _actual_
     * cursor field; we don't care about the source sync mode, we only care about the destination
     * sync mode; etc.).
     */
    fun asProtocolObject(): ConfiguredAirbyteStream =
        ConfiguredAirbyteStream()
            .withStream(
                AirbyteStream()
                    .withNamespace(unmappedNamespace)
                    .withName(unmappedName)
                    .withJsonSchema(AirbyteTypeToJsonSchema().convert(schema))
                    .withIsFileBased(isFileBased)
            )
            .withGenerationId(generationId)
            .withMinimumGenerationId(minimumGenerationId)
            .withSyncId(syncId)
            .withIncludeFiles(includeFiles)
            .withDestinationObjectName(destinationObjectName)
            .withPrimaryKey(matchingKey?.map { listOf(it) }.orEmpty())
            .apply {
                when (importType) {
                    is Append -> {
                        destinationSyncMode = DestinationSyncMode.APPEND
                    }
                    is Dedupe -> {
                        destinationSyncMode = DestinationSyncMode.APPEND_DEDUP
                        cursorField = importType.cursor
                        primaryKey = importType.primaryKey
                    }
                    Overwrite -> {
                        destinationSyncMode = DestinationSyncMode.OVERWRITE
                    }
                    SoftDelete -> destinationSyncMode = DestinationSyncMode.SOFT_DELETE
                    Update -> destinationSyncMode = DestinationSyncMode.UPDATE
                }
            }

    fun shouldBeTruncatedAtEndOfSync(): Boolean {
        return importType is Overwrite ||
            (minimumGenerationId == generationId && minimumGenerationId > 0)
    }

    fun isSingleGenerationTruncate() =
        shouldBeTruncatedAtEndOfSync() && minimumGenerationId == generationId
}

@Singleton
class DestinationStreamFactory(
    private val jsonSchemaToAirbyteType: JsonSchemaToAirbyteType,
    private val namespaceMapper: NamespaceMapper
) {
    fun make(stream: ConfiguredAirbyteStream): DestinationStream {
        return DestinationStream(
            unmappedNamespace = stream.stream.namespace,
            unmappedName = stream.stream.name,
            namespaceMapper = namespaceMapper,
            importType =
                when (stream.destinationSyncMode) {
                    null -> throw IllegalArgumentException("Destination sync mode was null")
                    DestinationSyncMode.APPEND -> Append
                    DestinationSyncMode.OVERWRITE -> Overwrite
                    DestinationSyncMode.APPEND_DEDUP ->
                        Dedupe(primaryKey = stream.primaryKey, cursor = stream.cursorField)
                    DestinationSyncMode.UPDATE -> Update
                    DestinationSyncMode.SOFT_DELETE -> SoftDelete
                },
            generationId = stream.generationId,
            minimumGenerationId = stream.minimumGenerationId,
            syncId = stream.syncId,
            schema = jsonSchemaToAirbyteType.convert(stream.stream.jsonSchema),
            isFileBased = stream.stream.isFileBased ?: false,
            includeFiles = stream.includeFiles ?: false,
            destinationObjectName = stream.destinationObjectName,
            matchingKey =
                stream.destinationObjectName?.let {
                    fromCompositeNestedKeyToCompositeKey(stream.primaryKey)
                }
        )
    }
}

private fun fromCompositeNestedKeyToCompositeKey(
    compositeNestedKey: List<List<String>>
): List<String> {
    if (compositeNestedKey.any { it.size > 1 }) {
        throw IllegalArgumentException(
            "Nested keys are not supported for matching keys. Key was $compositeNestedKey"
        )
    }
    if (compositeNestedKey.any { it.isEmpty() }) {
        throw IllegalArgumentException(
            "Parts of the composite key need to have at least one element. Key was $compositeNestedKey"
        )
    }

    return compositeNestedKey.map { it[0] }.toList()
}

sealed interface ImportType

data object Append : ImportType

data class Dedupe(
    /**
     * theoretically, the path to the fields in the PK. In practice, most destinations only support
     * PK at the root level, i.e. `listOf(listOf(pkField1), listOf(pkField2), etc)`.
     */
    val primaryKey: List<List<String>>,
    /**
     * theoretically, the path to the cursor. In practice, most destinations only support cursors at
     * the root level, i.e. `listOf(cursorField)`.
     *
     * If this is set to an empty list, then the destination should use
     * [DestinationRecord.message.record.emittedAt] as the cursor.
     */
    val cursor: List<String>,
) : ImportType

/**
 * A legacy destination sync mode. Modern destinations depend on platform to set
 * overwrite/record-retaining behavior via the generationId / minimumGenerationId parameters, and
 * should treat this as equivalent to Append.
 *
 * [Overwrite] is approximately equivalent to an [Append] sync, with nonzeao generationId equal to
 * minimumGenerationId.
 */
// TODO should this even exist?
data object Overwrite : ImportType

data object Update : ImportType

data object SoftDelete : ImportType
