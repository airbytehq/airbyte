/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.cdc

import com.fasterxml.jackson.databind.ObjectMapper
import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.read.CdcContext
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.DebeziumRecord
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.util.Jsons
import io.debezium.engine.ChangeEvent
import io.debezium.engine.DebeziumEngine
import io.debezium.engine.format.Json
import io.debezium.engine.spi.OffsetCommitPolicy
import io.github.oshai.kotlinlogging.KotlinLogging
import java.lang.reflect.Field
import java.util.*
import java.util.concurrent.atomic.AtomicReference
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import org.apache.kafka.connect.source.SourceRecord

class CdcPartitionReader(
    private val concurrencyResource: ConcurrencyResource,
    private val cdcContext: CdcContext,
    opaqueStateValue: OpaqueStateValue?,
) : PartitionReader {

    private val log = KotlinLogging.logger {}
    private lateinit var engine: DebeziumEngine<ChangeEvent<String?, String?>>
    private var numRecords = 0L
    private var initialOpaqueStateValue: OpaqueStateValue = ObjectMapper().createObjectNode()
    private val outputConsumer = cdcContext.outputConsumer
    private val eventConverter = cdcContext.eventConverter
    private val propertyManager = cdcContext.debeziumManager
    private val positionMapper = cdcContext.positionMapperFactory.get()
    private val initialCdcStateCreatorFactory = cdcContext.initialCdcStateCreatorFactory
    private val acquiredThread = AtomicReference<ConcurrencyResource.AcquiredThread>()
    private val opaqueStateValue = opaqueStateValue
    private val heartbeatEventSourceField: MutableMap<Class<out ChangeEvent<*, *>?>, Field?> =
        HashMap(1)

    /** Calling [close] releases the resources acquired for the [JdbcPartitionReader]. */
    fun interface AcquiredResources : AutoCloseable

    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus {
        val acquiredThread: ConcurrencyResource.AcquiredThread =
            concurrencyResource.tryAcquire()
                ?: return PartitionReader.TryAcquireResourcesStatus.RETRY_LATER
        this.acquiredThread.set(acquiredThread)
        return PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN
    }

    override suspend fun run() {
        // A null state value implies that this is the first time debezium is run. If so, we skip
        // running the debezium engine (as there are no new changes) and build the initial offset
        if (opaqueStateValue != null) {
            engine = createDebeziumEngine()
            engine.run()
        } else {
            initialOpaqueStateValue = initialCdcStateCreatorFactory.make()
        }
    }

    override fun checkpoint(): PartitionReadCheckpoint {
        if (opaqueStateValue != null) {
            return PartitionReadCheckpoint(propertyManager.readOffsetState(), numRecords)
        } else {
            return PartitionReadCheckpoint(initialOpaqueStateValue, 0)
        }
    }

    override fun releaseResources() {
        acquiredThread.getAndSet(null)?.close()
        cdcContext.cdcGlobalLockResource.markCdcAsComplete()
    }

    fun createDebeziumEngine(): DebeziumEngine<ChangeEvent<String?, String?>> {
        log.info {
            "Using DBZ version: ${DebeziumEngine::class.java.getPackage().implementationVersion}"
        }
        return DebeziumEngine.create(Json::class.java)
            .using(propertyManager.getPropertiesForSync(opaqueStateValue))
            .using(OffsetCommitPolicy.AlwaysCommitOffsetPolicy())
            .notifying { event: ChangeEvent<String?, String?> ->
                // debezium outputs a tombstone event that has a value of null. this is an
                // artifact of how it
                // interacts with kafka. we want to ignore it.
                // more on the tombstone:
                // https://debezium.io/documentation/reference/2.2/transformations/event-flattening.html
                if (event.value() == null) {
                    return@notifying
                }
                val record = DebeziumRecord(Jsons.deserialize(event.value()))
                // TODO : Migrate over all of the timeout/heartbeat timeout logic
                if (!record.isHeartbeat) {
                    numRecords++
                    outputConsumer.accept(eventConverter.toAirbyteMessage(record))
                    if (positionMapper.reachedTargetPosition(record)) {
                        requestClose(
                            "Closing: Heartbeat indicates sync is not progressing",
                            DebeziumCloseReason.HEARTBEAT_NOT_PROGRESSING
                        )
                    }
                } else {
                    val heartbeatSourceRecord = getSourceRecord(event)
                    if (positionMapper.reachedTargetPosition(heartbeatSourceRecord)) {
                        requestClose(
                            "Closing: Heartbeat indicates sync is done by reaching the target position",
                            DebeziumCloseReason.HEARTBEAT_REACHED_TARGET_POSITION
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

    /**
     * [DebeziumRecordIterator.heartbeatEventSourceField] acts as a cache so that we avoid using
     * reflection to setAccessible for each event
     */
    @VisibleForTesting
    internal fun getSourceRecord(heartbeatEvent: ChangeEvent<String?, String?>): SourceRecord {
        try {
            val eventClass: Class<out ChangeEvent<*, *>?> = heartbeatEvent.javaClass
            val f: Field?
            if (heartbeatEventSourceField.containsKey(eventClass)) {
                f = heartbeatEventSourceField[eventClass]
            } else {
                f = eventClass.getDeclaredField("sourceRecord")
                f.isAccessible = true
                heartbeatEventSourceField[eventClass] = f

                if (heartbeatEventSourceField.size > 1) {
                    log.warn {
                        "Field Cache size growing beyond expected size of 1, size is ${heartbeatEventSourceField.size}"
                    }
                }
            }

            val sr = f!![heartbeatEvent] as SourceRecord
            return sr
        } catch (e: NoSuchFieldException) {
            log.info { "failed to get heartbeat source offset" }
            throw RuntimeException(e)
        } catch (e: IllegalAccessException) {
            log.info { "failed to get heartbeat source offset" }
            throw RuntimeException(e)
        }
    }

    enum class DebeziumCloseReason() {
        TIMEOUT,
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
        CoroutineScope(Dispatchers.IO).launch { engine.close() }
    }
}
