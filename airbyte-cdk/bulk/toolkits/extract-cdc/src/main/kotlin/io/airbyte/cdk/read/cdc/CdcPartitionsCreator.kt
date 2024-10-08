/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.PartitionsCreator
import io.airbyte.cdk.read.StateQuerier
import io.airbyte.cdk.read.Stream
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.atomic.AtomicReference

/** [PartitionsCreator] implementation for CDC with Debezium. */
class CdcPartitionsCreator<T : Comparable<T>>(
    val concurrencyResource: ConcurrencyResource,
    val globalLockResource: CdcGlobalLockResource,
    val stateQuerier: StateQuerier,
    val outputConsumer: OutputConsumer,
    val creatorOps: CdcPartitionsCreatorDebeziumOperations<T>,
    val readerOps: CdcPartitionReaderDebeziumOperations<T>,
    val upperBoundReference: AtomicReference<T>,
    val incumbentOpaqueStateValue: OpaqueStateValue?,
) : PartitionsCreator {
    private val log = KotlinLogging.logger {}
    private val acquiredThread = AtomicReference<ConcurrencyResource.AcquiredThread>()

    override fun tryAcquireResources(): PartitionsCreator.TryAcquireResourcesStatus {
        val acquiredThread: ConcurrencyResource.AcquiredThread =
            concurrencyResource.tryAcquire()
                ?: return PartitionsCreator.TryAcquireResourcesStatus.RETRY_LATER
        this.acquiredThread.set(acquiredThread)
        return PartitionsCreator.TryAcquireResourcesStatus.READY_TO_RUN
    }

    override fun releaseResources() {
        acquiredThread.getAndSet(null)?.close()
    }

    override suspend fun run(): List<PartitionReader> {
        val activeStreams: List<Stream> by lazy {
            stateQuerier.feeds
                .filterIsInstance<Stream>()
                .filter { it.configuredSyncMode == ConfiguredSyncMode.INCREMENTAL }
                .filter { stateQuerier.current(it) != null }
        }
        val syntheticInput: DebeziumInput by lazy { creatorOps.synthesize() }
        // Ensure that the WAL position upper bound has been computed for this sync.
        val upperBound: T =
            upperBoundReference.updateAndGet {
                it ?: creatorOps.position(syntheticInput.state.offset)
            }
        // Deserialize the incumbent state value, if it exists.
        val input: DebeziumInput =
            if (incumbentOpaqueStateValue == null) {
                syntheticInput
            } else {
                // validate if existing state is still valid on DB.
                try {
                    creatorOps.deserialize(incumbentOpaqueStateValue, activeStreams)
                } catch (ex: ConfigErrorException) {
                    log.error(ex) { "Existing state is invalid." }
                    globalLockResource.markCdcAsComplete()
                    throw ex
                }
            }

        // Build and return PartitionReader instance, if applicable.
        val partitionReader =
            CdcPartitionReader(concurrencyResource, outputConsumer, readerOps, upperBound, input)
        if (input.isSynthetic) {
            // Handle synthetic offset edge-case, which always needs to run.
            // Debezium needs to run to generate the full state, which might include schema history.
            log.info { "Current offset is synthetic." }
            return listOf(partitionReader)
        }
        val lowerBound: T = creatorOps.position(input.state.offset)
        if (upperBound <= lowerBound) {
            // Handle completion due to reaching the WAL position upper bound.
            log.info {
                "Current position '$lowerBound' equals or exceeds target position '$upperBound'."
            }
            globalLockResource.markCdcAsComplete()
            return listOf()
        }
        // Handle common case.
        log.info { "Current position '$lowerBound' does not exceed target position '$upperBound'." }
        return listOf(partitionReader)
    }
}
