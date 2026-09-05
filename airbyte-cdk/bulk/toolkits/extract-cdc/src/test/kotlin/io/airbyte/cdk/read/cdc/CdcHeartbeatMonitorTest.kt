/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import java.time.Duration
import java.time.LocalDateTime
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test

private data class MonitorPosition(val value: Long) : PartiallyOrdered<MonitorPosition> {
    override fun compareTo(other: MonitorPosition): Int = value.compareTo(other.value)
}

class CdcHeartbeatMonitorTest {
    private var now = LocalDateTime.of(2026, 1, 1, 0, 0)

    private fun monitor(timeout: Duration? = Duration.ofMinutes(5)) =
        CdcHeartbeatMonitor<MonitorPosition>(timeout) { now }

    @Test
    fun progressingHeartbeatsWithoutRecordsCloseAfterTimeout() {
        val monitor = monitor()

        assertNull(monitor.onHeartbeat(MonitorPosition(1)))
        now = now.plusMinutes(6)

        assertEquals(
            CdcPartitionReader.CloseReason.HEARTBEAT_PROGRESSING_WITHOUT_RECORDS,
            monitor.onHeartbeat(MonitorPosition(2)),
        )
    }

    @Test
    fun firstHeartbeatAloneNeverCloses() {
        val monitor = monitor()
        now = now.plusMinutes(6)

        assertNull(monitor.onHeartbeat(MonitorPosition(1)))
    }

    @Test
    fun slowStartupBeforeFirstHeartbeatDoesNotCauseImmediateClose() {
        val monitor = monitor(Duration.ofSeconds(60))
        now = now.plusMinutes(10)

        assertNull(monitor.onHeartbeat(MonitorPosition(1)))
        now = now.plusSeconds(5)
        assertNull(monitor.onHeartbeat(MonitorPosition(2)))
        now = now.plusSeconds(61)

        assertEquals(
            CdcPartitionReader.CloseReason.HEARTBEAT_PROGRESSING_WITHOUT_RECORDS,
            monitor.onHeartbeat(MonitorPosition(3)),
        )
    }

    @Test
    fun recordsResetTheNoRecordTimer() {
        val monitor = monitor()

        assertNull(monitor.onHeartbeat(MonitorPosition(1)))
        now = now.plusMinutes(4)
        monitor.onRecord()
        now = now.plusMinutes(4)
        assertNull(monitor.onHeartbeat(MonitorPosition(2)))
        now = now.plusMinutes(6)

        assertEquals(
            CdcPartitionReader.CloseReason.HEARTBEAT_PROGRESSING_WITHOUT_RECORDS,
            monitor.onHeartbeat(MonitorPosition(3)),
        )
    }

    @Test
    fun stalledHeartbeatStillClosesWithNotProgressing() {
        val monitor = monitor()

        assertNull(monitor.onHeartbeat(MonitorPosition(1)))
        now = now.plusMinutes(2)
        assertNull(monitor.onHeartbeat(MonitorPosition(1)))
        now = now.plusMinutes(4)

        assertEquals(
            CdcPartitionReader.CloseReason.HEARTBEAT_NOT_PROGRESSING,
            monitor.onHeartbeat(MonitorPosition(1)),
        )
    }

    @Test
    fun noTimeoutNeverCloses() {
        val monitor = monitor(null)

        assertNull(monitor.onHeartbeat(MonitorPosition(1)))
        now = now.plusHours(1)
        assertNull(monitor.onHeartbeat(MonitorPosition(2)))
    }
}
