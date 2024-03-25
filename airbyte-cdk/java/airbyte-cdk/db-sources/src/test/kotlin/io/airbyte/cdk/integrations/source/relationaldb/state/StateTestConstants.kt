/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb.state

import io.airbyte.cdk.integrations.source.relationaldb.models.DbStreamState
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import java.util.*
import java.util.List
import org.testcontainers.shaded.com.google.common.collect.Lists

/** Collection of constants for use in state management-related tests. */
object StateTestConstants {
    const val NAMESPACE: String = "public"
    const val STREAM_NAME1: String = "cars"
    val NAME_NAMESPACE_PAIR1: AirbyteStreamNameNamespacePair =
        AirbyteStreamNameNamespacePair(STREAM_NAME1, NAMESPACE)
    const val STREAM_NAME2: String = "bicycles"
    val NAME_NAMESPACE_PAIR2: AirbyteStreamNameNamespacePair =
        AirbyteStreamNameNamespacePair(STREAM_NAME2, NAMESPACE)
    const val STREAM_NAME3: String = "stationary_bicycles"
    const val CURSOR_FIELD1: String = "year"
    const val CURSOR_FIELD2: String = "generation"
    const val CURSOR: String = "2000"
    const val CURSOR_RECORD_COUNT: Long = 19L

    fun getState(cursorField: String?, cursor: String?): Optional<DbStreamState> {
        return Optional.of(
            DbStreamState()
                .withStreamName(STREAM_NAME1)
                .withCursorField(Lists.newArrayList(cursorField))
                .withCursor(cursor)
        )
    }

    fun getState(
        cursorField: String?,
        cursor: String?,
        cursorRecordCount: Long
    ): Optional<DbStreamState> {
        return Optional.of(
            DbStreamState()
                .withStreamName(STREAM_NAME1)
                .withCursorField(Lists.newArrayList(cursorField))
                .withCursor(cursor)
                .withCursorRecordCount(cursorRecordCount)
        )
    }

    fun getCatalog(cursorField: String?): Optional<ConfiguredAirbyteCatalog> {
        return Optional.of(
            ConfiguredAirbyteCatalog().withStreams(List.of(getStream(cursorField).orElse(null)))
        )
    }

    fun getStream(cursorField: String?): Optional<ConfiguredAirbyteStream> {
        return Optional.of(
            ConfiguredAirbyteStream()
                .withStream(AirbyteStream().withName(STREAM_NAME1))
                .withCursorField(
                    if (cursorField == null) emptyList() else Lists.newArrayList(cursorField)
                )
        )
    }
}
