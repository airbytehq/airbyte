package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.output.CatalogValidationFailureHandler
import io.airbyte.cdk.read.DefaultJdbcSharedState
import io.airbyte.cdk.read.DefaultJdbcStreamState
import io.airbyte.cdk.read.JdbcPartitionFactory
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.airbyte.integrations.source.postgres.ctid.Ctid
import io.airbyte.integrations.source.postgres.operations.PostgresSourceSelectQueryGenerator
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

@Primary
@Singleton
class PostgresSourceJdbcPartitionFactory(
    override val sharedState: DefaultJdbcSharedState,
    val selectQueryGenerator: PostgresSourceSelectQueryGenerator,
    val config: PostgresSourceConfiguration,
    val handler: CatalogValidationFailureHandler,
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
//        return PostgresSourceJdbcNonResumableSnapshotPartition(selectQueryGenerator, streamState)
        return PostgresSourceJdbcSplittableSnapshotPartition(
            selectQueryGenerator,
            streamState,
            pkChosenFromCatalog,
            lowerBound = null,
            upperBound = null,
        )


    }

    override fun create(streamFeedBootstrap: StreamFeedBootstrap): PostgresSourceJdbcPartition? {
        val stream: Stream = streamFeedBootstrap.feed
        val streamState: DefaultJdbcStreamState = streamState(streamFeedBootstrap)
        val opaqueStateValue: OpaqueStateValue? = streamFeedBootstrap.currentState

        if (opaqueStateValue == PostgresSourceJdbcStreamStateValue.snapshotCompleted) {
            return null
        }

        return coldStart(streamState)
    }

    override fun split(
        unsplitPartition: PostgresSourceJdbcPartition,
        opaqueStateValues: List<OpaqueStateValue>
    ): List<PostgresSourceJdbcPartition> {
        val splitPartitionBoundaries: List<PostgresSourceJdbcStreamStateValue> by lazy {
            opaqueStateValues.map { Jsons.treeToValue(it, PostgresSourceJdbcStreamStateValue::class.java) }
        }

        return when (unsplitPartition) {
            is PostgresSourceJdbcSplittableSnapshotPartition -> unsplitPartition.split(splitPartitionBoundaries)
            else -> listOf(unsplitPartition)
        }
    }

    private fun PostgresSourceJdbcSplittableSnapshotPartition.split(
        splitPointValues: List<PostgresSourceJdbcStreamStateValue>
    ): List<PostgresSourceJdbcSplittableSnapshotPartition> {
        val inners: List<Ctid> =
            splitPointValues.map { Ctid(it.ctid!!) }
        val lbs: List<Ctid?> = listOf(lowerBound) + inners
        val ubs: List<Ctid?> = inners + listOf(upperBound)
        return lbs.zip(ubs).map { (lowerBound, upperBound) ->
            PostgresSourceJdbcSplittableSnapshotPartition(
                selectQueryGenerator,
                streamState,
                primaryKey = checkpointColumns,
                lowerBound,
                upperBound
            )
        }
    }

}
