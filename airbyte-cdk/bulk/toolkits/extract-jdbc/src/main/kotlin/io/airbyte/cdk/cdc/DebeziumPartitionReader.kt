package io.airbyte.cdk.cdc

import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.PartitionReader

class CdcPartitionReader() : PartitionReader {
    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus {
        TODO("Not yet implemented")
        // Acquire global lock
    }

    override suspend fun run() {
        TODO("Not yet implemented")

        //1. Start debezium engine
        //2.
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

    override fun checkpoint(): PartitionReadCheckpoint {
        TODO("Not yet implemented")
    }

    override fun releaseResources() {
        TODO("Not yet implemented")
        // Release global CDC lock
    }
}
