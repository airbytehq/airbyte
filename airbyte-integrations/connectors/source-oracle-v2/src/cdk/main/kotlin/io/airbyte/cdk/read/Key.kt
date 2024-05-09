/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.FieldOrMetaField
import io.airbyte.cdk.discover.TableName
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.airbyte.protocol.models.v0.SyncMode

/** Identifies a partition of the Airbyte RECORD and STATE messages emitted by a READ. */
sealed interface Key

data class GlobalKey(val streamKeys: List<StreamKey>) : Key

data class StreamKey(
    val configuredStream: ConfiguredAirbyteStream,
    val table: TableName,
    val fields: List<Field>,
    val primaryKeyCandidates: List<List<Field>>,
    val cursorCandidates: List<FieldOrMetaField>,
    val configuredSyncMode: SyncMode,
    val configuredPrimaryKey: List<Field>?,
    val configuredCursor: FieldOrMetaField?,
) : Key {

    val stream: AirbyteStream
        get() = configuredStream.stream

    val name: String
        get() = configuredStream.stream.name

    val namespace: String?
        get() = configuredStream.stream.namespace

    val namePair: AirbyteStreamNameNamespacePair
        get() = AirbyteStreamNameNamespacePair.fromConfiguredAirbyteSteam(configuredStream)

    val streamDescriptor: StreamDescriptor
        get() = StreamDescriptor().withName(name).withNamespace(namespace)
}
