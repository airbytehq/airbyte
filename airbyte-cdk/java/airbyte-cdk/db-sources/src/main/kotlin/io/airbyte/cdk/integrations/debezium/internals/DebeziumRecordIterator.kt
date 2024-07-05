/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import com.google.common.annotations.VisibleForTesting
import com.google.common.collect.AbstractIterator
import io.airbyte.cdk.integrations.debezium.CdcTargetPosition
import io.airbyte.commons.lang.MoreBooleans
import io.airbyte.commons.util.AutoCloseableIterator
import io.debezium.engine.ChangeEvent
import io.github.oshai.kotlinlogging.KotlinLogging
import java.lang.reflect.Field
import java.time.Duration
import java.time.LocalDateTime
import java.util.*
import java.util.concurrent.*
import java.util.function.Supplier
import org.apache.kafka.connect.source.SourceRecord

private val LOGGER = KotlinLogging.logger {}
/**
 * The record iterator is the consumer (in the producer / consumer relationship with debezium)
 * responsible for 1. making sure every record produced by the record publisher is processed 2.
 * signalling to the record publisher when it is time for it to stop producing records. It emits
 * this signal either when the publisher had not produced a new record for a long time or when it
 * has processed at least all of the records that were present in the database when the source was
 * started. Because the publisher might publish more records between the consumer sending this
 * signal and the publisher actually shutting down, the consumer must stay alive as long as the
 * publisher is not closed. Even after the publisher is closed, the consumer will finish processing
 * any produced records before closing.
 */
class DebeziumRecordIterator<T>(
    private val queue: LinkedBlockingQueue<ChangeEvent<String?, String?>>,
    private val targetPosition: CdcTargetPosition<T>,
    private val publisherStatusSupplier: Supplier<Boolean>,
    private val debeziumShutdownProcedure: DebeziumShutdownProcedure<ChangeEvent<String?, String?>>,
    private val firstRecordWaitTime: Duration,
) : AbstractIterator<ChangeEventWithMetadata>(), AutoCloseableIterator<ChangeEventWithMetadata> {
    private val heartbeatEventSourceField: MutableMap<Class<out ChangeEvent<*, *>?>, Field?> =
        HashMap(1)
    private val subsequentRecordWaitTime: Duration = firstRecordWaitTime.dividedBy(2)

    private var receivedFirstRecord = false
    private var hasSnapshotFinished = true
    private var tsLastHeartbeat: LocalDateTime? = null
    private var lastHeartbeatPosition: T? = null
    private var maxInstanceOfNoRecordsFound = 0
    private var signalledDebeziumEngineShutdown = false

    // The following logic incorporates heartbeat (CDC postgres only for now):
    // 1. Wait on queue either the configured time first or 1 min after a record received
    // 2. If nothing came out of queue finish sync
    // 3. If received heartbeat: check if hearbeat_lsn reached target or hasn't changed in a while
    // finish sync
    // 4. If change event lsn reached target finish sync
    // 5. Otherwise check message queuen again
    override fun computeNext(): ChangeEventWithMetadata? {
        // keep trying until the publisher is closed or until the queue is empty. the latter case is
        // possible when the publisher has shutdown but the consumer has not yet processed all
        // messages it
        // emitted.
        while (!MoreBooleans.isTruthy(publisherStatusSupplier.get()) || !queue.isEmpty()) {
            val next: ChangeEvent<String?, String?>?

            val waitTime =
                if (receivedFirstRecord) this.subsequentRecordWaitTime else this.firstRecordWaitTime
            try {
                next = queue.poll(waitTime.seconds, TimeUnit.SECONDS)
            } catch (e: InterruptedException) {
                throw RuntimeException(e)
            }

            // if within the timeout, the consumer could not get a record, it is time to tell the
            // producer to
            // shutdown.
            if (next == null) {
                if (
                    !receivedFirstRecord || hasSnapshotFinished || maxInstanceOfNoRecordsFound >= 10
                ) {
                    requestClose(
                        String.format(
                            "No records were returned by Debezium in the timeout seconds %s, closing the engine and iterator",
                            waitTime.seconds
                        )
                    )
                }
                LOGGER.info { "no record found. polling again." }
                maxInstanceOfNoRecordsFound++
                continue
            }

            if (isHeartbeatEvent(next)) {
                if (!hasSnapshotFinished) {
                    continue
                }

                val heartbeatPos = getHeartbeatPosition(next)
                // wrap up sync if heartbeat position crossed the target OR heartbeat position
                // hasn't changed for
                // too long
                if (targetPosition.reachedTargetPosition(heartbeatPos)) {
                    requestClose(
                        "Closing: Heartbeat indicates sync is done by reaching the target position"
                    )
                } else if (
                    heartbeatPos == this.lastHeartbeatPosition && heartbeatPosNotChanging()
                ) {
                    requestClose("Closing: Heartbeat indicates sync is not progressing")
                }

                if (heartbeatPos != lastHeartbeatPosition) {
                    this.tsLastHeartbeat = LocalDateTime.now()
                    this.lastHeartbeatPosition = heartbeatPos
                }
                continue
            }

            val changeEventWithMetadata = ChangeEventWithMetadata(next)
            hasSnapshotFinished = !changeEventWithMetadata.isSnapshotEvent

            // if the last record matches the target file position, it is time to tell the producer
            // to shutdown.
            if (targetPosition.reachedTargetPosition(changeEventWithMetadata)) {
                requestClose("Closing: Change event reached target position")
            }
            this.tsLastHeartbeat = null
            this.receivedFirstRecord = true
            this.maxInstanceOfNoRecordsFound = 0
            return changeEventWithMetadata
        }

        if (!signalledDebeziumEngineShutdown) {
            LOGGER.warn { "Debezium engine has not been signalled to shutdown, this is unexpected" }
        }

        // Read the records that Debezium might have fetched right at the time we called shutdown
        while (!debeziumShutdownProcedure.recordsRemainingAfterShutdown.isEmpty()) {
            val event: ChangeEvent<String?, String?>?
            try {
                event =
                    debeziumShutdownProcedure.recordsRemainingAfterShutdown.poll(
                        100,
                        TimeUnit.MILLISECONDS
                    )
            } catch (e: InterruptedException) {
                throw RuntimeException(e)
            }
            if (event == null || isHeartbeatEvent(event)) {
                continue
            }
            val changeEventWithMetadata = ChangeEventWithMetadata(event)
            hasSnapshotFinished = !changeEventWithMetadata.isSnapshotEvent
            return changeEventWithMetadata
        }
        throwExceptionIfSnapshotNotFinished()
        return endOfData()
    }

    /**
     * Debezium was built as an ever running process which keeps on listening for new changes on DB
     * and immediately processing them. Airbyte needs debezium to work as a start stop mechanism. In
     * order to determine when to stop debezium engine we rely on few factors 1. TargetPosition
     * logic. At the beginning of the sync we define a target position in the logs of the DB. This
     * can be an LSN or anything specific to the DB which can help us identify that we have reached
     * a specific position in the log based replication When we start processing records from
     * debezium, we extract the the log position from the metadata of the record and compare it with
     * our target that we defined at the beginning of the sync. If we have reached the target
     * position, we shutdown the debezium engine 2. The TargetPosition logic might not always work
     * and in order to tackle that we have another logic where if we do not receive records from
     * debezium for a given duration, we ask debezium engine to shutdown 3. We also take the
     * Snapshot into consideration, when a connector is running for the first time, we let it
     * complete the snapshot and only after the completion of snapshot we should shutdown the
     * engine. If we are closing the engine before completion of snapshot, we throw an exception
     */
    @Throws(Exception::class)
    override fun close() {
        requestClose("Closing: Iterator closing")
    }

    private fun isHeartbeatEvent(event: ChangeEvent<String?, String?>): Boolean {
        return targetPosition.isHeartbeatSupported &&
            Objects.nonNull(event) &&
            !event.value()!!.contains("source")
    }

    private fun heartbeatPosNotChanging(): Boolean {
        if (this.tsLastHeartbeat == null) {
            return false
        }
        val timeElapsedSinceLastHeartbeatTs =
            Duration.between(this.tsLastHeartbeat, LocalDateTime.now())
        LOGGER.info {
            "Time since last hb_pos change ${timeElapsedSinceLastHeartbeatTs.toSeconds()}s"
        }
        // wait time for no change in heartbeat position is half of initial waitTime
        return timeElapsedSinceLastHeartbeatTs.compareTo(firstRecordWaitTime.dividedBy(2)) > 0
    }

    private fun requestClose(closeLogMessage: String) {
        if (signalledDebeziumEngineShutdown) {
            return
        }
        LOGGER.info { closeLogMessage }
        debeziumShutdownProcedure.initiateShutdownProcedure()
        signalledDebeziumEngineShutdown = true
    }

    private fun throwExceptionIfSnapshotNotFinished() {
        if (!hasSnapshotFinished) {
            throw RuntimeException("Closing down debezium engine but snapshot has not finished")
        }
    }

    /**
     * [DebeziumRecordIterator.heartbeatEventSourceField] acts as a cache so that we avoid using
     * reflection to setAccessible for each event
     */
    @VisibleForTesting
    internal fun getHeartbeatPosition(heartbeatEvent: ChangeEvent<String?, String?>): T {
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
                    LOGGER.warn {
                        "Field Cache size growing beyond expected size of 1, size is ${heartbeatEventSourceField.size}"
                    }
                }
            }

            val sr = f!![heartbeatEvent] as SourceRecord
            return targetPosition.extractPositionFromHeartbeatOffset(sr.sourceOffset())
        } catch (e: NoSuchFieldException) {
            LOGGER.info { "failed to get heartbeat source offset" }
            throw RuntimeException(e)
        } catch (e: IllegalAccessException) {
            LOGGER.info { "failed to get heartbeat source offset" }
            throw RuntimeException(e)
        }
    }

    companion object {}
}
