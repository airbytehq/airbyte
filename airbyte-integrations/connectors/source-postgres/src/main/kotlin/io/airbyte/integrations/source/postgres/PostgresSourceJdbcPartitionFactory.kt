/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.DataField
import io.airbyte.cdk.discover.DataOrMetaField
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.JdbcFieldType
import io.airbyte.cdk.jdbc.LongFieldType
import io.airbyte.cdk.output.CatalogValidationFailureHandler
import io.airbyte.cdk.output.InvalidCursor
import io.airbyte.cdk.output.InvalidPrimaryKey
import io.airbyte.cdk.output.ResetStream
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.DefaultJdbcSharedState
import io.airbyte.cdk.read.DefaultJdbcStreamState
import io.airbyte.cdk.read.JdbcPartitionFactory
import io.airbyte.cdk.read.JdbcStreamState
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.postgres.PostgresSourceJdbcPartitionFactory.FilenodeChangeType.FILENODE_CHANGED
import io.airbyte.integrations.source.postgres.PostgresSourceJdbcPartitionFactory.FilenodeChangeType.FILENODE_NEW_STREAM
import io.airbyte.integrations.source.postgres.PostgresSourceJdbcPartitionFactory.FilenodeChangeType.FILENODE_NOT_FOUND
import io.airbyte.integrations.source.postgres.PostgresSourceJdbcPartitionFactory.FilenodeChangeType.FILENODE_NO_CHANGE
import io.airbyte.integrations.source.postgres.PostgresSourceJdbcPartitionFactory.FilenodeChangeType.NO_FILENODE
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.airbyte.integrations.source.postgres.ctid.Ctid
import io.airbyte.integrations.source.postgres.operations.PostgresSourceSelectQueryGenerator
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.sql.PreparedStatement
import java.util.concurrent.ConcurrentHashMap

@Primary
@Singleton
class PostgresSourceJdbcPartitionFactory(
    override val sharedState: DefaultJdbcSharedState,
    val selectQueryGenerator: PostgresSourceSelectQueryGenerator,
    val config: PostgresSourceConfiguration,
    val handler: CatalogValidationFailureHandler,
) :
    JdbcPartitionFactory<
        DefaultJdbcSharedState,
        PostgresSourceJdbcStreamState,
        PostgresSourceJdbcPartition,
    > {
    private val streamStates = ConcurrentHashMap<StreamIdentifier, PostgresSourceJdbcStreamState>()

    override fun streamState(
        streamFeedBootstrap: StreamFeedBootstrap
    ): PostgresSourceJdbcStreamState =
        streamStates.getOrPut(streamFeedBootstrap.feed.id) {
            PostgresSourceJdbcStreamState(DefaultJdbcStreamState(sharedState, streamFeedBootstrap))
        }

    private fun coldStart(
        streamState: PostgresSourceJdbcStreamState,
        filenode: Filenode?
    ): PostgresSourceJdbcPartition {
        val stream: Stream = streamState.stream
        if (stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH || config.global) {
            return filenode?.let {
                PostgresSourceJdbcSplittableSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                    lowerBound = null,
                    upperBound = null,
                    filenode,
                    false
                )
            }
                ?: PostgresSourceJdbcUnsplittableSnapshotPartition(
                    selectQueryGenerator,
                    streamState
                )
        }
        val cursorChosenFromCatalog: DataField =
            stream.configuredCursor as? DataField ?: throw ConfigErrorException("no cursor")
        return filenode?.let {
            PostgresSourceJdbcSplittableSnapshotWithCursorPartition(
                selectQueryGenerator,
                streamState,
                lowerBound = null,
                upperBound = null,
                cursorChosenFromCatalog,
                cursorUpperBound = null,
                filenode,
                false
            )
        }
            ?: PostgresSourceJdbcUnsplittableSnapshotWithCursorPartition(
                selectQueryGenerator,
                streamState,
                cursorChosenFromCatalog,
            )
    }

    val tidRangeScanCapableDBServer: Boolean by
        lazy(mode = LazyThreadSafetyMode.SYNCHRONIZED) {
            isTidRangeScanCapableDBServer(JdbcConnectionFactory(config))
        }

    override fun create(streamFeedBootstrap: StreamFeedBootstrap): PostgresSourceJdbcPartition? {
        val stream: Stream = streamFeedBootstrap.feed
        val streamState: PostgresSourceJdbcStreamState = streamState(streamFeedBootstrap)
        val opaqueStateValue: OpaqueStateValue? = streamFeedBootstrap.currentState

        // An empty table stream state will be marked as a nullNode. This prevents repeated attempt
        // to read it
        if (opaqueStateValue?.isNull == true) {
            return null
        }

        val filenode: Filenode? =
            when (tidRangeScanCapableDBServer) {
                true -> getStreamFilenode(streamState)
                false -> null
            }
        val fileNodeChange: FilenodeChangeType = detectStreamFilenodeChange(streamState, filenode)

        if (opaqueStateValue == null) {
            return coldStart(streamState, filenode)
        }

        val sv: PostgresSourceJdbcStreamStateValue = streamState.stateValue!!

        val cursorPair: Pair<DataField, JsonNode>? =
            if (sv.cursors.isEmpty()) {
                null
            } else {
                sv.cursorPair(stream)
                    ?: run {
                        handler.accept(ResetStream(stream.id))
                        streamState.reset()
                        return coldStart(streamState, filenode)
                    }
            }

        val isCursorBasedIncremental: Boolean =
            stream.configuredSyncMode == ConfiguredSyncMode.INCREMENTAL && !config.global

        return if (cursorPair == null) {
            if (isCursorBasedIncremental) {
                handler.accept(ResetStream(stream.id))
                streamState.reset()
                coldStart(streamState, filenode)
            } else if (streamState.maybeCtid == null) {
                // Snapshot complete
                null
            } else {
                // Snapshot ongoing
                if (fileNodeChange != FILENODE_NO_CHANGE) { // TODO: need other values? new stream
                    handler.accept(InvalidPrimaryKey(stream.id, listOf(ctidField.id)))
                    streamState.reset()
                    coldStart(streamState, filenode)
                } else {
                    PostgresSourceJdbcSplittableSnapshotPartition(
                        selectQueryGenerator,
                        streamState,
                        lowerBound = Jsons.textNode(streamState.maybeCtid!!.toString()),
                        upperBound = null,
                        filenode,
                        true
                    )
                }
            }
        } else {
            val (cursor: DataField, cursorCheckpoint: JsonNode) = cursorPair
            if (
                !isCursorBasedIncremental ||
                    fileNodeChange !in
                        listOf(
                            FILENODE_NO_CHANGE,
                            NO_FILENODE,
                            FILENODE_NEW_STREAM,
                        )
            ) {
                handler.accept(ResetStream(stream.id))
                streamState.reset()
                coldStart(streamState, filenode)
            } else if (streamState.maybeCtid != null) {
                // Snapshot ongoing
                PostgresSourceJdbcSplittableSnapshotWithCursorPartition(
                    selectQueryGenerator,
                    streamState,
                    lowerBound = Jsons.textNode(streamState.maybeCtid.toString()),
                    upperBound = null,
                    cursor,
                    cursorCheckpoint,
                    filenode,
                    true
                )
            } else if (cursorCheckpoint == streamState.cursorUpperBound) {
                // Incremental complete
                null
            } else {
                filenode?.let { // Incremental ongoing
                    PostgresSourceJdbcCursorIncrementalPartition(
                        selectQueryGenerator,
                        streamState,
                        cursor,
                        cursorLowerBound = cursorCheckpoint,
                        isLowerBoundIncluded = true,
                        cursorUpperBound = streamState.cursorUpperBound,
                    )
                }
                    ?: PostgresSourceJdbcUnsplittableCursorIncrementalPartition(
                        selectQueryGenerator,
                        streamState,
                        cursor,
                        cursorLowerBound = cursorCheckpoint,
                        isLowerBoundIncluded = true,
                        explicitCursorUpperBound = streamState.cursorUpperBound,
                    )
            }
        }
    }

    enum class FilenodeChangeType {
        NO_FILENODE,
        FILENODE_NOT_FOUND,
        FILENODE_NEW_STREAM,
        FILENODE_CHANGED,
        FILENODE_NO_CHANGE,
    }

    private fun getStreamFilenode(streamState: JdbcStreamState<*>): Filenode? {
        return getStreamFilenode(streamState, JdbcConnectionFactory(config))
    }

    companion object {
        private val log = KotlinLogging.logger {}
        fun getStreamFilenode(
            streamState: JdbcStreamState<*>,
            jdbcConnectionFactory: JdbcConnectionFactory
        ): Filenode? {
            log.info { "Querying filenode for stream ${streamState.stream.id}" }
            jdbcConnectionFactory.get().use { connection ->
                val sql =
                    """SELECT pg_relation_filenode('"${streamState.stream.namespace}"."${streamState.stream.name}"')"""
                val stmt: PreparedStatement = connection.prepareStatement(sql)
                val rs = stmt.executeQuery()
                if (rs.next()) {
                    val jdbcFieldType: JdbcFieldType<*> = LongFieldType
                    val filenode: Any? = jdbcFieldType.jdbcGetter.get(rs, 1)
                    log.info { "Found filenode: $filenode" }
                    return filenode as? Filenode
                } else {
                    log.info { "filenode not found" }
                }
                return null
            }
        }

        const val POSTGRESQL_VERSION_TID_RANGE_SCAN_CAPABLE: Int = 14
        fun isTidRangeScanCapableDBServer(jdbcConnectionFactory: JdbcConnectionFactory): Boolean {
            jdbcConnectionFactory.get().use { connection ->
                try {
                    return connection.metaData.databaseMajorVersion >=
                        POSTGRESQL_VERSION_TID_RANGE_SCAN_CAPABLE
                } catch (e: Exception) {
                    log.error(e) { "Failed to get database major version" }
                    return true
                }
            }
        }
    }

    private fun detectStreamFilenodeChange(
        streamState: PostgresSourceJdbcStreamState,
        filenode: Filenode?
    ): FilenodeChangeType =
        when {
            // No filenode - a view?
            streamState.maybeFilenode == null && filenode == null -> NO_FILENODE
            // New stream - filenode assigned
            streamState.maybeFilenode == null -> FILENODE_NEW_STREAM
            // Existing stream - filenode disappeared
            filenode == null -> FILENODE_NOT_FOUND
            // Existing stream - filenode changed. Must start over reading from ctid (0,0)
            streamState.maybeFilenode != filenode -> FILENODE_CHANGED
            // filenode unchanged - all good
            else -> FILENODE_NO_CHANGE
        }
    private fun PostgresSourceJdbcStreamStateValue.cursorPair(
        stream: Stream
    ): Pair<DataField, JsonNode>? {
        if (cursors.size > 1) {
            handler.accept(
                InvalidCursor(stream.id, cursors.keys.toString()),
            )
            return null
        }
        val cursorLabel: String = cursors.keys.first()
        val cursor: DataOrMetaField? = stream.schema.find { it.id == cursorLabel }
        if (cursor !is DataField) {
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

    val blockSize: Long by lazy(mode = LazyThreadSafetyMode.SYNCHRONIZED) {
        val jdbcConnectionFactory = JdbcConnectionFactory(config)
        jdbcConnectionFactory.get().use { connection ->
            val sql = "SELECT current_setting('block_size')::int"
            val stmt = connection.prepareStatement(sql)
            val rs = stmt.executeQuery()

            if (rs.next()) {
                val blockSize = rs.getLong(1)
                return@lazy blockSize
            }
            error("Could not get server block size")
        }
    }

    override fun split(
        unsplitPartition: PostgresSourceJdbcPartition,
        opaqueStateValues: List<OpaqueStateValue>
    ): List<PostgresSourceJdbcPartition> {
        val splitPartitionBoundaries: List<PostgresSourceJdbcStreamStateValue> by lazy {
            opaqueStateValues.map {
                Jsons.treeToValue(it, PostgresSourceJdbcStreamStateValue::class.java)
            }
        }

        val relationSize =
            PostgresSourceJdbcConcurrentPartitionsCreator.streamSizes[unsplitPartition.stream] ?: error("Could not get stream size for stream ${unsplitPartition.stream.id}")

        val rowSize: Long = PostgresSourceJdbcConcurrentPartitionsCreator.rowSizes[unsplitPartition.stream] ?: error("Could not get row size for stream ${unsplitPartition.stream.id}")

        return when (unsplitPartition) {
            is PostgresSourceJdbcSplittableSnapshotPartition ->
                unsplitPartition.split(splitPartitionBoundaries.size, splitPartitionBoundaries.first().filenode, relationSize, rowSize)
            is PostgresSourceJdbcSplittableSnapshotWithCursorPartition ->
                unsplitPartition.split(splitPartitionBoundaries.size, splitPartitionBoundaries.first().filenode, relationSize, rowSize)
            // TODO: implement split for cursor incremental partition
            else -> listOf(unsplitPartition)
        }
    }

    private fun computePartitionBounds(
        lowerBound: JsonNode?,
        numPartitions: Int,
        relationSize: Long,
        rowSize: Long
    ): List<Pair<Ctid?, Ctid?>> {
        val theoreticalLastPage: Long = relationSize / rowSize
        log.info { "Theoretical last page: $theoreticalLastPage" }
        val lowerBoundCtid: Ctid = lowerBound?.let {
            if (it.isNull.not() && it.asText().isEmpty().not()) {
                Ctid.of(it.asText())
            } else null
        } ?: Ctid.ZERO
        val eachStep: Long = ((theoreticalLastPage - lowerBoundCtid.page) / numPartitions).coerceAtLeast(1)
        val lbs: List<Ctid?> = listOf(lowerBoundCtid) + (1 ..< numPartitions).map {
            Ctid(lowerBoundCtid.page + eachStep * it, 1)
        }
        val ubs: List<Ctid?> = lbs.drop(1) + listOf(null)

        return lbs.zip(ubs)
    }

    private fun PostgresSourceJdbcSplittableSnapshotPartition.split(
        numPartitions: Int,
        filenode: Filenode?,
        relationSize: Long,
        rowSize: Long
    ): List<PostgresSourceJdbcSplittableSnapshotPartition> {
        val bounds = computePartitionBounds(lowerBound, numPartitions, relationSize, rowSize)

        return bounds.mapIndexed { index, (lowerBound, upperBound) ->
            PostgresSourceJdbcSplittableSnapshotPartition(
                selectQueryGenerator,
                streamState,
                lowerBound?.let { Jsons.textNode(it.toString()) },
                upperBound?.let { Jsons.textNode(it.toString()) },
                filenode,
                // The first partition includes the lower bound
                index == 0
            )
        }
    }

    private fun PostgresSourceJdbcSplittableSnapshotWithCursorPartition.split(
        numPartitions: Int,
        filenode: Filenode?,
        relationSize: Long,
        rowSize: Long
    ): List<PostgresSourceJdbcSplittableSnapshotWithCursorPartition> {
        val bounds = computePartitionBounds(lowerBound, numPartitions, relationSize, rowSize)

        return bounds.mapIndexed { index, (lowerBound, upperBound) ->
            PostgresSourceJdbcSplittableSnapshotWithCursorPartition(
                selectQueryGenerator,
                streamState,
                lowerBound?.let { Jsons.textNode(it.toString()) },
                upperBound?.let { Jsons.textNode(it.toString()) },
                cursor,
                cursorUpperBound,
                filenode,
                // The first partition includes the lower bound
                index == 0
            )
        }
    }
}
