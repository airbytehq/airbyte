/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import com.google.common.base.Preconditions
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.util.Optional
import java.util.UUID
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentMap

/**
 * Track the number of flush workers (and their size) that are currently running for a given stream.
 */
class RunningFlushWorkers {
    private val streamToFlushWorkerToBatchSize:
        ConcurrentMap<StreamDescriptor, ConcurrentMap<UUID, Optional<Long>>> =
        ConcurrentHashMap()

    /**
     * Call this when a worker starts flushing a stream.
     *
     * @param stream the stream that is being flushed
     * @param flushWorkerId flush worker id
     */
    fun trackFlushWorker(
        stream: StreamDescriptor,
        flushWorkerId: UUID,
    ) {
        streamToFlushWorkerToBatchSize
            .computeIfAbsent(
                stream,
            ) {
                ConcurrentHashMap()
            }
            .computeIfAbsent(
                flushWorkerId,
            ) {
                Optional.empty()
            }
    }

    /**
     * Call this when a worker completes flushing a stream.
     *
     * @param stream the stream that was flushed
     * @param flushWorkerId flush worker id
     */
    fun completeFlushWorker(
        stream: StreamDescriptor,
        flushWorkerId: UUID,
    ) {
        Preconditions.checkState(
            streamToFlushWorkerToBatchSize.containsKey(stream) &&
                streamToFlushWorkerToBatchSize[stream]!!.containsKey(flushWorkerId),
            "Cannot complete flush worker for stream that has not started.",
        )
        streamToFlushWorkerToBatchSize[stream]!!.remove(flushWorkerId)
        if (streamToFlushWorkerToBatchSize[stream]!!.isEmpty()) {
            streamToFlushWorkerToBatchSize.remove(stream)
        }
    }

    /**
     * When a worker gets a batch of records, register its size so that it can be referenced for
     * estimating how many records will be left in the queue after the batch is done.
     *
     * @param stream stream
     * @param batchSize batch size
     */
    fun registerBatchSize(
        stream: StreamDescriptor,
        flushWorkerId: UUID,
        batchSize: Long,
    ) {
        Preconditions.checkState(
            (streamToFlushWorkerToBatchSize.containsKey(stream) &&
                streamToFlushWorkerToBatchSize[stream]!!.containsKey(flushWorkerId)),
            "Cannot register a batch size for a flush worker that has not been initialized",
        )
        streamToFlushWorkerToBatchSize[stream]!![flushWorkerId] = Optional.of(batchSize)
    }

    /**
     * For a stream get how many bytes are in each running worker. If the worker doesn't have a
     * batch yet, return empty optional.
     *
     * @param stream stream
     * @return bytes in batches currently being processed
     */
    fun getSizesOfRunningWorkerBatches(stream: StreamDescriptor): List<Optional<Long>> {
        return ArrayList(
            streamToFlushWorkerToBatchSize.getOrDefault(stream, ConcurrentHashMap()).values,
        )
    }
}
