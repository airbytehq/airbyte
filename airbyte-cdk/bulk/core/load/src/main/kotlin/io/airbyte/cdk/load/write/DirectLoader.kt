/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue

/**
 * [DirectLoader] is for the use case where records are loaded directly into the destination or
 * added incrementally via a 3rd party library (eg, Iceberg)
 *
 * One direct loader will be created per batch of records per stream (optionally: and per part).
 *
 * A batch is a series of records that are loaded together, processed in the order they were
 * received. Its end is user-defined, or forced at the end of the stream.
 *
 * To enable, set [airbyte.destination.core.load-pipeline.strategy=direct] in the connector's
 * application.yaml.
 *
 * [accept] will be called once per record until it returns [Complete]. If end-of-stream is reached
 * before [accept] returns [Complete], [finish] will be called. [finish] might also be called at
 * other times by the CDK to force work to be flushed and start a new batch. Implementors should
 * always forward whatever work is in progress in [finish], as [accept] will not be called again for
 * the same batch.
 *
 * [close] will be called once at the end of the batch, after the last call to [accept] or [finish],
 * or if the sync fails. Afterward the loader will be discarded and a new one will be created for
 * the next batch if/a.
 *
 * The end of a record batch is determined by end of stream or when the [accept] method returns
 * [Complete]. If [Complete.persisted] is true, the batch is considered persisted and completion
 * will be acked to the platform. (If the sync fails after this point, the platform will not retry
 * the batch.) Otherwise, completion will not be acked until the stream is closed.
 *
 * By default, there is one part per stream, but this can be changed by setting
 * [airbyte.destination.core.load-pipeline.input-parts] in the connector's application.yaml.
 *
 * By default, the work is partitioned by stream (ie, even with 2 parts, only one batch for Stream A
 * will ever be in progress at a time, so increased concurrency will only help if streams are
 * interleaved). To distribute the work differently, implement
 * [io.airbyte.cdk.load.pipeline.InputPartitioner].
 */
interface DirectLoader : AutoCloseable {
    sealed interface DirectLoadResult
    data object Incomplete : DirectLoadResult
    data class Complete(val persisted: Boolean) : DirectLoadResult

    fun accept(record: DestinationRecordAirbyteValue): DirectLoadResult
    fun finish(): Complete
}

abstract class DirectLoaderFactory<T : DirectLoader> {
    abstract fun create(stream: DestinationStream.Descriptor, part: Int): T
}
