package io.airbyte.cdk.read

import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.jdbc.JDBC_PROPERTY_PREFIX
import io.airbyte.cdk.read.PartitionsCreator.TryAcquireResourcesStatus
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Singleton
@Requires(property = MODE_PROPERTY, value = "cdc")
class CdcPartitionsCreatorFactory<
    A : JdbcSharedState,
    S : JdbcStreamState<A>,
    P : JdbcPartition<S>,
    >(
        val partitionFactory: JdbcPartitionFactory<A, S, P>,
): PartitionsCreatorFactory {
    override fun make(stateQuerier: StateQuerier, feed: Feed): PartitionsCreator {
        val opaqueStateValue: OpaqueStateValue? = stateQuerier.current(feed)
        return when (feed) {
            is Global -> CdcPartitionCreator(partitionFactory.sharedState)
            is Stream -> {
                val partition: P? = partitionFactory.create(feed, opaqueStateValue)
                if (partition == null) {
                    CreateNoPartitions
                } else {
//                    CdcAwareJdbcNonResumablePartitionReader(partition)
                    partitionsCreator(partition)
                }
            }
        }
    }

    fun partitionsCreator(partition: P): PartitionsCreator {
        return MyPartitionsCreator<A, S, P>(partition)
    }
}

class MyPartitionsCreator<
    A : JdbcSharedState,
    S : JdbcStreamState<A>,
    P : JdbcPartition<S>,
>(val partition: P) : PartitionsCreator {
    override fun tryAcquireResources(): TryAcquireResourcesStatus {
        return TryAcquireResourcesStatus.READY_TO_RUN
    }

    override suspend fun run(): List<PartitionReader> {
        return listOf(CdcAwareJdbcNonResumablePartitionReader(partition))
    }

    override fun releaseResources() {
        //no-op
    }
}
private const val MODE_PROPERTY = "${JDBC_PROPERTY_PREFIX}.mode"
