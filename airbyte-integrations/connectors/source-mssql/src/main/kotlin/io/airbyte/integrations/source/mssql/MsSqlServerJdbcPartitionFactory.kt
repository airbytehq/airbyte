/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.JdbcFieldType
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.DefaultJdbcSharedState
import io.airbyte.cdk.read.DefaultJdbcStreamState
import io.airbyte.cdk.read.From
import io.airbyte.cdk.read.JdbcPartitionFactory
import io.airbyte.cdk.read.SelectColumnMaxValue
import io.airbyte.cdk.read.SelectQuerySpec
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.cdk.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import java.time.format.DateTimeFormatter
import java.time.format.DateTimeFormatterBuilder
import java.time.temporal.ChronoField
import java.util.concurrent.ConcurrentHashMap
import javax.inject.Singleton

@Primary
@Singleton
class MsSqlServerJdbcPartitionFactory(
    override val sharedState: DefaultJdbcSharedState,
    val selectQueryGenerator: MsSqlSourceOperations,
    val config: MsSqlServerSourceConfiguration,
    val metadataQuerierFactory: MsSqlSourceMetadataQuerier.Factory,
) :
    JdbcPartitionFactory<
        DefaultJdbcSharedState,
        DefaultJdbcStreamState,
        MsSqlServerJdbcPartition,
    > {
    private val log = KotlinLogging.logger {}

    private val metadataQuerier: MsSqlSourceMetadataQuerier by lazy {
        metadataQuerierFactory.session(config) as MsSqlSourceMetadataQuerier
    }

    private val streamStates = ConcurrentHashMap<StreamIdentifier, DefaultJdbcStreamState>()

    override fun streamState(streamFeedBootstrap: StreamFeedBootstrap): DefaultJdbcStreamState =
        streamStates.getOrPut(streamFeedBootstrap.feed.id) {
            DefaultJdbcStreamState(sharedState, streamFeedBootstrap)
        }

    /** Detects if a stream corresponds to a SQL Server VIEW (vs a TABLE) */
    private fun isView(stream: Stream): Boolean {
        val tableName = metadataQuerier.findTableName(stream.id) ?: return false
        return tableName.type.equals("VIEW", ignoreCase = true)
    }

    /**
     * Returns the ordered column (from clustered index or PK) as a single-element list, or null if
     * no ordered column is available. This is used for resumable partitioning.
     */
    private fun getOrderedColumnAsList(stream: Stream): List<Field>? {
        val orderedColumnName = metadataQuerier.getOrderedColumnForSync(stream.id) ?: return null
        val orderedColumn = stream.fields.find { it.id == orderedColumnName } ?: return null
        return listOf(orderedColumn)
    }

    private fun findPkUpperBound(stream: Stream): JsonNode {
        // find upper bound using maxPk query
        // Use the ordered column for sync (prefers clustered index for SQL Server performance)
        val orderedColumnName = metadataQuerier.getOrderedColumnForSync(stream.id)!!
        val orderedColumnForSync = stream.fields.find { it.id == orderedColumnName }!!

        val jdbcConnectionFactory = JdbcConnectionFactory(config)
        val from = From(stream.name, stream.namespace)
        val maxPkQuery = SelectQuerySpec(SelectColumnMaxValue(orderedColumnForSync), from)

        jdbcConnectionFactory.get().use { connection ->
            val stmt = connection.prepareStatement(selectQueryGenerator.generate(maxPkQuery).sql)
            val rs = stmt.executeQuery()

            if (rs.next()) {
                val jdbcFieldType = orderedColumnForSync.type as JdbcFieldType<*>
                val pkUpperBound: JsonNode = jdbcFieldType.get(rs, 1)
                return pkUpperBound
            } else {
                // Table might be empty thus there is no max PK value.
                return Jsons.nullNode()
            }
        }
    }

    private fun coldStart(streamState: DefaultJdbcStreamState): MsSqlServerJdbcPartition {
        val stream: Stream = streamState.stream
        val isView = isView(stream)
        val orderedColumns = getOrderedColumnAsList(stream)

        if (stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH) {
            if (isView || orderedColumns == null) {
                return MsSqlServerJdbcNonResumableSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                )
            }

            val upperBound = findPkUpperBound(stream)
            return if (sharedState.configuration.global) {
                MsSqlServerJdbcCdcRfrSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                    orderedColumns,
                    lowerBound = null,
                    upperBound = listOf(upperBound),
                )
            } else {
                MsSqlServerJdbcRfrSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                    orderedColumns,
                    lowerBound = null,
                    upperBound = listOf(upperBound),
                )
            }
        }

        if (sharedState.configuration.global) {
            // CDC mode: try to use ordered column for resumable snapshots
            if (isView || orderedColumns == null) {
                return MsSqlServerJdbcNonResumableSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                )
            }
            return MsSqlServerJdbcCdcSnapshotPartition(
                selectQueryGenerator,
                streamState,
                orderedColumns,
                lowerBound = null,
            )
        }

        val cursorChosenFromCatalog: Field =
            stream.configuredCursor as? Field ?: throw ConfigErrorException("no cursor")

        // Calculate cutoff time for cursor if exclude today's data is enabled
        val cursorCutoffTime = getCursorCutoffTime(cursorChosenFromCatalog)

        // Views can't be sampled with TABLESAMPLE, so use non-resumable partitions
        // which skip the sampling step entirely
        if (isView || orderedColumns == null) {
            return MsSqlServerJdbcNonResumableSnapshotWithCursorPartition(
                selectQueryGenerator,
                streamState,
                cursorChosenFromCatalog,
                cursorCutoffTime = cursorCutoffTime,
            )
        }

        return MsSqlServerJdbcSnapshotWithCursorPartition(
            selectQueryGenerator,
            streamState,
            orderedColumns,
            lowerBound = null,
            cursorChosenFromCatalog,
            cursorUpperBound = null,
            cursorCutoffTime = cursorCutoffTime,
        )
    }

    /**
     * Flowchart:
     * 1. If the input state is null - using coldstart.
     * ```
     *    a. If it's global but without PK, use non-resumable snapshot.
     *    b. If it's global with PK, use CDC snapshot.
     *    c. If it's not global, use snapshot with cursor.
     * ```
     * 2. If the input state is not null -
     * ```
     *    a. If it's in global mode:
     *       i. JdbcPartitionFactory handles the initial CDC snapshot phase (resuming incomplete snapshots)
     *       ii. CdcPartitionsCreator (in CDK) handles CDC incremental reads after snapshot completes
     *    b. If it's cursor based, it could be either in PK read phase (initial read) or
     *       cursor read phase (incremental read). This is determined by checking if pk_name is set.
     *      i. In PK read phase (pk_name != null), use snapshot with cursor. If no PKs were found,
     *         use non-resumable snapshot with cursor.
     *      ii. In cursor read phase (pk_name == null), use cursor incremental.
     * ```
     */
    override fun create(streamFeedBootstrap: StreamFeedBootstrap): MsSqlServerJdbcPartition? {
        val stream: Stream = streamFeedBootstrap.feed
        val streamState: DefaultJdbcStreamState = streamState(streamFeedBootstrap)
        val opaqueStateValue: OpaqueStateValue? = streamFeedBootstrap.currentState

        // An empty table or table with all NULL cursor values will be marked as a nullNode.
        // This prevents repeated attempts to read it
        if (opaqueStateValue?.isNull == true) {
            return null
        }

        if (opaqueStateValue == null) {
            return coldStart(streamState)
        }

        val isCursorBased: Boolean = !sharedState.configuration.global
        val isView = isView(stream)
        val orderedColumns = getOrderedColumnAsList(stream)

        // Views cannot use TABLESAMPLE, so use non-resumable partitions
        if (
            stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH &&
                (isView || orderedColumns == null)
        ) {
            return handleFullRefreshWithoutPk(streamState)
        }

        // CDC sync
        if (!isCursorBased) {
            val sv: MsSqlServerCdcInitialSnapshotStateValue =
                Jsons.treeToValue(
                    opaqueStateValue,
                    MsSqlServerCdcInitialSnapshotStateValue::class.java
                )

            if (stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH) {
                val upperBound = findPkUpperBound(stream)
                if (sv.pkVal == upperBound.asText()) {
                    return null
                }
                val pkLowerBound: JsonNode =
                    stateValueToJsonNode(orderedColumns!!.first(), sv.pkVal)

                return MsSqlServerJdbcCdcRfrSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                    orderedColumns,
                    lowerBound = if (pkLowerBound.isNull) null else listOf(pkLowerBound),
                    upperBound = listOf(upperBound),
                )
            }

            if (sv.pkName == null) {
                // This indicates initial snapshot has been completed. CDC snapshot will be handled
                // by CDCPartitionFactory.
                // Nothing to do here.
                return null
            } else {
                // This branch indicates snapshot is incomplete. We need to resume based on previous
                // snapshot state.
                // Views cannot use TABLESAMPLE, so use non-resumable partitions
                if (isView || orderedColumns == null) {
                    log.warn {
                        "Stream ${stream.name} ${if (isView) "is a view" else "has no PK or clustered index"}. Using non-resumable CDC snapshot."
                    }
                    return MsSqlServerJdbcNonResumableSnapshotPartition(
                        selectQueryGenerator,
                        streamState,
                    )
                }
                val pkLowerBound: JsonNode = stateValueToJsonNode(orderedColumns.first(), sv.pkVal)

                return MsSqlServerJdbcCdcSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                    orderedColumns,
                    listOf(pkLowerBound),
                )
            }
        } else { // Cursor-based sync
            val sv: MsSqlServerJdbcStreamStateValue =
                MsSqlServerStateMigration.parseStateValue(opaqueStateValue)

            if (stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH) {
                val upperBound = findPkUpperBound(stream)
                val pkLowerBound: JsonNode =
                    extractPkLowerBound(sv.pkValue, orderedColumns!!.first())

                if (!pkLowerBound.isNull && areValuesEqual(pkLowerBound, upperBound)) {
                    return null
                }

                return MsSqlServerJdbcRfrSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                    orderedColumns,
                    lowerBound = if (pkLowerBound.isNull) null else listOf(pkLowerBound),
                    upperBound = listOf(upperBound),
                )
            }

            // Resume from full refresh
            if (sv.pkName != null) {
                // Still in snapshot phase (PK read)
                val cursorChosenFromCatalog: Field =
                    stream.configuredCursor as? Field ?: throw ConfigErrorException("no cursor")

                // Views can't be sampled with TABLESAMPLE, so use non-resumable partitions
                if (isView(stream) || orderedColumns == null) {
                    return MsSqlServerJdbcNonResumableSnapshotWithCursorPartition(
                        selectQueryGenerator,
                        streamState,
                        cursorChosenFromCatalog,
                        cursorCutoffTime = getCursorCutoffTime(cursorChosenFromCatalog),
                    )
                }

                val pkLowerBound: JsonNode = extractPkLowerBound(sv.pkValue, orderedColumns.first())

                // Still in primary_key read phase (snapshot with cursor)
                return MsSqlServerJdbcSnapshotWithCursorPartition(
                    selectQueryGenerator,
                    streamState,
                    orderedColumns,
                    lowerBound = listOf(pkLowerBound),
                    cursorChosenFromCatalog,
                    cursorUpperBound = null,
                    cursorCutoffTime = getCursorCutoffTime(cursorChosenFromCatalog),
                )
            }
            if (sv.cursorField.isEmpty()) {
                // Empty cursor_field means the state was Jsons.nullNode() (emitted when cursor is
                // NULL).
                // This indicates the sync already completed in the previous run.
                log.info {
                    "State has empty cursor_field for stream ${stream.name}, sync already complete"
                }
                return null
            }

            // Cursor read phase (incremental read)
            val cursor: Field? = stream.fields.find { it.id == sv.cursorField.first() }
            if (cursor == null) {
                log.warn {
                    "Cursor field '${sv.cursorField.first()}' not found in stream ${stream.name}, resetting stream"
                }
                streamState.reset()
                return coldStart(streamState)
            }
            // Convert cursor JsonNode to proper type (handles timestamp formatting, binary
            // decoding, etc.)
            val cursorCheckpoint: JsonNode =
                if (sv.cursor == null || sv.cursor.isNull) {
                    Jsons.nullNode()
                } else {
                    stateValueToJsonNode(cursor, sv.cursor.asText())
                }

            val upperBound = streamState.cursorUpperBound
            if (upperBound != null) {
                if (areValuesEqual(cursorCheckpoint, upperBound)) {
                    // Values are equal - incremental complete
                    return null
                }
            }
            return MsSqlServerJdbcCursorIncrementalPartition(
                selectQueryGenerator,
                streamState,
                cursor,
                cursorLowerBound = cursorCheckpoint,
                isLowerBoundIncluded = false,
                cursorUpperBound = streamState.cursorUpperBound,
                cursorCutoffTime = getCursorCutoffTime(cursor),
            )
        }
    }

    private fun handleFullRefreshWithoutPk(
        streamState: DefaultJdbcStreamState
    ): MsSqlServerJdbcPartition? {
        if (
            streamState.streamFeedBootstrap.currentState ==
                MsSqlServerJdbcStreamStateValue.snapshotCompleted
        ) {
            return null
        }
        return MsSqlServerJdbcNonResumableSnapshotPartition(
            selectQueryGenerator,
            streamState,
        )
    }

    private fun extractPkLowerBound(pkValue: JsonNode?, orderedColumnForSync: Field): JsonNode {
        return when {
            pkValue == null || pkValue.isNull -> Jsons.nullNode()
            pkValue.isTextual -> stateValueToJsonNode(orderedColumnForSync, pkValue.asText())
            else -> pkValue
        }
    }

    private fun getCursorCutoffTime(cursorField: Field): JsonNode? {
        val incrementalConfig = config.incrementalReplicationConfiguration
        return if (
            incrementalConfig is UserDefinedCursorIncrementalConfiguration &&
                incrementalConfig.excludeTodaysData &&
                MsSqlServerCursorCutoffTimeProvider.isTemporalType(
                    cursorField,
                )
        ) {
            val cutoffTime = MsSqlServerCursorCutoffTimeProvider.getCutoffTime(cursorField)
            log.info { "Using cursor cutoff time: $cutoffTime for field '${cursorField.id}'" }
            cutoffTime
        } else {
            null
        }
    }

    /**
     * Compares two JsonNode values for equality, with special handling for numeric types. This is
     * needed because NUMERIC columns may have values like "11" stored in state but retrieved as
     * "11.0" from database, and they should be considered equal.
     */
    private fun areValuesEqual(a: JsonNode, b: JsonNode): Boolean {
        // Handle numeric comparisons - compare as BigDecimal to handle 13.0 == 13
        if (a.isNumber && b.isNumber) {
            return try {
                a.decimalValue().compareTo(b.decimalValue()) == 0
            } catch (e: Exception) {
                log.warn(e) {
                    "Failed to compare numeric values, falling back to string comparison"
                }
                a.toString() == b.toString()
            }
        }
        // For non-numeric values, use standard equality
        return a == b
    }

    override fun split(
        unsplitPartition: MsSqlServerJdbcPartition,
        opaqueStateValues: List<OpaqueStateValue>
    ): List<MsSqlServerJdbcPartition> {
        return when (unsplitPartition) {
            is MsSqlServerJdbcRfrSnapshotPartition -> unsplitPartition.split(opaqueStateValues)
            is MsSqlServerJdbcCdcRfrSnapshotPartition -> unsplitPartition.split(opaqueStateValues)
            is MsSqlServerJdbcCdcSnapshotPartition -> unsplitPartition.split(opaqueStateValues)
            is MsSqlServerJdbcSnapshotWithCursorPartition ->
                unsplitPartition.split(opaqueStateValues)
            is MsSqlServerJdbcSplittableSnapshotWithCursorPartition -> listOf(unsplitPartition)
            is MsSqlServerJdbcCursorIncrementalPartition -> listOf(unsplitPartition)
            is MsSqlServerJdbcNonResumableSnapshotPartition -> listOf(unsplitPartition)
            is MsSqlServerJdbcNonResumableSnapshotWithCursorPartition -> listOf(unsplitPartition)
        }
    }

    companion object {
        const val DATETIME_PATTERN = "yyyy-MM-dd'T'HH:mm:ss.SSSSSS"
        val outputDateFormatter: DateTimeFormatter = DateTimeFormatter.ofPattern(DATETIME_PATTERN)

        val TIMESTAMP_WITHOUT_FRACT_SECOND_PATTERN = "yyyy-MM-dd'T'HH:mm:ss"
        val inputDateFormatter: DateTimeFormatter =
            DateTimeFormatterBuilder()
                .appendPattern(TIMESTAMP_WITHOUT_FRACT_SECOND_PATTERN)
                .optionalStart()
                .appendFraction(ChronoField.NANO_OF_SECOND, 1, 6, true)
                .optionalEnd()
                .toFormatter()

        // Parser for timestamps without timezone info
        val timestampWithoutTimezoneParser: DateTimeFormatter =
            DateTimeFormatterBuilder()
                .appendPattern("yyyy-MM-dd'T'HH:mm:ss")
                .optionalStart()
                .appendFraction(ChronoField.NANO_OF_SECOND, 0, 9, true)
                .optionalEnd()
                .toFormatter()

        // Parser for timestamps with timezone info
        val timestampWithTimezoneParser: DateTimeFormatter =
            DateTimeFormatterBuilder()
                .appendPattern("yyyy-MM-dd'T'HH:mm:ss")
                .optionalStart()
                .appendFraction(ChronoField.NANO_OF_SECOND, 0, 9, true)
                .optionalEnd()
                .appendOffset("+HH:MM", "Z")
                .toFormatter()
    }
}
