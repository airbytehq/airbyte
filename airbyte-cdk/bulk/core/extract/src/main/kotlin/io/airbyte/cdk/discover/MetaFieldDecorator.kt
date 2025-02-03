/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.discover

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.read.Stream
import io.airbyte.protocol.models.v0.AirbyteStream
import java.time.OffsetDateTime

/** [MetaField] schema definition and utilities, to be implemented by each source connector. */
interface MetaFieldDecorator {

    /** [MetaField] to use as a global cursor, if applicable. */
    val globalCursor: FieldOrMetaField?

    /**
     * All [MetaField]s to be found in [Global] stream records.
     *
     * This must include at least [globalCursor] if not null.
     *
     * Empty set when not applicable.
     */
    val globalMetaFields: Set<MetaField>

    /** Convenience function for [AirbyteStreamFactory]. */
    fun decorateAirbyteStream(airbyteStream: AirbyteStream) {
        (airbyteStream.jsonSchema["properties"] as ObjectNode).apply {
            for (metaField in globalMetaFields) {
                set<ObjectNode>(metaField.id, metaField.type.airbyteSchemaType.asJsonSchema())
            }
        }
        val globalCursorIdentifier: String = globalCursor?.id ?: return
        airbyteStream.defaultCursorField = listOf(globalCursorIdentifier)
        airbyteStream.sourceDefinedCursor = true
    }

    /**
     * Modifies [recordData] by setting all [MetaField] values in global [Stream] feeds.
     *
     * This is required by the fact that records of a given stream may be emitted by both a [Stream]
     * and a [Global] feed and the schemas must be the same. This implies that the records emitted
     * by [Stream] must have [MetaField]s set to suitable values, even though that [Feed] has no
     * awareness of the [Global] state.
     *
     * This method is called at most once per [Stream].
     */
    fun decorateRecordData(
        /** Same value as emitted_at */
        timestamp: OffsetDateTime,
        /** Current state of the [Global] feed, if applicable. */
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: ObjectNode
    )
}
