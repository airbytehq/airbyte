package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.read.DefaultJdbcSharedState
import io.airbyte.cdk.read.DefaultJdbcStreamState
import io.airbyte.cdk.read.JdbcPartitionFactory
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.airbyte.integrations.source.postgres.operations.PostgresSourceSelectQueryGenerator
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

//@Primary
//@Singleton
class PostgresSourceJdbcPartitionFactory(
    override val sharedState: DefaultJdbcSharedState,
    val selectQueryGenerator: PostgresSourceSelectQueryGenerator,
    val config: PostgresSourceConfiguration
) : JdbcPartitionFactory<DefaultJdbcSharedState, DefaultJdbcStreamState, PostgresSourceJdbcPartition> {
    private val streamStates = ConcurrentHashMap<StreamIdentifier, DefaultJdbcStreamState>()

    override fun streamState(streamFeedBootstrap: StreamFeedBootstrap): DefaultJdbcStreamState =
        streamStates.getOrPut(streamFeedBootstrap.feed.id) {
            DefaultJdbcStreamState(sharedState, streamFeedBootstrap)
        }

    private fun coldStart(streamState: DefaultJdbcStreamState): PostgresSourceJdbcPartition {
        val stream: Stream = streamState.stream
        val pkChosenFromCatalog: List<Field> = stream.configuredPrimaryKey ?: listOf()
        pkChosenFromCatalog.size // TEMP
        return PostgresSourceJdbcNonResumableSnapshotPartition(selectQueryGenerator, streamState)


    }

    override fun create(streamFeedBootstrap: StreamFeedBootstrap): PostgresSourceJdbcPartition? {
        val stream: Stream = streamFeedBootstrap.feed
        val streamState: DefaultJdbcStreamState = streamState(streamFeedBootstrap)
        return coldStart(streamState) // TEMP
    }

    override fun split(
        unsplitPartition: PostgresSourceJdbcPartition,
        opaqueStateValues: List<OpaqueStateValue>
    ): List<PostgresSourceJdbcPartition> {
        return listOf(unsplitPartition) // TEMP
    }

}
