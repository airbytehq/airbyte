/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.sap_hana

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.read.DefaultJdbcSharedState
import io.airbyte.cdk.read.JdbcStreamState
import io.airbyte.cdk.read.LimitState
import io.airbyte.cdk.read.StreamFeedBootstrap
import java.util.concurrent.atomic.AtomicReference

/** Implementation of [JdbcStreamState] for SAP HANA. */
class SapHanaJdbcStreamState(
    override val sharedState: DefaultJdbcSharedState,
    override val streamFeedBootstrap: StreamFeedBootstrap,
) : JdbcStreamState<DefaultJdbcSharedState> {

    override var cursorUpperBound: JsonNode?
        get() = transient.get().cursorUpperBound
        set(value) {
            transient.updateAndGet { it.copy(cursorUpperBound = value) }
        }

    override var fetchSize: Int?
        get() = transient.get().fetchSize
        set(value) {
            transient.updateAndGet { it.copy(fetchSize = value) }
        }

    override val fetchSizeOrDefault: Int
        get() = fetchSize ?: sharedState.constants.defaultFetchSize

    override val limit: Long
        get() = fetchSizeOrDefault * transient.get().limitState.current

    private val transient = AtomicReference(Transient.initial)

    var isReadingFromTriggerTable: Boolean = false

    override fun updateLimitState(fn: (LimitState) -> LimitState) {
        transient.updateAndGet { it.copy(limitState = fn(it.limitState)) }
    }

    override fun reset() {
        transient.set(Transient.initial)
    }

    private data class Transient(
        val fetchSize: Int?,
        val limitState: LimitState,
        val cursorUpperBound: JsonNode?,
    ) {
        companion object {
            val initial = Transient(fetchSize = null, LimitState.minimum, cursorUpperBound = null)
        }
    }
}
