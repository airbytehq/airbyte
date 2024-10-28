/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb.state

import io.airbyte.cdk.integrations.source.relationaldb.CdcStateManager
import io.airbyte.cdk.integrations.source.relationaldb.models.DbState
import io.airbyte.cdk.integrations.source.relationaldb.models.DbStreamState
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*
import java.util.function.Function
import java.util.function.Supplier

private val LOGGER = KotlinLogging.logger {}
/**
 * Legacy implementation (pre-per-stream state support) of the [StateManager] interface.
 *
 * This implementation assumes that the state matches the [DbState] object and effectively tracks
 * state as global across the streams managed by a connector.
 */
@Deprecated(
    """This manager may be removed in the future if/once all connectors support per-stream
              state management."""
)
class LegacyStateManager(dbState: DbState, catalog: ConfiguredAirbyteCatalog) :
    AbstractStateManager<DbState, DbStreamState>(
        catalog,
        Supplier { dbState.streams },
        CURSOR_FUNCTION,
        CURSOR_FIELD_FUNCTION,
        CURSOR_RECORD_COUNT_FUNCTION,
        NAME_NAMESPACE_PAIR_FUNCTION
    ) {
    /** Tracks whether the connector associated with this state manager supports CDC. */
    private var isCdc: Boolean

    /** [CdcStateManager] used to manage state for connectors that support CDC. */
    override val cdcStateManager: CdcStateManager =
        CdcStateManager(
            dbState.cdcState,
            AirbyteStreamNameNamespacePair.fromConfiguredCatalog(catalog),
            null
        )

    /**
     * Constructs a new [LegacyStateManager] that is seeded with the provided [DbState] instance.
     *
     * @param dbState The initial state represented as an [DbState] instance.
     * @param catalog The [ConfiguredAirbyteCatalog] for the connector associated with this state
     * manager.
     */
    init {
        this.isCdc = dbState.cdc ?: false
    }

    override val rawStateMessages: List<AirbyteStateMessage>?
        get() {
            throw UnsupportedOperationException(
                "Raw state retrieval not supported by global state manager."
            )
        }

    override fun toState(pair: Optional<AirbyteStreamNameNamespacePair>): AirbyteStateMessage {
        val dbState =
            StateGeneratorUtils.generateDbState(pairToCursorInfoMap)
                .withCdc(isCdc)
                .withCdcState(cdcStateManager.cdcState)

        LOGGER.debug { "Generated legacy state for ${dbState.streams.size} streams" }
        return AirbyteStateMessage()
            .withType(AirbyteStateMessage.AirbyteStateType.LEGACY)
            .withData(Jsons.jsonNode(dbState))
    }

    override fun updateAndEmit(
        pair: AirbyteStreamNameNamespacePair,
        cursor: String?
    ): AirbyteStateMessage? {
        return updateAndEmit(pair, cursor, 0L)
    }

    override fun updateAndEmit(
        pair: AirbyteStreamNameNamespacePair,
        cursor: String?,
        cursorRecordCount: Long
    ): AirbyteStateMessage? {
        // cdc file gets updated by debezium so the "update" part is a no op.
        if (!isCdc) {
            return super.updateAndEmit(pair, cursor, cursorRecordCount)
        }

        return toState(Optional.ofNullable(pair))
    }

    companion object {

        /** [Function] that extracts the cursor from the stream state. */
        private val CURSOR_FUNCTION = DbStreamState::getCursor

        /** [Function] that extracts the cursor field(s) from the stream state. */
        private val CURSOR_FIELD_FUNCTION = DbStreamState::getCursorField

        private val CURSOR_RECORD_COUNT_FUNCTION = Function { stream: DbStreamState ->
            Objects.requireNonNullElse(stream.cursorRecordCount, 0L)
        }

        /** [Function] that creates an [AirbyteStreamNameNamespacePair] from the stream state. */
        private val NAME_NAMESPACE_PAIR_FUNCTION =
            Function<DbStreamState, AirbyteStreamNameNamespacePair?> { s: DbStreamState ->
                AirbyteStreamNameNamespacePair(s.streamName, s.streamNamespace)
            }
    }
}
