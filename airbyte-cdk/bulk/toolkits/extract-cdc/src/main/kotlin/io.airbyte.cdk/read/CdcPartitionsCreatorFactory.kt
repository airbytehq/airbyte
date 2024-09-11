package io.airbyte.cdk.read

import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.jdbc.JDBC_PROPERTY_PREFIX
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
        return when (feed) {
            is Global -> CdcPartitionCreator()
            is Stream -> CreateNoPartitions
        }
    }
}

private const val MODE_PROPERTY = "${JDBC_PROPERTY_PREFIX}.mode"
