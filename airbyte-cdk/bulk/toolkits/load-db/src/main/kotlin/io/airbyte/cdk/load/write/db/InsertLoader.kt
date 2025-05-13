/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.db

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.write.LoadStrategy

/**
 * [InsertLoader] is for the use case where the destination connector builds an insert query (or
 * specialized API call, a la BiqQuery) in one step, then executes the queries/requests in parallel
 * in a second step. This is different from [BulkLoader], which streams into object storage before
 * bulk loading into a table.
 *
 * The assumption is that the first step is CPU bound and the second step is IO bound, so the
 * connector dev will want to tune each step separately given the available resources.
 *
 * Note that this precludes cases where the insert query is built in a streaming fashion via an open
 * shared connection. [io.airbyte.cdk.load.write.DirectLoader] is probably a better fit for those
 * cases (for now).
 *
 * The type parameter [Q] is the client-provided type containing the accumulated records for
 * execution.
 *
 * The [InsertLoader.createAccumulator] method will be called once per batch per stream per
 * partition. A batch starts the first time a record is seen for a stream and ends either at the end
 * of the stream or when [InsertLoaderRequestBuilder.accept] returns an
 * [InsertLoaderRequestBuilder.Request].
 *
 * This means:
 * - The first time a record is seen for a stream, [InsertLoader.createAccumulator] is called,
 * - Then [InsertLoaderRequestBuilder.accept] is called, for that record and all subsequent records,
 * until it returns an [InsertLoaderRequestBuilder.Request]
 * - After a request is returned, the accumulator is discarded, and a new one is created only if new
 * data is seen for that stream, at which point the process repeats.
 * - If the framework sees end-of-stream or otherwise determines that work needs to be flushed, AND
 * if at least one record has been seen for that batch, [InsertLoaderRequestBuilder.finish] is
 * called, which must return an input. (After this, the accumulator is discarded and will be
 * recreated only if more data is seen for that stream.)
 *
 * Each request will result in a call to [InsertLoaderRequest.submit]. The call will be made async
 * relative to the building of requests. The ordering of the calls depends on the partitioning
 * strategy (see below).
 *
 * The number of parallel running accumulators is determined by [InsertLoader.numRequestBuilders].
 * The partitioning strategy is determined by [InsertLoader.partitioningStrategy].
 *
 * - [InsertLoader.PartitioningStrategy.ByStream] means that all data for a given stream will be
 * sent to the same partition. All calls to accept for that stream will occur in order, and all
 * queries for that stream will be submitted in order.
 * - [InsertLoader.PartitioningStrategy.ByPrimaryKey] means that records will be split on the
 * primary key (if available) and sent to different partitions. All calls to accept/submit for the
 * same primary key will occur in order, but calls for different primary keys my occur in parallel.
 * In the absence of a primary key, this will fall back to random.
 * - [InsertLoader.PartitioningStrategy.Random] means that all records for any key/stream will be
 * distributed randomly, and all queries will be executed in parallel.
 *
 * The default partitioning strategy is [InsertLoader.PartitioningStrategy.ByStream].
 *
 * The number of threads (coroutines) devoted to building requests is determined by
 * [InsertLoader.numRequestBuilders] (default 2) and the number devoted to executing them by
 * [InsertLoader.numRequestExecutors] (default 2). Note that unless the partitioning strategy is
 * [InsertLoader.PartitioningStrategy.Random] there is no value in having more executors than
 * builders.
 *
 * Memory management is handled by the framework. The connector dev just needs to specify the max
 * ratio of available memory to use for requests in [InsertLoader.maxMemoryRatioToUseForRequests]
 * and the expected request size in [InsertLoader.estimatedByteSizePerRequest]. The framework will
 * determine queue capacity and maximum request size accordingly. However, the framework assumes
 * that the accumulator will track its total size internally and return a request when that size has
 * been met. The argument `maxRequestSizeBytes` is passed containing a suggested maximum size for
 * the request. This will be <= [InsertLoader.estimatedByteSizePerRequest] and should be respected.
 *
 * If the dev is managing a shared resource like a connection pool, they can safely use a
 * [kotlinx.coroutines.sync.Semaphore] or similar construct to suspend execution across threads. (
 * [submit] is a suspend function for this reason.) This is true even if the request is sharing a
 * resource with the stream initialization or teardown.
 */
interface InsertLoaderRequest {
    suspend fun submit()
}

interface InsertLoaderRequestBuilder<Q : InsertLoaderRequest> : AutoCloseable {
    sealed interface InsertAcceptResult<Q>
    class NoOutput<Q> : InsertAcceptResult<Q>
    data class Request<Q>(val request: Q) : InsertAcceptResult<Q>

    fun accept(record: DestinationRecordRaw, maxRequestSizeBytes: Long): InsertAcceptResult<Q>
    fun finish(): Request<Q>
}

interface InsertLoader<Q : InsertLoaderRequest> : LoadStrategy {
    override val inputPartitions: Int
        get() = numRequestBuilders

    enum class PartitioningStrategy {
        ByStream,
        ByPrimaryKey,
        Random
    }

    val numRequestBuilders: Int
        get() = 2
    val numRequestExecutors: Int
        get() = 2
    val estimatedByteSizePerRequest: Long
        get() = 10 * 1024 * 1024 // 10MB
    val maxMemoryRatioToUseForRequests: Double
        get() = 0.6
    val partitioningStrategy: PartitioningStrategy
        get() = PartitioningStrategy.ByStream

    fun createAccumulator(
        streamDescriptor: DestinationStream.Descriptor,
        partition: Int
    ): InsertLoaderRequestBuilder<Q>
}
