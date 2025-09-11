package io.airbyte.integrations.source.datagen.partitionops

import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.FeedBootstrap
import io.airbyte.cdk.read.PartitionsCreator
import io.airbyte.cdk.read.PartitionsCreatorFactory
import io.airbyte.cdk.read.PartitionsCreatorFactorySupplier
import io.airbyte.cdk.read.ResourceAcquirer
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.integrations.source.datagen.partitionobjs.DataGenSharedState
import io.airbyte.integrations.source.datagen.partitionobjs.DataGenSourcePartition
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.time.Clock
import java.time.LocalTime
import kotlin.time.Duration.Companion.seconds

@Singleton
class DataGenSourcePartitionCreatorFactory(
    val partitionFactory: DataGenSourcePartitionFactory,
    val clock: Clock
) : PartitionsCreatorFactory {
    private val log = KotlinLogging.logger {}
    var endTime: LocalTime? = null

    override fun make(feedBootstrap: FeedBootstrap<*>): DataGenPartitionCreator? {
        if (feedBootstrap !is StreamFeedBootstrap) {
            return null
        }

        val partition: DataGenSourcePartition =
            partitionFactory.create(feedBootstrap) ?: return null
        val sharedState = partition.streamState.sharedState
        if (endTime == null) {
            endTime = LocalTime.now(clock).plusSeconds(sharedState.configuration.runDuration)
        }
        log.info { "runDuration: ${sharedState.configuration.runDuration}" }
        log.info { "endTime: $endTime" }
        val endTimeLocal = endTime!!

        return DataGenPartitionCreator(partition, partitionFactory, clock, endTimeLocal)
    }
}

@Singleton
class DataGenSourcePartitionCreatorFactorySupplier<T : DataGenSourcePartitionCreatorFactory> (val factory: T):
    PartitionsCreatorFactorySupplier<T> {
    override fun get(): T = factory
}
