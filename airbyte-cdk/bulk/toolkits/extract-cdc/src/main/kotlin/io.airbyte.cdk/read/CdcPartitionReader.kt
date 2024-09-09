/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.cdc

import io.airbyte.cdk.read.CdcPartition
import io.airbyte.cdk.read.DebeziumRecord
import io.airbyte.cdk.read.DefaultJdbcSharedState
import io.airbyte.cdk.read.JdbcPartitionReader.AcquiredResources
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.PartitionReader.TryAcquireResourcesStatus
import io.airbyte.cdk.read.cdcAware
import io.airbyte.cdk.read.cdcResourceTaker
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.debezium.engine.ChangeEvent
import io.debezium.engine.DebeziumEngine
import io.debezium.engine.format.Json
import io.debezium.engine.spi.OffsetCommitPolicy
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*
import java.util.concurrent.atomic.AtomicReference

class CdcPartitionReader<P : CdcPartition<DefaultJdbcSharedState>>(
    cdcContext: io.airbyte.cdk.read.CdcContext,
    val partition: P
) : PartitionReader, cdcAware, cdcResourceTaker {

    private val log = KotlinLogging.logger {}
    private var engine: DebeziumEngine<ChangeEvent<String?, String?>>? = null
    private val outputConsumer = cdcContext.outputConsumer
    private val propertyManager = cdcContext.propertyManager
    private val acquiredResources = AtomicReference<AcquiredResources>()

    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus {
        if (!cdcResourceAcquire()) {
            return TryAcquireResourcesStatus.RETRY_LATER
        }

        val acquiredResources: AcquiredResources =
            partition.tryAcquireResourcesForReader() ?: return TryAcquireResourcesStatus.RETRY_LATER
        this.acquiredResources.set(acquiredResources)
        return TryAcquireResourcesStatus.READY_TO_RUN
    }

    override suspend fun run() {
        engine = createDebeziumEngine()
        // TODO: Determine if debezium engine should be run asynchronously or engine stop should be
        // run asynchronously
        engine?.run()
        cdcAware.cdcRan.set(true)
    }

    override fun checkpoint(): PartitionReadCheckpoint {
        TODO("Not yet implemented")
    }

    override fun releaseResources() {
        acquiredResources.getAndSet(null)?.close()
        // Release global CDC lock
    }

    fun processDebeziumMessage(changeEvent: ChangeEvent<String?, String?>) {
        log.info { changeEvent }
        TODO("Not yet implemented")
    }

    fun convertToAirbyteMessage(record: DebeziumRecord): AirbyteRecordMessage {
        // TODO : Convert event to an airbyte message
        log.info { record }
        return AirbyteRecordMessage()
    }

    fun createDebeziumEngine(): DebeziumEngine<ChangeEvent<String?, String?>>? {
        return DebeziumEngine.create(Json::class.java)
            .using(propertyManager.get())
            .using(OffsetCommitPolicy.AlwaysCommitOffsetPolicy())
            .notifying { event: ChangeEvent<String?, String?> ->
                if (event.value() == null) {
                    return@notifying
                }
                val record = DebeziumRecord(Jsons.deserialize(event.value()))
                // TODO : Migrate over all of the timeout/heartbeat timeout logic
                if (!record.isHeartbeat) {
                    outputConsumer.accept(convertToAirbyteMessage(record))
                }
                if (reachedTargetPosition(record)) {
                    // Stop if we've reached the upper bound.
                    if (record.isHeartbeat) {
                        requestClose(
                            "Closing: Heartbeat indicates sync is done by reaching the target position",
                            DebeziumCloseReason.HEARTBEAT_REACHED_TARGET_POSITION
                        )
                    } else {
                        requestClose(
                            "Closing: Heartbeat indicates sync is not progressing",
                            DebeziumCloseReason.HEARTBEAT_NOT_PROGRESSING
                        )
                    }
                }
            }
            .using { success: Boolean, message: String?, error: Throwable? ->
                log.info { "Debezium engine shutdown. Engine terminated successfully : $success" }
                log.info { message }
                if (!success) {
                    if (error != null) {
                        log.info { "Debezium failed with: $error" }
                    } else {
                        // There are cases where Debezium doesn't succeed but only fills the
                        // message field.
                        // In that case, we still want to fail loud and clear
                        log.info { "Debezium failed with: $message" }
                    }
                }
            }
            .using(
                object : DebeziumEngine.ConnectorCallback {
                    override fun connectorStarted() {
                        log.info { "DebeziumEngine notify: connector started" }
                    }

                    override fun connectorStopped() {
                        log.info { "DebeziumEngine notify: connector stopped" }
                    }

                    override fun taskStarted() {
                        log.info { "DebeziumEngine notify: task started" }
                    }

                    override fun taskStopped() {
                        log.info { "DebeziumEngine notify: task stopped" }
                    }
                },
            )
            .build()
    }

    fun reachedTargetPosition(record: DebeziumRecord): Boolean {
        // TODO : Implement this
        log.info { record }
        return false
    }
    enum class DebeziumCloseReason() {
        TIMEOUT,
        ITERATOR_CLOSE,
        HEARTBEAT_REACHED_TARGET_POSITION,
        CHANGE_EVENT_REACHED_TARGET_POSITION,
        HEARTBEAT_NOT_PROGRESSING
    }

    private fun requestClose(closeLogMessage: String, closeReason: DebeziumCloseReason) {
        log.info { closeLogMessage }
        log.info { closeReason }
        // TODO : send close analytics message
        // TODO : Close the engine. Note that engine must be closed in a different thread
        // than the running engine.
        // launch { engine?.close() }
    }
}
