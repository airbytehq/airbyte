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
    val metadataQuerier: MsSqlSourceMetadataQuerier,
) :
    JdbcPartitionFactory<
        DefaultJdbcSharedState,
        DefaultJdbcStreamState,
        MsSqlServerJdbcPartition,
    > {
    private val log = KotlinLogging.logger {}

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

    private fun findPkUpperBound(stream: Stream, pkChosenFromCatalog: List<Field>): JsonNode {
        // find upper bound using maxPk query
        val jdbcConnectionFactory = JdbcConnectionFactory(config)
        val from = From(stream.name, stream.namespace)
        val maxPkQuery = SelectQuerySpec(SelectColumnMaxValue(pkChosenFromCatalog[0]), from)

        jdbcConnectionFactory.get().use { connection ->
            val stmt = connection.prepareStatement(selectQueryGenerator.generate(maxPkQuery).sql)
            val rs = stmt.executeQuery()

            if (rs.next()) {
                val jdbcFieldType = pkChosenFromCatalog[0].type as JdbcFieldType<*>
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
        val pkChosenFromCatalog: List<Field> = stream.configuredPrimaryKey ?: listOf()
        val isView = isView(stream)

        if (stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH) {
            if (pkChosenFromCatalog.isEmpty()) {
                return MsSqlServerJdbcNonResumableSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                )
            }

            val upperBound = findPkUpperBound(stream, pkChosenFromCatalog)
            return if (sharedState.configuration.global) {
                MsSqlServerJdbcCdcRfrSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                    pkChosenFromCatalog,
                    lowerBound = null,
                    upperBound = listOf(upperBound),
                )
            } else {
                MsSqlServerJdbcRfrSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                    pkChosenFromCatalog,
                    lowerBound = null,
                    upperBound = listOf(upperBound),
                )
            }
        }

        if (sharedState.configuration.global) {
            return MsSqlServerJdbcCdcSnapshotPartition(
                selectQueryGenerator,
                streamState,
                pkChosenFromCatalog,
                lowerBound = null,
            )
        }

        val cursorChosenFromCatalog: Field =
            stream.configuredCursor as? Field ?: throw ConfigErrorException("no cursor")

        // Calculate cutoff time for cursor if exclude today's data is enabled
        val cursorCutoffTime = getCursorCutoffTime(cursorChosenFromCatalog)

        // Views can't be sampled with TABLESAMPLE, so use non-resumable partitions
        // which skip the sampling step entirely
        if (isView || pkChosenFromCatalog.isEmpty()) {
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
            pkChosenFromCatalog,
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
     *    a. If it's global but without PK, use non-resumable  snapshot.
     *    b. If it's global with PK, use snapshot.
     *    c. If it's not global, use snapshot with cursor.
     * ```
     * 2. If the input state is not null -
     * ```
     *    a. If it's in global mode, JdbcPartitionFactory will not handle this. (TODO)
     *    b. If it's cursor based, it could be either in PK read phase (initial read) or
     *       cursor read phase (incremental read). This is differentiated by the stateType.
     *      i. In PK read phase, use snapshot with cursor. If no PKs were found,
     *         use non-resumable snapshot with cursor.
     *      ii. In cursor read phase, use cursor incremental.
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
        val pkChosenFromCatalog: List<Field> = stream.configuredPrimaryKey ?: listOf()

        if (
            pkChosenFromCatalog.isEmpty() &&
                stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH
        ) {
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

        if (!isCursorBased) {
            val sv: MsSqlServerCdcInitialSnapshotStateValue =
                Jsons.treeToValue(
                    opaqueStateValue,
                    MsSqlServerCdcInitialSnapshotStateValue::class.java
                )

            if (stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH) {
                val upperBound = findPkUpperBound(stream, pkChosenFromCatalog)
                if (sv.pkVal == upperBound.asText()) {
                    return null
                }
                val pkLowerBound: JsonNode = stateValueToJsonNode(pkChosenFromCatalog[0], sv.pkVal)

                return MsSqlServerJdbcRfrSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                    pkChosenFromCatalog,
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
                val pkField = pkChosenFromCatalog.first()
                val pkLowerBound: JsonNode = stateValueToJsonNode(pkField, sv.pkVal)

                return MsSqlServerJdbcCdcSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                    pkChosenFromCatalog,
                    listOf(pkLowerBound),
                )
            }
        } else {
            val sv: MsSqlServerJdbcStreamStateValue =
                MsSqlServerStateMigration.parseStateValue(opaqueStateValue)

            if (stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH) {
                val upperBound = findPkUpperBound(stream, pkChosenFromCatalog)
                val pkLowerBound: JsonNode =
                    if (sv.pkValue == null || sv.pkValue.isNull) {
                        Jsons.nullNode()
                    } else if (sv.pkValue.isTextual) {
                        stateValueToJsonNode(pkChosenFromCatalog[0], sv.pkValue.asText())
                    } else {
                        sv.pkValue
                    }

                if (!pkLowerBound.isNull && areValuesEqual(pkLowerBound, upperBound)) {
                    return null
                }

                return MsSqlServerJdbcRfrSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                    pkChosenFromCatalog,
                    lowerBound = if (pkLowerBound.isNull) null else listOf(pkLowerBound),
                    upperBound = listOf(upperBound),
                )
            }

            if (sv.stateType != StateType.CURSOR_BASED.stateType) {
                // Loading value from catalog. Note there could be unexpected behaviors if user
                // updates their schema but did not reset their state.
                val pkLowerBound: JsonNode =
                    if (sv.pkValue == null || sv.pkValue.isNull) {
                        Jsons.nullNode()
                    } else if (sv.pkValue.isTextual) {
                        stateValueToJsonNode(pkChosenFromCatalog[0], sv.pkValue.asText())
                    } else {
                        sv.pkValue
                    }

                val cursorChosenFromCatalog: Field =
                    stream.configuredCursor as? Field ?: throw ConfigErrorException("no cursor")

                // in a state where it's still in primary_key read part.
                return MsSqlServerJdbcSnapshotWithCursorPartition(
                    selectQueryGenerator,
                    streamState,
                    pkChosenFromCatalog,
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
