/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import java.util.concurrent.atomic.AtomicReference

/** Default implementation of [JdbcStreamState]. */
class DefaultJdbcStreamState(
    override val sharedState: DefaultJdbcSharedState,
    override val stream: Stream,
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
