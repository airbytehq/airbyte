/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb.state

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.integrations.source.relationaldb.CursorInfo
import io.airbyte.protocol.models.v0.*
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*
import java.util.concurrent.*
import java.util.function.Function
import java.util.function.Supplier

private val LOGGER = KotlinLogging.logger {}
/**
 * Manages the map of streams to current cursor values for state management.
 *
 * @param <S> The type that represents the stream object which holds the current cursor information
 * in the state. </S>
 */
class CursorManager<S : Any>(
    catalog: ConfiguredAirbyteCatalog,
    streamSupplier: Supplier<Collection<S>>,
    cursorFunction: Function<S, String>?,
    cursorFieldFunction: Function<S, List<String>>?,
    cursorRecordCountFunction: Function<S, Long>?,
    namespacePairFunction: Function<S, AirbyteStreamNameNamespacePair?>,
    onlyIncludeIncrementalStreams: Boolean
) {
    /**
     * Map of streams (name/namespace tuple) to the current cursor information stored in the state.
     */
    val pairToCursorInfo: Map<AirbyteStreamNameNamespacePair, CursorInfo>

    /**
     * Constructs a new [CursorManager] based on the configured connector and current state
     * information.
     *
     * @param catalog The connector's configured catalog.
     * @param streamSupplier A [Supplier] that provides the cursor manager with the collection of
     * streams tracked by the connector's state.
     * @param cursorFunction A [Function] that extracts the current cursor from a stream stored in
     * the connector's state.
     * @param cursorFieldFunction A [Function] that extracts the cursor field name from a stream
     * stored in the connector's state.
     * @param cursorRecordCountFunction A [Function] that extracts the cursor record count for a
     * stream stored in the connector's state.
     * @param namespacePairFunction A [Function] that generates a [AirbyteStreamNameNamespacePair]
     * that identifies each stream in the connector's state.
     */
    init {
        pairToCursorInfo =
            createCursorInfoMap(
                catalog,
                streamSupplier,
                cursorFunction,
                cursorFieldFunction,
                cursorRecordCountFunction,
                namespacePairFunction,
                onlyIncludeIncrementalStreams
            )
    }

    /**
     * Creates the cursor information map that associates stream name/namespace tuples with the
     * current cursor information for that stream as stored in the connector's state.
     *
     * @param catalog The connector's configured catalog.
     * @param streamSupplier A [Supplier] that provides the cursor manager with the collection of
     * streams tracked by the connector's state.
     * @param cursorFunction A [Function] that extracts the current cursor from a stream stored in
     * the connector's state.
     * @param cursorFieldFunction A [Function] that extracts the cursor field name from a stream
     * stored in the connector's state.
     * @param cursorRecordCountFunction A [Function] that extracts the cursor record count for a
     * stream stored in the connector's state.
     * @param namespacePairFunction A [Function] that generates a [AirbyteStreamNameNamespacePair]
     * that identifies each stream in the connector's state.
     * @return A map of streams to current cursor information for the stream.
     */
    @VisibleForTesting
    protected fun createCursorInfoMap(
        catalog: ConfiguredAirbyteCatalog,
        streamSupplier: Supplier<Collection<S>>,
        cursorFunction: Function<S, String>?,
        cursorFieldFunction: Function<S, List<String>>?,
        cursorRecordCountFunction: Function<S, Long>?,
        namespacePairFunction: Function<S, AirbyteStreamNameNamespacePair?>,
        onlyIncludeIncrementalStreams: Boolean
    ): Map<AirbyteStreamNameNamespacePair, CursorInfo> {
        val allStreamNames =
            catalog.streams
                .filter { c: ConfiguredAirbyteStream ->
                    if (onlyIncludeIncrementalStreams) {
                        return@filter c.syncMode == SyncMode.INCREMENTAL
                    }
                    true
                }
                .map { obj: ConfiguredAirbyteStream -> obj.stream }
                .map { stream: AirbyteStream ->
                    AirbyteStreamNameNamespacePair.fromAirbyteStream(stream)
                }
                .toMutableSet()
        allStreamNames.addAll(
            streamSupplier
                .get()
                .map { namespacePairFunction.apply(it) }
                .filter { obj: AirbyteStreamNameNamespacePair? -> Objects.nonNull(obj) }
                .toSet()
        )

        val localMap: MutableMap<AirbyteStreamNameNamespacePair, CursorInfo> = ConcurrentHashMap()
        val pairToState = streamSupplier.get().associateBy { namespacePairFunction.apply(it) }
        val pairToConfiguredAirbyteStream =
            catalog.streams.associateBy {
                AirbyteStreamNameNamespacePair.fromConfiguredAirbyteSteam(it)
            }

        for (pair in allStreamNames) {
            val stateOptional: Optional<S> = Optional.ofNullable(pairToState[pair])
            val streamOptional = Optional.ofNullable(pairToConfiguredAirbyteStream[pair])
            localMap[pair] =
                createCursorInfoForStream(
                    pair,
                    stateOptional,
                    streamOptional,
                    cursorFunction,
                    cursorFieldFunction,
                    cursorRecordCountFunction
                )
        }

        return localMap.toMap()
    }

    /**
     * Generates a [CursorInfo] object based on the data currently stored in the connector's state
     * for the given stream.
     *
     * @param pair A [AirbyteStreamNameNamespacePair] that identifies a specific stream managed by
     * the connector.
     * @param stateOptional [Optional] containing the current state associated with the stream.
     * @param streamOptional [Optional] containing the [ConfiguredAirbyteStream] associated with the
     * stream.
     * @param cursorFunction A [Function] that provides the current cursor from the state associated
     * with the stream.
     * @param cursorFieldFunction A [Function] that provides the cursor field name for the cursor
     * stored in the state associated with the stream.
     * @param cursorRecordCountFunction A [Function] that extracts the cursor record count for a
     * stream stored in the connector's state.
     * @return A [CursorInfo] object based on the data currently stored in the connector's state for
     * the given stream.
     */
    internal fun createCursorInfoForStream(
        pair: AirbyteStreamNameNamespacePair?,
        stateOptional: Optional<S>,
        streamOptional: Optional<ConfiguredAirbyteStream>,
        cursorFunction: Function<S, String>?,
        cursorFieldFunction: Function<S, List<String>>?,
        cursorRecordCountFunction: Function<S, Long>?
    ): CursorInfo {
        val originalCursorField =
            stateOptional
                .map(cursorFieldFunction)
                .flatMap { f: List<String> ->
                    if (f.isNotEmpty()) Optional.of(f[0]) else Optional.empty()
                }
                .orElse(null)
        val originalCursor = stateOptional.map(cursorFunction).orElse(null)
        val originalCursorRecordCount = stateOptional.map(cursorRecordCountFunction).orElse(0L)

        val cursor: String?
        val cursorField: String?
        val cursorRecordCount: Long

        // if cursor field is set in catalog.
        if (
            streamOptional
                .map<List<String>> { obj: ConfiguredAirbyteStream -> obj.cursorField }
                .isPresent
        ) {
            cursorField =
                streamOptional
                    .map { obj: ConfiguredAirbyteStream -> obj.cursorField }
                    .flatMap { f: List<String> ->
                        if (f.size > 0) Optional.of(f[0]) else Optional.empty()
                    }
                    .orElse(null)
            // if cursor field is set in state.
            if (stateOptional.map<List<String>?>(cursorFieldFunction).isPresent) {
                // if cursor field in catalog and state are the same.
                if (
                    stateOptional.map<List<String>?>(cursorFieldFunction) ==
                        streamOptional.map<List<String>> { obj: ConfiguredAirbyteStream ->
                            obj.cursorField
                        }
                ) {
                    cursor = stateOptional.map(cursorFunction).orElse(null)
                    cursorRecordCount = stateOptional.map(cursorRecordCountFunction).orElse(0L)
                    // If a matching cursor is found in the state, and it's value is null - this
                    // indicates a CDC stream
                    // and we shouldn't log anything.
                    if (cursor != null) {
                        LOGGER.info {
                            "Found matching cursor in state. Stream: $pair. Cursor Field: $cursorField Value: $cursor Count: $cursorRecordCount"
                        }
                    }
                    // if cursor field in catalog and state are different.
                } else {
                    cursor = null
                    cursorRecordCount = 0L
                    LOGGER.info {
                        "Found cursor field. Does not match previous cursor field. Stream: $pair." +
                            " Original Cursor Field: $originalCursorField (count $originalCursorRecordCount). " +
                            "New Cursor Field: $cursorField. Resetting cursor value."
                    }
                }
                // if cursor field is not set in state but is set in catalog.
            } else {
                LOGGER.info {
                    "No cursor field set in catalog but not present in state. " +
                        "Stream: $pair, New Cursor Field: $cursorField. Resetting cursor value"
                }
                cursor = null
                cursorRecordCount = 0L
            }
            // if cursor field is not set in catalog.
        } else {
            LOGGER.info {
                "Cursor field set in state but not present in catalog. " +
                    "Stream: $pair. Original Cursor Field: $originalCursorField. " +
                    "Original value: $originalCursor. Resetting cursor."
            }
            cursorField = null
            cursor = null
            cursorRecordCount = 0L
        }

        return CursorInfo(
            originalCursorField,
            originalCursor,
            originalCursorRecordCount,
            cursorField,
            cursor,
            cursorRecordCount
        )
    }

    /**
     * Retrieves an [Optional] possibly containing the current [CursorInfo] associated with the
     * provided stream name/namespace tuple.
     *
     * @param pair The [AirbyteStreamNameNamespacePair] which identifies a stream.
     * @return An [Optional] possibly containing the current [CursorInfo] associated with the
     * provided stream name/namespace tuple.
     */
    fun getCursorInfo(pair: AirbyteStreamNameNamespacePair?): Optional<CursorInfo> {
        return Optional.ofNullable(pairToCursorInfo[pair])
    }

    /**
     * Retrieves an [Optional] possibly containing the cursor field name associated with the cursor
     * tracked in the state associated with the provided stream name/namespace tuple.
     *
     * @param pair The [AirbyteStreamNameNamespacePair] which identifies a stream.
     * @return An [Optional] possibly containing the cursor field name associated with the cursor
     * tracked in the state associated with the provided stream name/namespace tuple.
     */
    fun getCursorField(pair: AirbyteStreamNameNamespacePair?): Optional<String> {
        return getCursorInfo(pair).map { obj: CursorInfo -> obj.cursorField }
    }

    /**
     * Retrieves an [Optional] possibly containing the cursor value tracked in the state associated
     * with the provided stream name/namespace tuple.
     *
     * @param pair The [AirbyteStreamNameNamespacePair] which identifies a stream.
     * @return An [Optional] possibly containing the cursor value tracked in the state associated
     * with the provided stream name/namespace tuple.
     */
    fun getCursor(pair: AirbyteStreamNameNamespacePair?): Optional<String> {
        return getCursorInfo(pair).map { obj: CursorInfo -> obj.cursor }
    }

    companion object {}
}
