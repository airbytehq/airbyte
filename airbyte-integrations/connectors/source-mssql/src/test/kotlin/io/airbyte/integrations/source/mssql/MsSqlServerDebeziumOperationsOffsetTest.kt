/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.NullNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.fasterxml.jackson.databind.node.TextNode
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.cdc.DebeziumOffset
import io.airbyte.cdk.util.Jsons
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertSame
import org.junit.jupiter.api.Test

class MsSqlServerDebeziumOperationsOffsetTest {

    private val offsetKey =
        Jsons.readTree("""["CdcTest",{"server":"CdcTest","database":"CdcTest"}]""")

    @Test
    fun `serializeState replaces textual NULL change_lsn with commit_lsn`() {
        val operations = operations()

        val serialized =
            serializedOffset(
                operations,
                offset("00033e76:0000cd58:0008", TextNode.valueOf("NULL"), 0)
            )

        assertEquals("00033e76:0000cd58:0008", serialized["change_lsn"].asText())
        assertEquals(0, serialized["event_serial_no"].asInt())
    }

    @Test
    fun `serializeState replaces JSON null change_lsn with commit_lsn`() {
        val operations = operations()

        val serialized =
            serializedOffset(operations, offset("00033e76:0000cd58:0008", NullNode.instance, 0))

        assertEquals("00033e76:0000cd58:0008", serialized["change_lsn"].asText())
    }

    @Test
    fun `serializeState leaves a real change_lsn untouched`() {
        val operations = operations()

        val serialized =
            serializedOffset(
                operations,
                offset("00033e7b:0001f308:0034", TextNode.valueOf("00033e7b:0001f308:0007"), 2)
            )

        assertEquals("00033e7b:0001f308:0007", serialized["change_lsn"].asText())
        assertEquals(2, serialized["event_serial_no"].asInt())
    }

    @Test
    fun `heartbeat regression with unchanged commit_lsn restores starting values`() {
        val operations = operations()
        val startingOffset =
            offset("00033e76:0000cd58:0008", TextNode.valueOf("00033e76:0000cd58:0003"), 2)
        setLastLoadedOffset(operations, startingOffset)

        val serialized =
            serializedOffset(
                operations,
                offset("00033e76:0000cd58:0008", TextNode.valueOf("NULL"), 0)
            )

        assertEquals("00033e76:0000cd58:0003", serialized["change_lsn"].asText())
        assertEquals(2, serialized["event_serial_no"].asInt())
    }

    @Test
    fun `heartbeat that advanced commit_lsn gets change_lsn equal to commit_lsn`() {
        val operations = operations()
        val startingOffset =
            offset("00033e76:0000cd58:0008", TextNode.valueOf("00033e76:0000cd58:0003"), 2)
        setLastLoadedOffset(operations, startingOffset)

        val serialized =
            serializedOffset(
                operations,
                offset("00033e76:0000cd60:0001", TextNode.valueOf("NULL"), 0)
            )

        assertEquals("00033e76:0000cd60:0001", serialized["change_lsn"].asText())
        assertEquals(0, serialized["event_serial_no"].asInt())
    }

    @Test
    fun `normalizeHeartbeatChangeLsn leaves offsets without change_lsn key alone`() {
        val operations = operations()
        val snapshotOffset =
            DebeziumOffset(
                mapOf(
                    offsetKey to
                        snapshotValue("00033e76:0000cd58:0008").apply {
                            put("snapshot", true)
                            put("snapshot_completed", true)
                        }
                )
            )

        assertSame(snapshotOffset, operations.normalizeHeartbeatChangeLsn(snapshotOffset))
    }

    @Test
    fun `normalizeHeartbeatChangeLsn leaves multi-key offsets alone`() {
        val operations = operations()
        val secondKey = Jsons.readTree("""["CdcTest2",{"server":"CdcTest","database":"CdcTest"}]""")
        val firstValue = offsetValue("00033e76:0000cd58:0008", TextNode.valueOf("NULL"), 0)
        val secondValue = offsetValue("00033e76:0000cd60:0001", NullNode.instance, 0)
        val multiKeyOffset =
            DebeziumOffset(mapOf(offsetKey to firstValue, secondKey to secondValue))

        assertSame(multiKeyOffset, operations.normalizeHeartbeatChangeLsn(multiKeyOffset))
    }

    private fun operations(): MsSqlServerDebeziumOperations {
        val spec =
            MsSqlServerSourceConfigurationSpecification().apply {
                host = "localhost"
                port = 1433
                database = "CdcTest"
                username = "sa"
                password = "Password123!"
                setIncrementalValue(Cdc())
            }
        val config = MsSqlServerSourceConfigurationFactory().make(spec)
        return MsSqlServerDebeziumOperations(mockk<JdbcConnectionFactory>(relaxed = true), config)
    }

    private fun offset(
        commitLsn: String,
        changeLsn: JsonNode?,
        eventSerialNo: Int
    ): DebeziumOffset {
        return DebeziumOffset(mapOf(offsetKey to offsetValue(commitLsn, changeLsn, eventSerialNo)))
    }

    private fun offsetValue(
        commitLsn: String,
        changeLsn: JsonNode?,
        eventSerialNo: Int
    ): ObjectNode {
        val value = snapshotValue(commitLsn)
        value.put("event_serial_no", eventSerialNo)
        if (changeLsn != null) {
            value.set<JsonNode>("change_lsn", changeLsn)
        }
        return value
    }

    private fun snapshotValue(commitLsn: String): ObjectNode =
        Jsons.objectNode().apply { put("commit_lsn", commitLsn) }

    private fun serializedOffset(
        operations: MsSqlServerDebeziumOperations,
        offset: DebeziumOffset,
    ): JsonNode {
        val serialized = operations.serializeState(offset, null)
        val state = serialized[MsSqlServerDebeziumOperations.MSSQL_STATE]
        val offsetNode = state[MsSqlServerDebeziumOperations.MSSQL_CDC_OFFSET]
        val encodedValue = offsetNode.elements().next().asText()
        return Jsons.readTree(encodedValue)
    }

    private fun setLastLoadedOffset(
        operations: MsSqlServerDebeziumOperations,
        offset: DebeziumOffset,
    ) {
        MsSqlServerDebeziumOperations::class
            .java
            .getDeclaredField("lastLoadedOffset")
            .apply { isAccessible = true }
            .set(operations, offset)
    }
}
