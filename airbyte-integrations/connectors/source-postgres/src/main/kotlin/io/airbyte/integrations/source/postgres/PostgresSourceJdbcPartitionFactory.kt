package io.airbyte.integrations.source.postgres

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.FieldOrMetaField
import io.airbyte.cdk.output.CatalogValidationFailureHandler
import io.airbyte.cdk.output.InvalidCursor
import io.airbyte.cdk.output.ResetStream
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.DefaultJdbcSharedState
import io.airbyte.cdk.read.DefaultJdbcStreamState
import io.airbyte.cdk.read.DefaultJdbcStreamStateValue
import io.airbyte.cdk.read.JdbcPartitionFactory
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.airbyte.integrations.source.postgres.ctid.Ctid
import io.airbyte.integrations.source.postgres.operations.PostgresSourceSelectQueryGenerator
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

@Primary
@Singleton
class PostgresSourceJdbcPartitionFactory(
    override val sharedState: DefaultJdbcSharedState,
    val selectQueryGenerator: PostgresSourceSelectQueryGenerator,
    val config: PostgresSourceConfiguration,
    val handler: CatalogValidationFailureHandler,
) : JdbcPartitionFactory<DefaultJdbcSharedState, DefaultJdbcStreamState, PostgresSourceJdbcPartition> {
    private val streamStates = ConcurrentHashMap<StreamIdentifier, DefaultJdbcStreamState>()

    override fun streamState(streamFeedBootstrap: StreamFeedBootstrap): DefaultJdbcStreamState =
        streamStates.getOrPut(streamFeedBootstrap.feed.id) {
            DefaultJdbcStreamState(sharedState, streamFeedBootstrap)
        }

    private fun coldStart(streamState: DefaultJdbcStreamState): PostgresSourceJdbcPartition {
        val stream: Stream = streamState.stream
        if (stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH || config.global) {
            return PostgresSourceJdbcSplittableSnapshotPartition(
                selectQueryGenerator,
                streamState,
                lowerBound = null,
                upperBound = null,
            )
        }
        val cursorChosenFromCatalog: Field =
            stream.configuredCursor as? Field ?: throw ConfigErrorException("no cursor")
        return PostgresSourceJdbcSplittableSnapshotWithCursorPartition(
            selectQueryGenerator,
            streamState,
            lowerBound = null,
            upperBound = null,
            cursorChosenFromCatalog,
            cursorUpperBound = null,
        )



    }

    override fun create(streamFeedBootstrap: StreamFeedBootstrap): PostgresSourceJdbcPartition? {
        val stream: Stream = streamFeedBootstrap.feed
        val streamState: DefaultJdbcStreamState = streamState(streamFeedBootstrap)
        val opaqueStateValue: OpaqueStateValue? = streamFeedBootstrap.currentState

        // An empty table stream state will be marked as a nullNode. This prevents repeated attempt
        // to read it
        if (opaqueStateValue?.isNull == true) { // TODO: check empty table
            return null
        }

        if (opaqueStateValue == null) {
            return coldStart(streamState)
        }

        val sv: PostgresSourceJdbcStreamStateValue =
            Jsons.treeToValue(opaqueStateValue, PostgresSourceJdbcStreamStateValue::class.java)

        val ctidVal: Ctid? = sv.ctid?.let { Ctid(it) }

        val cursorPair: Pair<Field, JsonNode>? =
            if (sv.cursors.isEmpty()) {
                null
            } else {
                sv.cursorPair(stream)
                    ?: run {
                        handler.accept(ResetStream(stream.id))
                        streamState.reset()
                        return coldStart(streamState)
                    }
            }

        val isCursorBasedIncremental: Boolean =
            stream.configuredSyncMode == ConfiguredSyncMode.INCREMENTAL && !config.global

        return if (cursorPair == null) {
            if (isCursorBasedIncremental) {
                handler.accept(ResetStream(stream.id))
                streamState.reset()
                coldStart(streamState)
            } else if (ctidVal == null) {
                // Snapshot complete
                null
            } else {
                // Snapshot ongoing
                PostgresSourceJdbcSplittableSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                    lowerBound = listOf(Jsons.textNode(ctidVal.toString())),
                    upperBound = null,
                )
            }
        } else {
            val (cursor: Field, cursorCheckpoint: JsonNode) = cursorPair
            if (!isCursorBasedIncremental) {
                handler.accept(ResetStream(stream.id))
                streamState.reset()
                coldStart(streamState)
            } else if (ctidVal != null) {
                // Snapshot ongoing
                PostgresSourceJdbcSplittableSnapshotWithCursorPartition(
                    selectQueryGenerator,
                    streamState,
                    lowerBound = listOf(Jsons.textNode(ctidVal.toString())),
                    upperBound = null,
                    cursor,
                    cursorCheckpoint
                )
            } else if (cursorCheckpoint == streamState.cursorUpperBound) {
                // Incremental complete
                null
            } else {
                // Incremental ongoing
                PostgresSourceJdbcCursorIncrementalPartition(
                    selectQueryGenerator,
                    streamState,
                    cursor,
                    cursorLowerBound = cursorCheckpoint,
                    isLowerBoundIncluded = true,
                    cursorUpperBound = streamState.cursorUpperBound
                )
            }
        }
    }

    private fun PostgresSourceJdbcStreamStateValue.cursorPair(stream: Stream): Pair<Field, JsonNode>? {
        if (cursors.size > 1) {
            handler.accept(
                InvalidCursor(stream.id, cursors.keys.toString()),
            )
            return null
        }
        val cursorLabel: String = cursors.keys.first()
        val cursor: FieldOrMetaField? = stream.schema.find { it.id == cursorLabel }
        if (cursor !is Field) {
            handler.accept(
                InvalidCursor(stream.id, cursorLabel),
            )
            return null
        }
        if (stream.configuredCursor != cursor) {
            handler.accept(
                InvalidCursor(stream.id, cursorLabel),
            )
            return null
        }
        return cursor to cursors[cursorLabel]!!
    }

    override fun split(
        unsplitPartition: PostgresSourceJdbcPartition,
        opaqueStateValues: List<OpaqueStateValue>
    ): List<PostgresSourceJdbcPartition> {
        val splitPartitionBoundaries: List<PostgresSourceJdbcStreamStateValue> by lazy {
            opaqueStateValues.map { Jsons.treeToValue(it, PostgresSourceJdbcStreamStateValue::class.java) }
        }

        return when (unsplitPartition) {
            is PostgresSourceJdbcSplittableSnapshotPartition -> unsplitPartition.split(splitPartitionBoundaries)
            is PostgresSourceJdbcSplittableSnapshotWithCursorPartition -> unsplitPartition.split(splitPartitionBoundaries)
            else -> listOf(unsplitPartition)
        }
    }

    private fun PostgresSourceJdbcSplittableSnapshotPartition.split(
        splitPointValues: List<PostgresSourceJdbcStreamStateValue>
    ): List<PostgresSourceJdbcSplittableSnapshotPartition> {
        val inners: List<Ctid> =
            splitPointValues.map { Ctid(it.ctid!!) }
        val lbCtid: Ctid?  = lowerBound?.let { if (it.isNotEmpty()) { Ctid.of(it[0].asText()) } else null }
        val ubCtid: Ctid?  = upperBound?.let { if (it.isNotEmpty()) { Ctid.of(it[0].asText()) } else null }
        val lbs: List<Ctid?> = listOf(lbCtid) + inners
        val ubs: List<Ctid?> = inners + listOf(ubCtid)
        return lbs.zip(ubs).map { (lowerBound, upperBound) ->
            PostgresSourceJdbcSplittableSnapshotPartition(
                selectQueryGenerator,
                streamState,
                lowerBound?.let { listOf(Jsons.textNode(it.toString())) },
                upperBound?.let { listOf(Jsons.textNode(it.toString())) }
            )
        }
    }

    private fun PostgresSourceJdbcSplittableSnapshotWithCursorPartition.split(
        splitPointValues: List<PostgresSourceJdbcStreamStateValue>
    ): List<PostgresSourceJdbcSplittableSnapshotWithCursorPartition> {
        val inners: List<Ctid> =
            splitPointValues.map { Ctid(it.ctid!!) }
        val lbCtid: Ctid?  = lowerBound?.let { if (it.isNotEmpty()) { Ctid.of(it[0].asText()) } else null }
        val ubCtid: Ctid?  = upperBound?.let { if (it.isNotEmpty()) { Ctid.of(it[0].asText()) } else null }
        val lbs: List<Ctid?> = listOf(lbCtid) + inners
        val ubs: List<Ctid?> = inners + listOf(ubCtid)
        return lbs.zip(ubs).map { (lowerBound, upperBound) ->
            PostgresSourceJdbcSplittableSnapshotWithCursorPartition(
                selectQueryGenerator,
                streamState,
                lowerBound?.let { listOf(Jsons.textNode(it.toString())) },
                upperBound?.let { listOf(Jsons.textNode(it.toString())) },
                cursor,
                cursorUpperBound
            )
        }
    }

}
