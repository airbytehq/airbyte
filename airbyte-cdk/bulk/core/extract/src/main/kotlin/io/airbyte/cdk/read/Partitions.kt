/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.read.PartitionsCreator.TryAcquireResourcesStatus

/**
 * [PartitionsCreatorFactory] must be implemented by each source connector and serves as the
 * entrypoint to how READ operations are executed for that connector, via the [PartitionsCreator]
 * and [PartitionReader] instances which are ultimately created by it.
 */
fun interface PartitionsCreatorFactory {
    /**
     * Returns a [PartitionsCreator] which will cause the READ to advance for this particular [feed]
     * when possible. A [StateQuerier] is provided to obtain the current [OpaqueStateValue] for this
     * [feed] but may also be used to peek at the state of other [Feed]s. This may be useful for
     * synchronizing the READ for this [feed] by waiting for other [Feed]s to reach a desired state
     * before proceeding; the waiting may be triggered by [PartitionsCreator.tryAcquireResources] or
     * [PartitionReader.tryAcquireResources].
     *
     * Returns null when the factory is unable to generate a [PartitionsCreator]. This causes
     * another factory to be used instead.
     */
    fun make(
        stateQuerier: StateQuerier,
        feed: Feed,
    ): PartitionsCreator?
}

/**
 * A [PartitionsCreator] breaks down a [Feed] (a stream, or some global data feed) into zero, one or
 * more partitions. Each partition is defined and read by a [PartitionReader] instance. These
 * execute concurrently, but are joined serially because the state checkpoints need to appear in
 * sequence.
 *
 * - zero partitions means that there is no more records to be read for this [Feed];
 * - one partition effectively means that the records will be read serially;
 * - many partitions therefore involves some concurrency within the [Feed].
 */
interface PartitionsCreator {
    /**
     * Called before [run] to try to acquire all the resources required for its execution. These may
     * be, but are not limited to:
     * - disk space,
     * - heap space,
     * - JDBC connections from a connection pool,
     * - API tokens,
     * - etc.
     *
     * The CDK is not aware of resources; resource management is the responsibility of the connector
     * implementation. Implementations of this method should not block the thread; in fact they
     * should never be slow because the invocation of [tryAcquireResources] is guarded by a lock to
     * ensure serial execution.
     *
     * This [tryAcquireResources] method may also be used to coordinate work. For example, the
     * connector may require the global [Feed] to wait until all stream [Feed]s are done.
     *
     * This method gets called multiple times.
     */
    fun tryAcquireResources(): TryAcquireResourcesStatus

    enum class TryAcquireResourcesStatus {
        READY_TO_RUN,
        RETRY_LATER,
    }

    /**
     * Creates [PartitionReader] instances.
     *
     * This method gets called at most once.
     */
    suspend fun run(): List<PartitionReader>

    /**
     * Called after [run] to release any resources acquired by [tryAcquireResources].
     *
     * This method gets called exactly once after a successful call to [tryAcquireResources].
     */
    fun releaseResources()
}

data object CreateNoPartitions : PartitionsCreator {
    override fun tryAcquireResources() = TryAcquireResourcesStatus.READY_TO_RUN

    override suspend fun run(): List<PartitionReader> = listOf()

    override fun releaseResources() {}
}

/**
 * A [PartitionReader], when executed via [run], emits records within the corresponding _partition_,
 * and completes by returning the value of the state checkpoint.
 *
 * A _partition_ is a chunk of consecutive records within a [Feed], which is either a stream or some
 * global data feed.
 */
interface PartitionReader {
    /**
     * Called before [run] to try to acquire all the resources required for its execution. These may
     * be, but are not limited to:
     * - disk space,
     * - heap space,
     * - JDBC connections from a connection pool,
     * - API tokens,
     * - etc.
     *
     * The CDK is not aware of resources; resource management is the responsibility of the connector
     * implementation. Implementations of this method should not block the thread; in fact they
     * should never be slow because the invocation of [tryAcquireResources] is guarded by a lock to
     * ensure serial execution.
     *
     * This [tryAcquireResources] method may also be used to coordinate work. For example, the
     * connector may require the global [Feed] to wait until all stream [Feed]s are done.
     *
     * This method gets called multiple times.
     */
    fun tryAcquireResources(): TryAcquireResourcesStatus

    enum class TryAcquireResourcesStatus {
        READY_TO_RUN,
        RETRY_LATER,
        // XXX: there's room here for some kind of CANCEL value which cancels all pending
        // PartitionReaders.
    }

    /**
     * Reads the corresponding partition.
     *
     * This method gets called at most once.
     *
     * This method is suspendable and may be cancelled due to a timeout. Implementations must be
     * careful to always make at least some forward progress (according to the value returned by
     * [checkpoint]) regardless of timeouts.
     */
    suspend fun run()

    /**
     * Returns the forward progress made by the execution of [run].
     *
     * The [checkpoint] method gets called exactly once after the call to [run] either completes
     * successfully or times out, and not necessarily in the same thread as [run]. The [checkpoint]
     * method does not get called if [run] is otherwise interrupted.
     */
    fun checkpoint(): PartitionReadCheckpoint

    /**
     * Called after [run] and [checkpoint] to release any resources acquired by
     * [tryAcquireResources].
     *
     * This method gets called exactly once after a successful call to [tryAcquireResources], but
     * not necessarily in the same thread as [tryAcquireResources], [run] or [checkpoint].
     */
    fun releaseResources()
}

data class PartitionReadCheckpoint(
    val opaqueStateValue: OpaqueStateValue,
    val numRecords: Long,
)
