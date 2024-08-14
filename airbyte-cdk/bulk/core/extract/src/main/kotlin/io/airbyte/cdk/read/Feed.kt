/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.FieldOrMetaField
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.airbyte.protocol.models.v0.SyncMode

/**
 * [Feed] identifies part of the data consumed during a READ operation.
 *
 * It's either one of the configured streams in the catalog, or some kind of global data feed
 * comprising records for multiple streams, as is the case in database CDC.
 */
sealed interface Feed {
    val label: String
}

/** Acts as a key for Airbyte STATE messages of type GLOBAL. */
data class Global(
    val streams: List<Stream>,
) : Feed {
    override val label: String
        get() = "global"
}

/**
 * Acts as a key for Airbyte STATE messages of type STREAM.
 *
 * Roughly equivalent to a [io.airbyte.protocol.models.v0.ConfiguredAirbyteStream].
 */
data class Stream(
    val name: String,
    val namespace: String?,
    val fields: List<Field>,
    val configuredSyncMode: SyncMode,
    val configuredPrimaryKey: List<Field>?,
    val configuredCursor: FieldOrMetaField?,
) : Feed {
    val namePair: AirbyteStreamNameNamespacePair
        get() = AirbyteStreamNameNamespacePair(name, namespace)

    val streamDescriptor: StreamDescriptor
        get() = StreamDescriptor().withName(name).withNamespace(namespace)

    override val label: String
        get() = namePair.toString()
}
