/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import com.google.common.annotations.VisibleForTesting
import com.google.common.base.Preconditions
import com.google.common.base.Strings
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer
import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.cdk.integrations.destination.async.buffers.BufferEnqueue
import io.airbyte.cdk.integrations.destination.async.buffers.BufferManager
import io.airbyte.cdk.integrations.destination.async.deser.DeserializationUtil
import io.airbyte.cdk.integrations.destination.async.deser.IdentityDataTransformer
import io.airbyte.cdk.integrations.destination.async.deser.StreamAwareDataTransformer
import io.airbyte.cdk.integrations.destination.async.function.DestinationFlushFunction
import io.airbyte.cdk.integrations.destination.async.partial_messages.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.async.state.FlushFailure
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnCloseFunction
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnStartFunction
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.util.Optional
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentMap
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicLong
import java.util.function.Consumer
import java.util.stream.Collectors
import kotlin.jvm.optionals.getOrNull
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * Async version of the
 * [io.airbyte.cdk.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer].
 *
 * With this consumer, a destination is able to continue reading records until hitting the maximum
 * memory limit governed by [GlobalMemoryManager]. Record writing is decoupled via [FlushWorkers].
 * See the other linked class for more detail.
 */
class AsyncStreamConsumer
@VisibleForTesting
constructor(
    outputRecordCollector: Consumer<AirbyteMessage?>,
    private val onStart: OnStartFunction,
    private val onClose: OnCloseFunction,
    flusher: DestinationFlushFunction,
    private val catalog: ConfiguredAirbyteCatalog,
    private val bufferManager: BufferManager,
    private val flushFailure: FlushFailure,
    private val defaultNamespace: Optional<String>,
    workerPool: ExecutorService,
    private val dataTransformer: StreamAwareDataTransformer,
    private val deserializationUtil: DeserializationUtil,
) : SerializedAirbyteMessageConsumer {
    private val bufferEnqueue: BufferEnqueue = bufferManager.bufferEnqueue
    private val flushWorkers: FlushWorkers =
        FlushWorkers(
            bufferManager.bufferDequeue,
            flusher,
            outputRecordCollector,
            flushFailure,
            bufferManager.stateManager,
            workerPool,
        )
    private val streamNames: Set<StreamDescriptor> =
        StreamDescriptorUtils.fromConfiguredCatalog(
            catalog,
        )

    // Note that this map will only be populated for streams with nonzero records.
    private val recordCounts: ConcurrentMap<StreamDescriptor, AtomicLong> = ConcurrentHashMap()

    private var hasStarted = false
    private var hasClosed = false
    private var hasFailed = false

    // This is to account for the references when deserialization to a PartialAirbyteMessage. The
    // calculation is as follows:
    // PartialAirbyteMessage (4) + Max( PartialRecordMessage(4), PartialStateMessage(6)) with
    // PartialStateMessage being larger with more nested objects within it. Using 8 bytes as we
    // assumed
    // a 64 bit JVM.
    private val PARTIAL_DESERIALIZE_REF_BYTES: Int = 10 * 8

    constructor(
        outputRecordCollector: Consumer<AirbyteMessage?>,
        onStart: OnStartFunction,
        onClose: OnCloseFunction,
        flusher: DestinationFlushFunction,
        catalog: ConfiguredAirbyteCatalog,
        bufferManager: BufferManager,
        defaultNamespace: Optional<String>,
    ) : this(
        outputRecordCollector,
        onStart,
        onClose,
        flusher,
        catalog,
        bufferManager,
        FlushFailure(),
        defaultNamespace,
    )

    constructor(
        outputRecordCollector: Consumer<AirbyteMessage?>,
        onStart: OnStartFunction,
        onClose: OnCloseFunction,
        flusher: DestinationFlushFunction,
        catalog: ConfiguredAirbyteCatalog,
        bufferManager: BufferManager,
        defaultNamespace: Optional<String>,
        dataTransformer: StreamAwareDataTransformer,
    ) : this(
        outputRecordCollector,
        onStart,
        onClose,
        flusher,
        catalog,
        bufferManager,
        FlushFailure(),
        defaultNamespace,
        Executors.newFixedThreadPool(5),
        dataTransformer,
        DeserializationUtil(),
    )

    constructor(
        outputRecordCollector: Consumer<AirbyteMessage?>,
        onStart: OnStartFunction,
        onClose: OnCloseFunction,
        flusher: DestinationFlushFunction,
        catalog: ConfiguredAirbyteCatalog,
        bufferManager: BufferManager,
        defaultNamespace: Optional<String>,
        workerPool: ExecutorService,
    ) : this(
        outputRecordCollector,
        onStart,
        onClose,
        flusher,
        catalog,
        bufferManager,
        FlushFailure(),
        defaultNamespace,
        workerPool,
        IdentityDataTransformer(),
        DeserializationUtil(),
    )

    @VisibleForTesting
    constructor(
        outputRecordCollector: Consumer<AirbyteMessage?>,
        onStart: OnStartFunction,
        onClose: OnCloseFunction,
        flusher: DestinationFlushFunction,
        catalog: ConfiguredAirbyteCatalog,
        bufferManager: BufferManager,
        flushFailure: FlushFailure,
        defaultNamespace: Optional<String>,
    ) : this(
        outputRecordCollector,
        onStart,
        onClose,
        flusher,
        catalog,
        bufferManager,
        flushFailure,
        defaultNamespace,
        Executors.newFixedThreadPool(5),
        IdentityDataTransformer(),
        DeserializationUtil(),
    )

    @Throws(Exception::class)
    override fun start() {
        Preconditions.checkState(!hasStarted, "Consumer has already been started.")
        hasStarted = true

        flushWorkers.start()

        LOGGER.info("{} started.", AsyncStreamConsumer::class.java)
        onStart.call()
    }

    @Throws(Exception::class)
    override fun accept(
        messageString: String,
        sizeInBytes: Int,
    ) {
        Preconditions.checkState(hasStarted, "Cannot accept records until consumer has started")
        propagateFlushWorkerExceptionIfPresent()
        /*
         * intentionally putting extractStream outside the buffer manager so that if in the future we want
         * to try to use a thread pool to partially deserialize to get record type and stream name, we can
         * do it without touching buffer manager.
         */
        val message =
            deserializationUtil.deserializeAirbyteMessage(
                messageString,
                dataTransformer,
            )
        if (AirbyteMessage.Type.RECORD == message.type) {
            if (Strings.isNullOrEmpty(message.record?.namespace)) {
                message.record?.namespace = defaultNamespace.getOrNull()
            }
            validateRecord(message)

            message.record?.streamDescriptor?.let { getRecordCounter(it).incrementAndGet() }
        }
        bufferEnqueue.addRecord(
            message,
            sizeInBytes + PARTIAL_DESERIALIZE_REF_BYTES,
            defaultNamespace,
        )
    }

    @Throws(Exception::class)
    override fun close() {
        Preconditions.checkState(hasStarted, "Cannot close; has not started.")
        Preconditions.checkState(!hasClosed, "Has already closed.")
        hasClosed = true

        // assume closing upload workers will flush all accepted records.
        // we need to close the workers before closing the bufferManagers (and underlying buffers)
        // or we risk in-memory data.
        flushWorkers.close()

        bufferManager.close()

        val streamSyncSummaries =
            streamNames
                .stream()
                .collect(
                    Collectors.toMap(
                        { streamDescriptor: StreamDescriptor -> streamDescriptor },
                        { streamDescriptor: StreamDescriptor ->
                            StreamSyncSummary(
                                Optional.of(getRecordCounter(streamDescriptor).get()),
                            )
                        },
                    ),
                )
        onClose.accept(hasFailed, streamSyncSummaries)

        // as this throws an exception, we need to be after all other close functions.
        propagateFlushWorkerExceptionIfPresent()
        LOGGER.info("{} closed", AsyncStreamConsumer::class.java)
    }

    private fun getRecordCounter(streamDescriptor: StreamDescriptor): AtomicLong {
        return recordCounts.computeIfAbsent(
            streamDescriptor,
        ) {
            AtomicLong()
        }
    }

    @Throws(Exception::class)
    private fun propagateFlushWorkerExceptionIfPresent() {
        if (flushFailure.isFailed()) {
            hasFailed = true
            throw flushFailure.exception
        }
    }

    private fun validateRecord(message: PartialAirbyteMessage) {
        val streamDescriptor =
            StreamDescriptor()
                .withNamespace(message.record?.namespace)
                .withName(message.record?.stream)
        // if stream is not part of list of streams to sync to then throw invalid stream exception
        if (!streamNames.contains(streamDescriptor)) {
            throwUnrecognizedStream(catalog, message)
        }
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(AsyncStreamConsumer::class.java)

        private fun throwUnrecognizedStream(
            catalog: ConfiguredAirbyteCatalog?,
            message: PartialAirbyteMessage,
        ) {
            throw IllegalArgumentException(
                String.format(
                    "Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
                    Jsons.serialize(catalog),
                    Jsons.serialize(message),
                ),
            )
        }
    }
}
