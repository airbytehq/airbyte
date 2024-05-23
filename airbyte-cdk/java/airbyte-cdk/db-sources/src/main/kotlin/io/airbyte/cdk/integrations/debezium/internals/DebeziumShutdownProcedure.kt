/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import io.airbyte.commons.concurrency.VoidCallable
import io.airbyte.commons.lang.MoreBooleans
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.*
import java.util.function.Supplier

private val LOGGER = KotlinLogging.logger {}
/**
 * This class has the logic for shutting down Debezium Engine in graceful manner. We made it Generic
 * to allow us to write tests easily.
 */
class DebeziumShutdownProcedure<T>(
    private val sourceQueue: LinkedBlockingQueue<T>,
    private val debeziumThreadRequestClose: VoidCallable,
    private val publisherStatusSupplier: Supplier<Boolean>
) {
    private val targetQueue = LinkedBlockingQueue<T>()
    private val executorService: ExecutorService
    private var exception: Throwable? = null
    private var hasTransferThreadShutdown: Boolean

    init {
        this.hasTransferThreadShutdown = false
        this.executorService =
            Executors.newSingleThreadExecutor { r: Runnable ->
                val thread = Thread(r, "queue-data-transfer-thread")
                thread.uncaughtExceptionHandler =
                    Thread.UncaughtExceptionHandler { _: Thread, e: Throwable -> exception = e }
                thread
            }
    }

    private fun transfer(): Runnable {
        return Runnable {
            while (!sourceQueue.isEmpty() || !hasEngineShutDown()) {
                try {
                    val event = sourceQueue.poll(100, TimeUnit.MILLISECONDS)
                    if (event != null) {
                        targetQueue.put(event)
                    }
                } catch (e: InterruptedException) {
                    Thread.currentThread().interrupt()
                    throw RuntimeException(e)
                }
            }
        }
    }

    private fun hasEngineShutDown(): Boolean {
        return MoreBooleans.isTruthy(publisherStatusSupplier.get())
    }

    private fun initiateTransfer() {
        executorService.execute(transfer())
    }

    val recordsRemainingAfterShutdown: LinkedBlockingQueue<T>
        get() {
            if (!hasTransferThreadShutdown) {
                LOGGER.warn {
                    "Queue transfer thread has not shut down, some records might be missing."
                }
            }
            return targetQueue
        }

    /**
     * This method triggers the shutdown of Debezium Engine. When we trigger Debezium shutdown, the
     * main thread pauses, as a result we stop reading data from the [sourceQueue] and since the
     * queue is of fixed size, if it's already at capacity, Debezium won't be able to put remaining
     * records in the queue. So before we trigger Debezium shutdown, we initiate a transfer of the
     * records from the [sourceQueue] to a new queue i.e. [targetQueue]. This allows Debezium to
     * continue to put records in the [sourceQueue] and once done, gracefully shutdown. After the
     * shutdown is complete we just have to read the remaining records from the [targetQueue]
     */
    fun initiateShutdownProcedure() {
        if (hasEngineShutDown()) {
            LOGGER.info { "Debezium Engine has already shut down." }
            return
        }
        var exceptionDuringEngineClose: Exception? = null
        try {
            initiateTransfer()
            debeziumThreadRequestClose.call()
        } catch (e: Exception) {
            exceptionDuringEngineClose = e
            throw RuntimeException(e)
        } finally {
            try {
                shutdownTransferThread()
            } catch (e: Exception) {
                if (exceptionDuringEngineClose != null) {
                    e.addSuppressed(exceptionDuringEngineClose)
                    throw e
                }
            }
        }
    }

    private fun shutdownTransferThread() {
        executorService.shutdown()
        var terminated = false
        while (!terminated) {
            try {
                terminated = executorService.awaitTermination(5, TimeUnit.MINUTES)
            } catch (e: InterruptedException) {
                Thread.currentThread().interrupt()
                throw RuntimeException(e)
            }
        }
        hasTransferThreadShutdown = true
        if (exception != null) {
            throw RuntimeException(exception)
        }
    }

    companion object {}
}
