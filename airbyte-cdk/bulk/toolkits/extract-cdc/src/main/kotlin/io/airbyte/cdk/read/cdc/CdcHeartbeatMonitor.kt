/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Duration
import java.time.LocalDateTime

internal class CdcHeartbeatMonitor<T : PartiallyOrdered<T>>(
    private val timeout: Duration?,
    private val clock: () -> LocalDateTime = LocalDateTime::now,
) {
    private val log = KotlinLogging.logger {}
    private var lastHeartbeatPosition: T? = null
    private var lastHeartbeatTime: LocalDateTime? = null
    private var lastRecordTime: LocalDateTime = clock()

    fun onRecord() {
        lastRecordTime = clock()
    }

    fun onHeartbeat(currentPosition: T): CdcPartitionReader.CloseReason? {
        if (timeout == null) return null
        val now = clock()
        val isProgressing =
            lastHeartbeatPosition == null || currentPosition.isGreater(lastHeartbeatPosition)
        if (isProgressing) {
            val previousPosition = lastHeartbeatPosition
            if (previousPosition == null) {
                lastRecordTime = now
            }
            lastHeartbeatPosition = currentPosition
            lastHeartbeatTime = now
            log.info { "Heartbeat progressing to position: $currentPosition" }
            val timeSinceLastRecord = Duration.between(lastRecordTime, now)
            if (previousPosition != null && timeSinceLastRecord > timeout) {
                log.info {
                    "No records received for ${timeSinceLastRecord.toSeconds()}s while heartbeat position advanced from $previousPosition to $currentPosition; closing engine to checkpoint progress."
                }
                return CdcPartitionReader.CloseReason.HEARTBEAT_PROGRESSING_WITHOUT_RECORDS
            }
        } else {
            val timeSinceLastProgress = Duration.between(lastHeartbeatTime!!, now)
            if (timeSinceLastProgress > timeout) {
                log.info {
                    "Heartbeat timeout: no progress for ${timeSinceLastProgress.toMinutes()} minutes. " +
                        "Last position: $lastHeartbeatPosition, current: $currentPosition"
                }
                return CdcPartitionReader.CloseReason.HEARTBEAT_NOT_PROGRESSING
            }
            log.info {
                "Heartbeat not progressing, time since last progress: ${timeSinceLastProgress.toSeconds()}s"
            }
        }
        return null
    }
}
