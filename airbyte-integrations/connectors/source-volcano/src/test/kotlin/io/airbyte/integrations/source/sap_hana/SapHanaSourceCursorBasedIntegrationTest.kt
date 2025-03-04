/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.sap_hana

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.airbyte.protocol.models.v0.SyncMode
import java.sql.SQLException
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class SapHanaSourceCursorBasedIntegrationTest {
    @BeforeEach
    fun setUp() {
        try {
            db.connect()
            for (i in 0..schemaNames.size - 1) {
                db.execute("CREATE SCHEMA ${schemaNames[i]}")
                for (j in 0..tableNames.size - 1) {
                    db.execute(
                        "CREATE TABLE ${schemaNames[i]}.${tableNames[j]} (ID INT PRIMARY KEY, NAME VARCHAR(255))"
                    )
                    db.execute(
                        "INSERT INTO ${schemaNames[0]}.${tableNames[0]} (ID, NAME) VALUES (10, 'foo')"
                    )
                    db.execute(
                        "INSERT INTO ${schemaNames[0]}.${tableNames[0]} (ID, NAME) VALUES (20, 'bar')"
                    )
                }
            }
        } catch (e: SQLException) {
            e.printStackTrace()
        }
    }

    @AfterEach
    fun tearDown() {
        try {
            for (i in 0..schemaNames.size - 1) db.execute("DROP SCHEMA ${schemaNames[i]} CASCADE")
            db.disconnect()
        } catch (e: SQLException) {
            e.printStackTrace()
        }
    }

    @Test
    fun testCursorBasedRead() {
        val run1: BufferingOutputConsumer =
            CliRunner.source("read", config, getConfiguredCatalog()).run()
        val lastStateMessageFromRun1 = run1.states().last()
        val lastStreamStateFromRun1 = lastStateMessageFromRun1.stream.streamState
        assertEquals("20", lastStreamStateFromRun1.get("cursors").get("ID").toString())
        assertEquals(tableNames[0], lastStateMessageFromRun1.stream.streamDescriptor.name)
        assertEquals(schemaNames[0], lastStateMessageFromRun1.stream.streamDescriptor.namespace)
        assertEquals(2, lastStateMessageFromRun1.sourceStats.recordCount.toInt())
        db.execute(
            "INSERT INTO ${schemaNames[0]}.${tableNames[0]} (ID, NAME) VALUES (3, 'baz-ignore')"
        )
        db.execute(
            "INSERT INTO ${schemaNames[0]}.${tableNames[0]} (ID, NAME) VALUES (13, 'baz-ignore')"
        )
        db.execute("INSERT INTO ${schemaNames[0]}.${tableNames[0]} (ID, NAME) VALUES (30, 'baz')")

        val run2InputState: List<AirbyteStateMessage> = listOf(lastStateMessageFromRun1)
        val run2: BufferingOutputConsumer =
            CliRunner.source("read", config, getConfiguredCatalog(), run2InputState).run()
        val recordMessageFromRun2: List<AirbyteRecordMessage> = run2.records()
        assertEquals(2, recordMessageFromRun2.size)
    }

    companion object {
        var db =
            SapHanaTestDatabase(
                "1bd5e6cf-2112-4b8d-b9d2-3ea58d8a6a8e.hna0.prod-us10.hanacloud.ondemand.com",
                443,
                "DBADMIN",
                "Dbsource12345!"
            )

        val schemaNames = db.getRandomSchemaNames(1)
        val tableNames = db.getRandomTableNames(1)

        val config: SapHanaSourceConfigurationSpecification =
            SapHanaSourceConfigurationSpecification().apply {
                host = db.host
                port = db.port
                schemas = schemaNames
                username = db.username
                password = db.password
                setCursorMethodValue(UserDefinedCursorConfigurationSpecification)
            }

        fun getConfiguredCatalog(): ConfiguredAirbyteCatalog {
            val desc = StreamDescriptor().withName(tableNames[0]).withNamespace(schemaNames[0])
            val discoveredStream =
                DiscoveredStream(
                    id = StreamIdentifier.from(desc),
                    columns = listOf(Field("ID", IntFieldType), Field("NAME", StringFieldType)),
                    primaryKeyColumnIDs = listOf(listOf("ID"))
                )
            val stream: AirbyteStream =
                SapHanaSourceOperations()
                    .create(SapHanaSourceConfigurationFactory().make(config), discoveredStream)
            val configuredStream: ConfiguredAirbyteStream =
                CatalogHelpers.toDefaultConfiguredStream(stream)
                    .withSyncMode(SyncMode.INCREMENTAL)
                    .withPrimaryKey(discoveredStream.primaryKeyColumnIDs)
                    .withCursorField(listOf("ID"))
            return ConfiguredAirbyteCatalog().withStreams(listOf(configuredStream))
        }
    }
}
