/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import io.debezium.engine.ChangeEvent
import io.debezium.engine.DebeziumEngine
import io.debezium.engine.format.Json
import io.debezium.engine.spi.OffsetCommitPolicy
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*
import java.util.concurrent.*
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicReference

private val LOGGER = KotlinLogging.logger {}
/**
 * The purpose of this class is to initialize and spawn the debezium engine with the right
 * properties to fetch records
 */
class DebeziumRecordPublisher(private val debeziumPropertiesManager: DebeziumPropertiesManager) :
    AutoCloseable {
    private val executor: ExecutorService = Executors.newSingleThreadExecutor()
    private var engine: DebeziumEngine<ChangeEvent<String?, String?>>? = null
    private val hasClosed = AtomicBoolean(false)
    private val isClosing = AtomicBoolean(false)
    private val thrownError = AtomicReference<Throwable>()
    private val engineLatch = CountDownLatch(1)

    fun start(
        queue: BlockingQueue<ChangeEvent<String?, String?>>,
        offsetManager: AirbyteFileOffsetBackingStore,
        schemaHistoryManager: Optional<AirbyteSchemaHistoryStorage>
    ) {
        engine =
            DebeziumEngine.create(Json::class.java)
                .using(
                    debeziumPropertiesManager.getDebeziumProperties(
                        offsetManager,
                        schemaHistoryManager,
                    ),
                )
                .using(OffsetCommitPolicy.AlwaysCommitOffsetPolicy())
                .notifying { e: ChangeEvent<String?, String?> ->
                    // debezium outputs a tombstone event that has a value of null. this is an
                    // artifact of how it
                    // interacts with kafka. we want to ignore it.
                    // more on the tombstone:
                    // https://debezium.io/documentation/reference/2.2/transformations/event-flattening.html
                    if (e.value() != null) {
                        try {
                            queue.put(e)
                        } catch (ex: InterruptedException) {
                            Thread.currentThread().interrupt()
                            throw RuntimeException(ex)
                        }
                    }
                }
                .using { success: Boolean, message: String?, error: Throwable? ->
                    LOGGER.info {
                        "Debezium engine shutdown. Engine terminated successfully : $success"
                    }
                    LOGGER.info { message }
                    if (!success) {
                        if (error != null) {
                            thrownError.set(error)
                        } else {
                            // There are cases where Debezium doesn't succeed but only fills the
                            // message field.
                            // In that case, we still want to fail loud and clear
                            thrownError.set(RuntimeException(message))
                        }
                    }
                    engineLatch.countDown()
                }
                .using(
                    object : DebeziumEngine.ConnectorCallback {
                        override fun connectorStarted() {
                            LOGGER.info { "DebeziumEngine notify: connector started" }
                        }

                        override fun connectorStopped() {
                            LOGGER.info { "DebeziumEngine notify: connector stopped" }
                        }

                        override fun taskStarted() {
                            LOGGER.info { "DebeziumEngine notify: task started" }
                        }

                        override fun taskStopped() {
                            LOGGER.info { "DebeziumEngine notify: task stopped" }
                        }
                    },
                )
                .build()

        // Run the engine asynchronously ...
        executor.execute(engine)
    }

    fun hasClosed(): Boolean {
        return hasClosed.get()
    }

    @Throws(Exception::class)
    override fun close() {
        if (isClosing.compareAndSet(false, true)) {
            // consumers should assume records can be produced until engine has closed.
            if (engine != null) {
                engine!!.close()
            }

            // wait for closure before shutting down executor service
            engineLatch.await(5, TimeUnit.MINUTES)

            // shut down and await for thread to actually go down
            executor.shutdown()
            executor.awaitTermination(5, TimeUnit.MINUTES)

            // after the engine is completely off, we can mark this as closed
            hasClosed.set(true)

            if (thrownError.get() != null) {
                throw RuntimeException(thrownError.get())
            }
        }
    }

    companion object {}
}
