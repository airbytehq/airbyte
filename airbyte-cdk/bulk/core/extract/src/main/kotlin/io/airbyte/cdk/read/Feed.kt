/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.FieldOrMetaField

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
    val id: StreamIdentifier,
    val schema: Set<FieldOrMetaField>,
    val configuredSyncMode: ConfiguredSyncMode,
    val configuredPrimaryKey: List<Field>?,
    val configuredCursor: FieldOrMetaField?,
) : Feed {
    val name: String
        get() = id.name

    val namespace: String?
        get() = id.namespace

    override val label: String
        get() = id.toString()

    val fields: List<Field>
        get() = schema.filterIsInstance<Field>()
}

/** List of [Stream]s this [Feed] emits records for. */
val Feed.streams
    get() =
        when (this) {
            is Global -> streams
            is Stream -> listOf(this)
        }
