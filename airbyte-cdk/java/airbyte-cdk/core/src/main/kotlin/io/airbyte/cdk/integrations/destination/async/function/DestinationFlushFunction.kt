/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async.function

import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.util.stream.Stream
import kotlin.math.max

/**
 * An interface meant to be used with [FlushWorkers].
 *
 * A destination instructs workers how to write data by specifying [.flush]. This keeps the worker
 * abstraction generic and reusable.
 *
 * e.g. A database destination's flush function likely involves parsing the stream into SQL
 * statements.
 *
 * There are 2 different destination types as of this writing:
 *
 * * 1. Destinations that upload files. This includes warehouses and databases.
 * * 2. Destinations that upload data streams. This mostly includes various Cloud storages. This
 * will include reverse-ETL in the future
 *
 * In both cases, the simplest way to model the incoming data is as a stream.
 */
interface DestinationFlushFunction {
    /**
     * Flush a batch of data to the destination.
     *
     * @param streamDescriptor the Airbyte stream the data stream belongs to
     * @param stream a bounded [AirbyteMessage] stream ideally of [.getOptimalBatchSizeBytes] size
     * @throws Exception
     */
    @Throws(Exception::class)
    fun flush(
        streamDescriptor: StreamDescriptor,
        stream: Stream<PartialAirbyteMessage>,
    )

    /**
     * When invoking [.flush], best effort attempt to invoke flush with a batch of this size. Useful
     * for Destinations that have optimal flush batch sizes.
     *
     * If you increase this, make sure that [.getQueueFlushThresholdBytes] is larger than this
     * value. Otherwise we may trigger flushes before reaching the optimal batch size.
     *
     * @return the optimal batch size in bytes
     */
    val optimalBatchSizeBytes: Long

    val queueFlushThresholdBytes: Long
        /**
         * This value should be at least as high as [.getOptimalBatchSizeBytes]. It's used by
         * [DetectStreamToFlush] as part of deciding when a stream needs to be flushed. I'm being
         * vague because I don't understand the specifics.
         */
        get() = max((10 * 1024 * 1024).toDouble(), optimalBatchSizeBytes.toDouble()).toLong()
}
