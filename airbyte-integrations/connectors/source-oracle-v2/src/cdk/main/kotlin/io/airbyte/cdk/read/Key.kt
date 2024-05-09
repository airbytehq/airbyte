/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.source.Field
import io.airbyte.cdk.source.FieldOrMetaField
import io.airbyte.cdk.source.TableName
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.airbyte.protocol.models.v0.SyncMode

/**
 * [Key] identifies a partition of the work required for a READ operation.
 *
 * This effectively allows us to have one thread per [Key] instance and perform READ concurrently.
 */
sealed interface Key

/** Acts as a key for [GlobalState]. */
data class GlobalKey(val streamKeys: List<StreamKey>) : Key

/**
 * Acts as a key for [StreamState]
 *
 * Essentially maps to a [io.airbyte.protocol.models.v0.ConfiguredAirbyteStream].
 */
data class StreamKey(
    val table: TableName,
    val fields: List<Field>,
    val primaryKeyCandidates: List<List<Field>>,
    val cursorCandidates: List<FieldOrMetaField>,
    val configuredSyncMode: SyncMode,
    val configuredPrimaryKey: List<Field>?,
    val configuredCursor: FieldOrMetaField?,
) : Key {

    val name: String
        get() = table.name

    val namespace: String?
        get() = table.schema ?: table.catalog

    val namePair: AirbyteStreamNameNamespacePair
        get() = AirbyteStreamNameNamespacePair(name, namespace)

    val streamDescriptor: StreamDescriptor
        get() = StreamDescriptor().withName(name).withNamespace(namespace)
}
