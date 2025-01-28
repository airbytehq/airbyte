/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.TransientErrorException
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.GlobalFeedBootstrap
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.PartitionsCreator
import io.airbyte.cdk.read.Stream
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.atomic.AtomicReference

/** [PartitionsCreator] implementation for CDC with Debezium. */
open class CdcPartitionsCreator<T : Comparable<T>>(
    val concurrencyResource: ConcurrencyResource,
    val feedBootstrap: GlobalFeedBootstrap,
    val creatorOps: CdcPartitionsCreatorDebeziumOperations<T>,
    val readerOps: CdcPartitionReaderDebeziumOperations<T>,
    val lowerBoundReference: AtomicReference<T>,
    val upperBoundReference: AtomicReference<T>,
) : PartitionsCreator {
    private val log = KotlinLogging.logger {}
    private val acquiredThread = AtomicReference<ConcurrencyResource.AcquiredThread>()

    class OffsetInvalidNeedsResyncIllegalStateException() : IllegalStateException()

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

    open fun createCdcPartitionReader(upperBound: T, input: DebeziumInput) =
        CdcPartitionReader(
            concurrencyResource,
            feedBootstrap.streamRecordConsumers(),
            readerOps,
            upperBound,
            input
        )

    override suspend fun run(): List<PartitionReader> {
        if (CDCNeedsRestart) {
            throw TransientErrorException(
                "Saved offset no longer present on the server, Airbyte is going to trigger a sync from scratch."
            )
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
                        throw ex
                    } catch (_: OffsetInvalidNeedsResyncIllegalStateException) {
                        // If deserialization concludes we need a re-sync we rollback stream states
                        // and put the creator in a Need Restart mode.
                        // The next round will throw a transient error to kickoff the resync
                        feedBootstrap.stateQuerier.resetFeedStates()
                        CDCNeedsRestart = true
                        syntheticInput
                    }
                }
            }

        // Build and return PartitionReader instance, if applicable.
        val partitionReader = createCdcPartitionReader(upperBound, input)

        val lowerBound: T = creatorOps.position(input.state.offset)
        val lowerBoundInPreviousRound: T? = lowerBoundReference.getAndSet(lowerBound)
        if (input.isSynthetic) {
            // Handle synthetic offset edge-case, which always needs to run.
            // Debezium needs to run to generate the full state, which might include schema history.
            log.info { "Current offset is synthetic." }
            return listOf(partitionReader)
        }
        if (upperBound <= lowerBound) {
            // Handle completion due to reaching the WAL position upper bound.
            log.info {
                "Current position '$lowerBound' equals or exceeds target position '$upperBound'."
            }
            return emptyList()
        }
        if (lowerBoundInPreviousRound != null && lowerBound <= lowerBoundInPreviousRound) {
            // Handle completion due to stalling.
            log.info {
                "Current position '$lowerBound' has not increased in the last round, " +
                    "prior to which is was '$lowerBoundInPreviousRound'."
            }
            return emptyList()
        }
        // Handle common case.
        log.info { "Current position '$lowerBound' does not exceed target position '$upperBound'." }
        return listOf(partitionReader)
    }

    companion object {
        var CDCNeedsRestart: Boolean = false
    }
}
