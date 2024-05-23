/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.util.concurrent

import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility
import io.airbyte.commons.stream.AirbyteStreamStatusHolder
import io.airbyte.commons.stream.StreamStatusUtils
import io.airbyte.commons.util.AutoCloseableIterator
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.AirbyteMessage
import java.util.*
import java.util.concurrent.*
import java.util.concurrent.ThreadPoolExecutor.AbortPolicy
import java.util.function.Consumer
import kotlin.math.min
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * [Consumer] implementation that consumes [AirbyteMessage] records from each provided stream
 * concurrently.
 *
 * The consumer calculates the parallelism based on the provided requested parallelism. If the
 * requested parallelism is greater than zero, the minimum value between the requested parallelism
 * and the maximum number of allowed threads is chosen as the parallelism value. Otherwise, the
 * minimum parallelism value is selected. This is to avoid issues with attempting to execute with a
 * parallelism value of zero, which is not allowed by the underlying [ExecutorService].
 *
 * This consumer will capture any raised exceptions during execution of each stream. Anu exceptions
 * are stored and made available by calling the [.getException] method.
 */
class ConcurrentStreamConsumer(
    streamConsumer: Consumer<AutoCloseableIterator<AirbyteMessage>>,
    requestedParallelism: Int
) : Consumer<Collection<AutoCloseableIterator<AirbyteMessage>>>, AutoCloseable {
    private val executorService: ExecutorService
    private val exceptions: MutableList<Exception>
    /**
     * the parallelism value that will be used by this consumer to execute the consumption of data
     * from the provided streams in parallel.
     *
     * @return The parallelism value of this consumer.
     */
    val parallelism: Int
    private val streamConsumer: Consumer<AutoCloseableIterator<AirbyteMessage>>
    private val streamStatusEmitter =
        Optional.of(
            Consumer { obj: AirbyteStreamStatusHolder ->
                AirbyteTraceMessageUtility.emitStreamStatusTrace(obj)
            }
        )

    /**
     * Constructs a new [ConcurrentStreamConsumer] that will use the provided stream consumer to
     * execute each stream submitted to the [&lt;][.accept] method of this consumer. Streams
     * submitted to the [&lt;][.accept] method will be converted to a [Runnable] and executed on an
     * [ExecutorService] configured by this consumer to ensure concurrent execution of each stream.
     *
     * @param streamConsumer The [Consumer] that accepts streams as an [AutoCloseableIterator].
     * @param requestedParallelism The requested amount of parallelism that will be used as a hint
     * to determine the appropriate number of threads to execute concurrently.
     */
    init {
        this.parallelism = computeParallelism(requestedParallelism)
        this.executorService = createExecutorService(parallelism)
        this.exceptions = ArrayList()
        this.streamConsumer = streamConsumer
    }

    override fun accept(streams: Collection<AutoCloseableIterator<AirbyteMessage>>) {
        /*
         * Submit the provided streams to the underlying executor service for concurrent execution. This
         * thread will track the status of each stream as well as consuming all messages produced from each
         * stream, passing them to the provided message consumer for further processing. Any exceptions
         * raised within the thread will be captured and exposed to the caller.
         */
        val futures: Collection<CompletableFuture<Void>> =
            streams
                .map { stream: AutoCloseableIterator<AirbyteMessage> ->
                    ConcurrentStreamRunnable(stream, this)
                }
                .map { runnable: ConcurrentStreamRunnable ->
                    CompletableFuture.runAsync(runnable, executorService)
                }

        /*
         * Wait for the submitted streams to complete before returning. This uses the join() method to allow
         * all streams to complete even if one or more encounters an exception.
         */
        LOGGER.debug("Waiting for all streams to complete....")
        CompletableFuture.allOf(*futures.toTypedArray<CompletableFuture<*>>()).join()
        LOGGER.debug("Completed consuming from all streams.")
    }

    val exception: Optional<Exception>
        /**
         * Returns the first captured [Exception].
         *
         * @return The first captured [Exception] or an empty [Optional] if no exceptions were
         * captured during execution.
         */
        get() =
            if (!exceptions.isEmpty()) {
                Optional.of(exceptions[0])
            } else {
                Optional.empty()
            }

    /**
     * Returns the list of exceptions captured during execution of the streams, if any.
     *
     * @return The collection of captured exceptions or an empty list.
     */
    fun getExceptions(): List<Exception> {
        return Collections.unmodifiableList(exceptions)
    }

    /**
     * Calculates the parallelism based on the requested parallelism. If the requested parallelism
     * is greater than zero, the minimum value between the parallelism and the maximum parallelism
     * is chosen as the parallelism count. Otherwise, the minimum parallelism is selected. This is
     * to avoid issues with attempting to create an executor service with a thread pool size of 0,
     * which is not allowed.
     *
     * @param requestedParallelism The requested parallelism.
     * @return The selected parallelism based on the factors outlined above.
     */
    private fun computeParallelism(requestedParallelism: Int): Int {
        /*
         * Selects the default thread pool size based on the provided value via an environment variable or
         * the number of available processors if the environment variable is not set/present. This is to
         * ensure that we do not over-parallelize unless requested explicitly.
         */
        val defaultPoolSize =
            Optional.ofNullable(System.getenv("DEFAULT_CONCURRENT_STREAM_CONSUMER_THREADS"))
                .map { s: String -> s.toInt() }
                .orElseGet { Runtime.getRuntime().availableProcessors() }
        LOGGER.debug(
            "Default parallelism: {}, Requested parallelism: {}",
            defaultPoolSize,
            requestedParallelism
        )
        val parallelism =
            min(
                    defaultPoolSize.toDouble(),
                    (if (requestedParallelism > 0) requestedParallelism else 1).toDouble()
                )
                .toInt()
        LOGGER.debug("Computed concurrent stream consumer parallelism: {}", parallelism)
        return parallelism
    }

    /**
     * Creates the [ExecutorService] that will be used by the consumer to consume from the provided
     * streams in parallel.
     *
     * @param nThreads The number of threads to execute concurrently.
     * @return The configured [ExecutorService].
     */
    private fun createExecutorService(nThreads: Int): ExecutorService {
        return ThreadPoolExecutor(
            nThreads,
            nThreads,
            0L,
            TimeUnit.MILLISECONDS,
            LinkedBlockingQueue(),
            ConcurrentStreamThreadFactory(),
            AbortPolicy()
        )
    }

    /**
     * Executes the stream by providing it to the configured [.streamConsumer].
     *
     * @param stream The stream to be executed.
     */
    private fun executeStream(stream: AutoCloseableIterator<AirbyteMessage>) {
        try {
            stream.use {
                stream.airbyteStream.ifPresent { s: AirbyteStreamNameNamespacePair ->
                    LOGGER.debug("Consuming from stream {}...", s)
                }
                StreamStatusUtils.emitStartStreamStatus(stream, streamStatusEmitter)
                streamConsumer.accept(stream)
                StreamStatusUtils.emitCompleteStreamStatus(stream, streamStatusEmitter)
                stream.airbyteStream.ifPresent { s: AirbyteStreamNameNamespacePair ->
                    LOGGER.debug("Consumption from stream {} complete.", s)
                }
            }
        } catch (e: Exception) {
            stream.airbyteStream.ifPresent { s: AirbyteStreamNameNamespacePair ->
                LOGGER.error("Unable to consume from stream {}.", s, e)
            }
            StreamStatusUtils.emitIncompleteStreamStatus(stream, streamStatusEmitter)
            exceptions.add(e)
        }
    }

    @Throws(Exception::class)
    override fun close() {
        // Block waiting for the executor service to close
        executorService.shutdownNow()
        executorService.awaitTermination(30, TimeUnit.SECONDS)
    }

    /** Custom [ThreadFactory] that names the threads used to concurrently execute streams. */
    private class ConcurrentStreamThreadFactory : ThreadFactory {
        override fun newThread(r: Runnable): Thread {
            val thread = Thread(r)
            if (r is ConcurrentStreamRunnable) {
                val stream = r.stream
                if (stream.airbyteStream.isPresent) {
                    val airbyteStream = stream.airbyteStream.get()
                    thread.name =
                        String.format(
                            "%s-%s-%s",
                            CONCURRENT_STREAM_THREAD_NAME,
                            airbyteStream.namespace,
                            airbyteStream.name
                        )
                } else {
                    thread.name = CONCURRENT_STREAM_THREAD_NAME
                }
            } else {
                thread.name = CONCURRENT_STREAM_THREAD_NAME
            }
            return thread
        }
    }

    /**
     * Custom [Runnable] that exposes the stream for thread naming purposes.
     *
     * @param stream The stream that is part of the [Runnable] execution.
     * @param consumer The [ConcurrentStreamConsumer] that will execute the stream.
     */
    private class ConcurrentStreamRunnable(
        val stream: AutoCloseableIterator<AirbyteMessage>,
        val consumer: ConcurrentStreamConsumer
    ) : Runnable {
        override fun run() {
            consumer.executeStream(stream)
        }
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(ConcurrentStreamConsumer::class.java)

        /** Name of threads spawned by the [ConcurrentStreamConsumer]. */
        const val CONCURRENT_STREAM_THREAD_NAME: String = "concurrent-stream-thread"
    }
}
