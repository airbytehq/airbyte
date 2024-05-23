/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb.state

import io.airbyte.cdk.integrations.source.relationaldb.CursorInfo
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import java.util.*
import java.util.function.Function
import java.util.function.Supplier

/**
 * Abstract implementation of the [StateManager] interface that provides common functionality for
 * state manager implementations.
 *
 * @param <T> The type associated with the state object managed by this manager.
 * @param <S> The type associated with the state object stored in the state managed by this manager.
 * </S></T>
 */
abstract class AbstractStateManager<T, S : Any>
@JvmOverloads
constructor(
    catalog: ConfiguredAirbyteCatalog,
    streamSupplier: Supplier<Collection<S>>,
    cursorFunction: Function<S, String>?,
    cursorFieldFunction: Function<S, List<String>>?,
    cursorRecordCountFunction: Function<S, Long>?,
    namespacePairFunction: Function<S, AirbyteStreamNameNamespacePair?>,
    onlyIncludeIncrementalStreams: Boolean = false
) : StateManager {
    /**
     * The [CursorManager] responsible for keeping track of the current cursor value for each stream
     * managed by this state manager.
     */
    private val cursorManager: CursorManager<*> =
        CursorManager<S>(
            catalog,
            streamSupplier,
            cursorFunction,
            cursorFieldFunction,
            cursorRecordCountFunction,
            namespacePairFunction,
            onlyIncludeIncrementalStreams
        )

    override val pairToCursorInfoMap: Map<AirbyteStreamNameNamespacePair, CursorInfo>
        get() = cursorManager.pairToCursorInfo

    abstract override fun toState(
        pair: Optional<AirbyteStreamNameNamespacePair>
    ): AirbyteStateMessage
}
