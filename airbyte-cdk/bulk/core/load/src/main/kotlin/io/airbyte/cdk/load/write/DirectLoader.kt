/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecordRaw

/**
 * [DirectLoader] is for the use case where records are loaded directly into the destination or
 * staged in chunks with a 3rd party library (eg, Iceberg)
 *
 * One direct loader will be created per batch of records per stream (optionally: and per part). It
 * will be discarded at the end of the batch (defined below).
 *
 * A batch is a series of records that are loaded together, processed in the order they were
 * received. Its end is user-defined, or forced at the end of the stream (or if the CDK determines
 * the work needs to be flushed due to resource constraints, etc). From the implementor's POV, the
 * end is when any staged work is forwarded, after which it is safe for the CDK to acknowledge to
 * the Airbyte platform that the records have been handled. (Specifically, even after a sync failure
 * these records might not be replayed, though some may be.) If records are being pushed
 * incrementally, then there is no need to signal the end of a batch.
 *
 * To enable, declare a `@Singleton` inheriting from [DirectLoaderFactory] in your connector and set
 * the value `airbyte.destination.load-strategy` to `direct` in your
 * `src/main/resources/application-destination.yaml`
 *
 * [accept] will be called once per record until it returns [Complete]. If end-of-stream is reached
 * before [accept] returns [Complete], [finish] will be called. [finish] might also be called at
 * other times by the CDK to force work to be flushed and start a new batch. Implementors should
 * always forward whatever work is in progress in [finish], as [accept] will not be called again for
 * the same batch.
 *
 * After [accept] returns a [DirectLoader.Complete] status, or after [finish] returns, the
 * DirectLoader MUST have committed all data durably to the destination.
 *
 * [close] will be called once at the end of the batch, after the last call to [accept] or [finish],
 * or if the sync fails. Afterward the loader will be discarded and a new one will be created for
 * the next batch if more data arrives. (Note: close should only be used to do cleanup that must
 * happen even if the sync fails; it should not be used to forward work.)
 *
 * By default, there is one part per stream, but this can be changed by setting
 * [DirectLoaderFactory.inputPartitions] to a number greater than 1. Specifically, up to
 * `numWorkers` DirectLoaders will be created per stream, and each will handle a specific subset of
 * records concurrently, and each subset will be processed in order of receipt.
 *
 * By default, the work is partitioned by stream (ie, even with 2 parts, only one batch for Stream A
 * will ever be in progress at a time, so increased concurrency will only help if streams are
 * interleaved). To distribute the work differently, implement
 * [io.airbyte.cdk.load.pipeline.InputPartitioner].
 *
 * If the loaders share a fixed resource (eg, a connection pool), you can limit the number of
 * concurrent loaders with [DirectLoaderFactory.maxNumOpenLoaders]. (These will be distributed over
 * the number of input partitions, and the result must be at least 1 per partition.) This will be
 * implemented by forcing a call to `finish()` any time data is seen for the Nth + 1 loader, before
 * creating the new loader. Specifically, one loader will be created per unique key (default:
 * stream) per partition. So for a loader using the default partitioner (by stream), this will
 * result in at most num_streams unique loaders. For loaders partitioning by primary key/random/
 * round-robin, this will result in at most num_streams * num_partitions unique loaders. In both
 * cases, this will be clamped to the specified max. Meaning: syncs with a large number of
 * interleaved streams risk generating pathologically small batches, but will never break the
 * specified concurrency restrictions.
 */
interface DirectLoader : AutoCloseable {
    sealed interface DirectLoadResult
    data object Incomplete : DirectLoadResult
    data object Complete : DirectLoadResult

    /**
     * Called once per record until it returns [Complete], after which [close] is called, the loader
     * is discarded, and the records are considered processed by the platform.
     */
    suspend fun accept(record: DestinationRecordRaw): DirectLoadResult

    /**
     * Called by the CDK to force work to finish. It will only be called if the last call to
     * [accept] did not return [Complete]. After which [close] is called, the loader is discarded,
     * and the records are considered processed by the platform.
     */
    suspend fun finish()
}

interface DirectLoaderFactory<T : DirectLoader> : LoadStrategy {
    val maxNumOpenLoaders: Int?
        get() = null

    fun create(streamDescriptor: DestinationStream.Descriptor, part: Int): T
}
