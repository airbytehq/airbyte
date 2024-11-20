/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.TransientErrorException
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.GlobalFeedBootstrap
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.PartitionsCreator
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.atomic.AtomicReference

/** [PartitionsCreator] implementation for CDC with Debezium. */
class CdcPartitionsCreator<T : Comparable<T>>(
    val concurrencyResource: ConcurrencyResource,
    val globalLockResource: CdcGlobalLockResource,
    val feedBootstrap: GlobalFeedBootstrap,
    val creatorOps: CdcPartitionsCreatorDebeziumOperations<T>,
    val readerOps: CdcPartitionReaderDebeziumOperations<T>,
    val lowerBoundReference: AtomicReference<T>,
    val upperBoundReference: AtomicReference<T>,
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
        if (b) {
            val pr = object: PartitionReader {
                override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus =
                    PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN

                override suspend fun run() {
                    throw TransientErrorException("Re-Sync")
                }

                override fun checkpoint(): PartitionReadCheckpoint {
                    TODO("Not yet implemented")
                }

                override fun releaseResources() {
                    // no-op
                }

            }
            log.info { "*** resync 2: $pr"}
            return listOf(pr)
        }
        val activeStreams: List<Stream> by lazy {
            feedBootstrap.feed.streams.filter { feedBootstrap.stateQuerier.current(it) != null }
        }
        val syntheticInput: DebeziumInput by lazy { creatorOps.synthesize() }
        // Ensure that the WAL position upper bound has been computed for this sync.
        val upperBound: T =
            upperBoundReference.updateAndGet {
                it ?: creatorOps.position(syntheticInput.state.offset)
            }
        // Deserialize the incumbent state value, if it exists.
        val input: DebeziumInput =
            when (val incumbentOpaqueStateValue = feedBootstrap.currentState) {
                null -> syntheticInput
                else -> {
                    // validate if existing state is still valid on DB.
                    try {
                        creatorOps.deserialize(incumbentOpaqueStateValue, activeStreams)
                    } catch (ex: ConfigErrorException) {
                        log.error(ex) { "Existing state is invalid." }
                        globalLockResource.markCdcAsComplete()
                        throw ex
                    }
                }
            }

        // Build and return PartitionReader instance, if applicable.
        val partitionReader =
            CdcPartitionReader(
                concurrencyResource,
                feedBootstrap.streamRecordConsumers(),
                readerOps,
                upperBound,
                input
            )
        val lowerBound: T = creatorOps.position(input.state.offset)
        val lowerBoundInPreviousRound: T? = lowerBoundReference.getAndSet(lowerBound)
        if (input.isSynthetic) {
            // Handle synthetic offset edge-case, which always needs to run.
            // Debezium needs to run to generate the full state, which might include schema history.
            /*log.info { "*** stateQuerier before: ${feedBootstrap.stateQuerier.feeds}" }
            log.info { "*** stateQuerier: ${feedBootstrap.stateQuerier.feeds}" }
            log.info { "*** current: ${feedBootstrap.stateQuerier.current(feedBootstrap.stateQuerier.feeds[1])}" }
            val pr = object : PartitionReader {
                override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus =
                    PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN

                override suspend fun run() {
                    // no-op
                }

                override fun checkpoint(): PartitionReadCheckpoint {
                    Jsons.valueToTree("aaa") as ObjectNode
                    val key: ArrayNode = Jsons.arrayNode().apply {
                        add("aaa")
                    }
                    val value: ObjectNode = Jsons.objectNode().apply {
                        put("bbb", "ccc")
                    }
                    val offset: DebeziumOffset = DebeziumOffset(mapOf(key to value))
                    val schemaHistory: DebeziumSchemaHistory? = null
                    val output = DebeziumState(offset, schemaHistory)
                    return PartitionReadCheckpoint(readerOps.serialize(output), 0)
                    // Implement checkpoint logic here
                    return PartitionReadCheckpoint(
                        opaqueStateValue = Jsons.objectNode() ,
                        numRecords = 0L
                    )
                }

                override fun releaseResources() {
                    // Implement resource release logic here
                }
            }*/
            log.info { "*** resync 1"}
            feedBootstrap.stateQuerier.reset()
            b = true
            log.info { "Current offset is synthetic." }
            return listOf(partitionReader/*pr*/)
        }
        if (upperBound <= lowerBound) {
            // Handle completion due to reaching the WAL position upper bound.
            log.info {
                "Current position '$lowerBound' equals or exceeds target position '$upperBound'."
            }
            globalLockResource.markCdcAsComplete()
            return emptyList()
        }
        if (lowerBoundInPreviousRound != null && lowerBound <= lowerBoundInPreviousRound) {
            // Handle completion due to stalling.
            log.info {
                "Current position '$lowerBound' has not increased in the last round, " +
                    "prior to which is was '$lowerBoundInPreviousRound'."
            }
            globalLockResource.markCdcAsComplete()
            return emptyList()
        }
        // Handle common case.
        log.info { "Current position '$lowerBound' does not exceed target position '$upperBound'." }
        return listOf(partitionReader)
    }

    companion object {
        var b: Boolean = false
    }
}
