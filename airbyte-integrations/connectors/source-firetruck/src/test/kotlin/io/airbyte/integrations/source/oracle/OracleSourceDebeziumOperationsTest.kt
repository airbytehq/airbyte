/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle

import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.read.cdc.DebeziumInput
import io.airbyte.cdk.read.cdc.DebeziumSchemaHistory
import io.airbyte.cdk.read.cdc.DebeziumState
import io.airbyte.cdk.util.Jsons
import io.airbyte.cdk.util.ResourceUtils
import io.debezium.relational.history.HistoryRecord
import io.micronaut.context.annotation.Property
import io.micronaut.context.env.Environment
import io.micronaut.test.annotation.MockBean
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import java.net.InetSocketAddress
import java.util.function.Supplier
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(environments = [Environment.TEST], rebuildContext = true)
@Property(name = "airbyte.connector.config.host", value = "localhost")
@Property(name = "airbyte.connector.config.port", value = "12345")
@Property(name = "airbyte.connector.config.username", value = "FOO")
@Property(name = "airbyte.connector.config.password", value = "BAR")
@Property(
    name = "airbyte.connector.config.connection_data.connection_type",
    value = "service_name",
)
@Property(name = "airbyte.connector.config.connection_data.service_name", value = "FREEPDB1")
@Property(name = "airbyte.connector.config.cursor.cursor_method", value = "cdc")
class OracleSourceDebeziumOperationsTest {

    @Inject lateinit var ops: OracleSourceDebeziumOperations

    @MockBean(OracleSourceDebeziumOperations.OracleDatabaseStateSupplier::class)
    fun mockOracleDatabaseStateSupplier():
        Supplier<OracleSourceDebeziumOperations.CurrentDatabaseState> {
        return Supplier<OracleSourceDebeziumOperations.CurrentDatabaseState> {
            OracleSourceDebeziumOperations.CurrentDatabaseState(
                address = InetSocketAddress.createUnresolved("localhost", 12345),
                pluggableDatabaseName = "FREEPDB1",
                databaseName = "FREE",
                position = OracleSourcePosition(54321L),
            )
        }
    }

    @Test
    fun testSynthesize() {
        val input: DebeziumInput = ops.synthesize()
        Assertions.assertTrue(input.isSynthetic)
    }

    @Test
    fun testDeserializeUncompressed() {
        val opaqueState: OpaqueStateValue =
            Jsons.readTree(ResourceUtils.readResource("test-state-uncompressed.json"))
        val deserializedInput: DebeziumInput = ops.deserialize(opaqueState, streams = emptyList())
        Assertions.assertFalse(deserializedInput.isSynthetic)
        Assertions.assertEquals(
            OracleSourcePosition(479703),
            ops.position(deserializedInput.state.offset)
        )
    }

    @Test
    fun testDeserializeCompressed() {
        val opaqueState: OpaqueStateValue =
            Jsons.readTree(ResourceUtils.readResource("test-state-compressed.json"))
        val deserializedInput: DebeziumInput = ops.deserialize(opaqueState, streams = emptyList())
        Assertions.assertFalse(deserializedInput.isSynthetic)
        Assertions.assertEquals(
            OracleSourcePosition(479703),
            ops.position(deserializedInput.state.offset)
        )
    }

    @Test
    fun testSerializeUncompressed() {
        val opaqueState: OpaqueStateValue =
            Jsons.readTree(ResourceUtils.readResource("test-state-uncompressed.json"))
        val deserializedInput: DebeziumInput = ops.deserialize(opaqueState, streams = emptyList())
        val roundTrippedOpaqueState: OpaqueStateValue = ops.serialize(deserializedInput.state)

        Assertions.assertEquals(opaqueState, roundTrippedOpaqueState)
    }

    @Test
    fun testSerializeCompressed() {
        val state: DebeziumState = generateVeryLargeState()
        val opaqueState: OpaqueStateValue = ops.serialize(state)
        Assertions.assertFalse(opaqueState["schema_history"].isArray)
        val deserializedInput: DebeziumInput = ops.deserialize(opaqueState, streams = emptyList())
        val roundTrippedOpaqueState: OpaqueStateValue = ops.serialize(deserializedInput.state)
        Assertions.assertEquals(opaqueState, roundTrippedOpaqueState)
    }

    private fun generateVeryLargeState(): DebeziumState {
        val opaqueState: OpaqueStateValue =
            Jsons.readTree(ResourceUtils.readResource("test-state-uncompressed.json"))
        val state: DebeziumState = ops.deserialize(opaqueState, streams = emptyList()).state
        val bigHistory: List<HistoryRecord> = (1..20).flatMap { state.schemaHistory!!.wrapped }
        return state.copy(schemaHistory = DebeziumSchemaHistory(bigHistory))
    }
}
