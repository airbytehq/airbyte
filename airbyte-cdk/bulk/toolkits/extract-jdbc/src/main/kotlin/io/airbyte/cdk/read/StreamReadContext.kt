/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.output.CatalogValidationFailureHandler
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.output.ResetStream
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentMap
import java.util.concurrent.atomic.AtomicReference
import kotlinx.coroutines.sync.Semaphore

/**
 * A [StreamReadContextManager] may be injected in a
 * [io.airbyte.cdk.read.PartitionsCreatorFactory] to provide it, and the
 * [io.airbyte.cdk.read.PartitionsCreator] and [io.airbyte.cdk.read.PartitionReader] instances
 * it creates, with a set of global singletons useful for implementing stream READs for a JDBC
 * source.
 *
 * For each stream in the configured catalog, these global singletons are packaged in a
 * [StreamReadContext] which bundles them with the corresponding [Stream] as well as a couple
 * [TransientState] instances which hold mutable metadata which is _transient_, transient in the
 * sense that it is not persisted in an Airbyte STATE message.
 */
@Singleton
class StreamReadContextManager(
    val configuration: JdbcSourceConfiguration,
    val handler: CatalogValidationFailureHandler,
    val selectQueryGenerator: SelectQueryGenerator,
    val selectQuerier: SelectQuerier,
    val outputConsumer: OutputConsumer,
) {
    private val map: ConcurrentMap<AirbyteStreamNameNamespacePair, StreamReadContext> =
        ConcurrentHashMap()

    private val globalSemaphore = Semaphore(configuration.maxConcurrency)

    operator fun get(stream: Stream): StreamReadContext =
        map.getOrPut(stream.namePair) {
            StreamReadContext(
                configuration,
                handler,
                selectQueryGenerator,
                selectQuerier,
                globalSemaphore,
                outputConsumer,
                stream,
            )
        }
}

class StreamReadContext(
    val configuration: JdbcSourceConfiguration,
    val handler: CatalogValidationFailureHandler,
    val selectQueryGenerator: SelectQueryGenerator,
    val selectQuerier: SelectQuerier,
    val querySemaphore: Semaphore,
    val outputConsumer: OutputConsumer,
    val stream: Stream,
) {
    val transientLimitState: TransientState<LimitState> = TransientState(LimitState.minimum)

    val transientCursorUpperBoundState: TransientState<JsonNode?> = TransientState(null)

    val transientFetchSize: TransientState<Int?> = TransientState(null)

    fun resetStream() {
        handler.accept(ResetStream(stream.name, stream.namespace))
        transientLimitState.reset()
        transientCursorUpperBoundState.reset()
        transientFetchSize.reset()
    }
}

class TransientState<T>(
    val initialState: T,
) {
    private val ref: AtomicReference<T> = AtomicReference(initialState)

    fun get(): T = ref.get()

    fun reset() {
        ref.set(initialState)
    }

    fun update(fn: (T) -> T): T = ref.updateAndGet(fn)
}
