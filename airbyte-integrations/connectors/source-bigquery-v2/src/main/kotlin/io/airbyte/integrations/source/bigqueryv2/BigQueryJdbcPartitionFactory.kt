/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.output.CatalogValidationFailureHandler
import io.airbyte.cdk.output.InvalidCursor
import io.airbyte.cdk.output.ResetStream
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.DefaultJdbcPartition
import io.airbyte.cdk.read.DefaultJdbcPartitionFactory
import io.airbyte.cdk.read.DefaultJdbcSharedState
import io.airbyte.cdk.read.DefaultJdbcSplittableSnapshotPartition
import io.airbyte.cdk.read.DefaultJdbcSplittableSnapshotWithCursorPartition
import io.airbyte.cdk.read.DefaultJdbcStreamState
import io.airbyte.cdk.read.DefaultJdbcUnsplittableSnapshotPartition
import io.airbyte.cdk.read.DefaultJdbcUnsplittableSnapshotWithCursorPartition
import io.airbyte.cdk.read.DefaultUnsplittableJdbcCursorIncrementalPartition
import io.airbyte.cdk.read.JdbcPartitionFactory
import io.airbyte.cdk.read.SelectQueryGenerator
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton

private val log = KotlinLogging.logger {}

/**
 * [JdbcPartitionFactory] for BigQuery: the toolkit's [DefaultJdbcPartitionFactory] with support for
 * the state persisted by the legacy `source-bigquery` connector ([BigQueryLegacyStreamState]).
 *
 * Partitions, queries and the emitted state (`{"primary_key": {...}, "cursors": {...}}`) are the
 * toolkit defaults. A legacy state value is translated on the fly into the equivalent cursor
 * incremental partition, so that connections migrated from the legacy connector resume where it
 * stopped instead of re-reading every table. As in the legacy connector, the resumed query is
 * `WHERE cursor > <legacy cursor>`.
 */
@Singleton
@Primary
class BigQueryJdbcPartitionFactory(
    private val default: DefaultJdbcPartitionFactory,
    override val sharedState: DefaultJdbcSharedState,
    private val handler: CatalogValidationFailureHandler,
    private val selectQueryGenerator: SelectQueryGenerator,
) : JdbcPartitionFactory<DefaultJdbcSharedState, DefaultJdbcStreamState, DefaultJdbcPartition> {

    override fun streamState(streamFeedBootstrap: StreamFeedBootstrap): DefaultJdbcStreamState =
        default.streamState(streamFeedBootstrap)

    override fun split(
        unsplitPartition: DefaultJdbcPartition,
        opaqueStateValues: List<OpaqueStateValue>
    ): List<DefaultJdbcPartition> = default.split(unsplitPartition, opaqueStateValues)

    override fun create(streamFeedBootstrap: StreamFeedBootstrap): DefaultJdbcPartition? {
        val legacy: BigQueryLegacyStreamState =
            BigQueryLegacyStreamState.parseOrNull(streamFeedBootstrap.currentState)
                ?: return default.create(streamFeedBootstrap)
        val stream: Stream = streamFeedBootstrap.feed
        val streamState: DefaultJdbcStreamState = streamState(streamFeedBootstrap)
        log.info {
            "Stream '${stream.label}' has a state persisted by the legacy source-bigquery " +
                "connector: cursor_field=${legacy.cursorField}, cursor=${legacy.cursor}."
        }
        val cursor: EmittedField? = stream.configuredCursor as? EmittedField
        if (stream.configuredSyncMode != ConfiguredSyncMode.INCREMENTAL || cursor == null) {
            // Legacy full refresh syncs had no state; whatever this is, start over.
            return coldStart(streamState)
        }
        if (legacy.cursorField != listOf(cursor.id)) {
            handler.accept(InvalidCursor(stream.id, legacy.cursorField.toString()))
            return resetAndColdStart(streamState)
        }
        val cursorCheckpoint: JsonNode =
            BigQueryLegacyStreamState.cursorValue(cursor, legacy.cursor)
                ?: run {
                    log.warn {
                        "Legacy cursor value '${legacy.cursor}' of '${stream.label}' cannot be " +
                            "interpreted as ${cursor.type.airbyteSchemaType}."
                    }
                    return resetAndColdStart(streamState)
                }
        log.info { "Resuming '${stream.label}' after legacy cursor value $cursorCheckpoint." }
        return DefaultUnsplittableJdbcCursorIncrementalPartition(
            selectQueryGenerator,
            streamState,
            cursor,
            cursorLowerBound = cursorCheckpoint,
            isLowerBoundIncluded = false,
            explicitCursorUpperBound = streamState.cursorUpperBound,
        )
    }

    private fun resetAndColdStart(streamState: DefaultJdbcStreamState): DefaultJdbcPartition {
        handler.accept(ResetStream(streamState.stream.id))
        streamState.reset()
        return coldStart(streamState)
    }

    /** Same as the private `DefaultJdbcPartitionFactory.coldStart`. */
    private fun coldStart(streamState: DefaultJdbcStreamState): DefaultJdbcPartition {
        val stream: Stream = streamState.stream
        val pkChosenFromCatalog: List<EmittedField> = stream.configuredPrimaryKey ?: listOf()
        val cursorChosenFromCatalog: EmittedField? = stream.configuredCursor as? EmittedField
        if (
            stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH ||
                cursorChosenFromCatalog == null
        ) {
            if (pkChosenFromCatalog.isEmpty()) {
                return DefaultJdbcUnsplittableSnapshotPartition(selectQueryGenerator, streamState)
            }
            return DefaultJdbcSplittableSnapshotPartition(
                selectQueryGenerator,
                streamState,
                pkChosenFromCatalog,
                lowerBound = null,
                upperBound = null,
            )
        }
        if (pkChosenFromCatalog.isEmpty()) {
            return DefaultJdbcUnsplittableSnapshotWithCursorPartition(
                selectQueryGenerator,
                streamState,
                cursorChosenFromCatalog,
            )
        }
        return DefaultJdbcSplittableSnapshotWithCursorPartition(
            selectQueryGenerator,
            streamState,
            pkChosenFromCatalog,
            lowerBound = null,
            upperBound = null,
            cursorChosenFromCatalog,
            cursorUpperBound = null,
        )
    }
}
