/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.output.CatalogValidationFailureHandler
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentMap

/**
 * A [StreamReadContextManager] may be injected in a [io.airbyte.cdk.read.PartitionsCreatorFactory]
 * to provide it, and the[io.airbyte.cdk.read.PartitionsCreator] and
 * [io.airbyte.cdk.read.PartitionReader] instances it creates, with a set of global singletons
 * useful for implementing stream READs for a JDBC source.
 *
 * For each stream in the configured catalog, these global singletons are packaged in a
 * [JdbcStreamState] which bundles them with the corresponding [Stream] as well as mutable metadata
 * which is _transient_, transient in the sense that it is not persisted in an Airbyte STATE
 * message.
 */
@Singleton
class StreamReadContextManager(
    val sharedState: JdbcSharedState,
    val handler: CatalogValidationFailureHandler,
    val selectQueryGenerator: SelectQueryGenerator,
) {

    val configuration: JdbcSourceConfiguration
        get() = sharedState.configuration

    val outputConsumer: OutputConsumer
        get() = sharedState.outputConsumer

    val selectQuerier: SelectQuerier
        get() = sharedState.selectQuerier

    private val map: ConcurrentMap<AirbyteStreamNameNamespacePair, JdbcStreamState<*>> =
        ConcurrentHashMap()

    operator fun get(stream: Stream): JdbcStreamState<*> =
        map.getOrPut(stream.namePair) {
            DefaultJdbcStreamState(sharedState as DefaultJdbcSharedState, stream)
        }
}
