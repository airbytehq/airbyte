package io.airbyte.integrations.source.postgres

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.output.CatalogValidationFailureHandler
import io.airbyte.cdk.output.InvalidPrimaryKey
import io.airbyte.cdk.read.DefaultJdbcSharedState
import io.airbyte.cdk.read.DefaultJdbcStreamState
import io.airbyte.cdk.read.DefaultJdbcStreamStateValue
import io.airbyte.cdk.read.JdbcPartitionFactory
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
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
        return coldStart(streamState) // TEMP
    }

    override fun split(
        unsplitPartition: PostgresSourceJdbcPartition,
        opaqueStateValues: List<OpaqueStateValue>
    ): List<PostgresSourceJdbcPartition> {
        val splitPartitionBoundaries: List<DefaultJdbcStreamStateValue> by lazy {
            opaqueStateValues.map { Jsons.treeToValue(it, DefaultJdbcStreamStateValue::class.java) }
        }

        return when (unsplitPartition) {
            is PostgresSourceJdbcSplittableSnapshotPartition -> unsplitPartition.split(splitPartitionBoundaries)
            else -> listOf(unsplitPartition)
        }
    }

    private fun PostgresSourceJdbcSplittableSnapshotPartition.split(
        splitPointValues: List<DefaultJdbcStreamStateValue>
    ): List<PostgresSourceJdbcSplittableSnapshotPartition> {
        val inners: List<List<JsonNode>> =
            splitPointValues.mapNotNull { it.pkMap(streamState.stream)?.values?.toList() }
        val lbs: List<List<JsonNode>?> = listOf(lowerBound) + inners
        val ubs: List<List<JsonNode>?> = inners + listOf(upperBound)
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

    private fun DefaultJdbcStreamStateValue.pkMap(stream: Stream): Map<Field, JsonNode>? {
        if (primaryKey.isEmpty()) {
            return mapOf()
        }
        val fields: List<Field> = stream.configuredPrimaryKey ?: listOf()
        if (primaryKey.keys != fields.map { it.id }.toSet()) {
            handler.accept(
                InvalidPrimaryKey(stream.id, primaryKey.keys.toList()),
            )
            return null
        }
        return fields.associateWith { primaryKey[it.id]!! }
    }

}
