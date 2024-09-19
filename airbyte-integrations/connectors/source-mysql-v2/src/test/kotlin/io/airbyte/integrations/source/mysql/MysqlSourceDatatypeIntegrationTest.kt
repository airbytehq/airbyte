/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.ClockFactory
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.data.AirbyteType
import io.airbyte.cdk.data.LeafAirbyteType
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Connection
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.DynamicContainer
import org.junit.jupiter.api.DynamicNode
import org.junit.jupiter.api.DynamicTest
import org.junit.jupiter.api.TestFactory
import org.junit.jupiter.api.Timeout
import org.testcontainers.containers.MySQLContainer

private val log = KotlinLogging.logger {}

class MysqlSourceDatatypeIntegrationTest {
    @TestFactory
    @Timeout(300)
    fun syncTests(): Iterable<DynamicNode> {
        val discover: DynamicNode =
            DynamicTest.dynamicTest("discover") {
                Assertions.assertFalse(LazyValues.actualStreams.isEmpty())
            }
        val read: DynamicNode =
            DynamicTest.dynamicTest("read") {
                Assertions.assertFalse(LazyValues.actualReads.isEmpty())
            }
        val cases: List<DynamicNode> =
            allStreamNamesAndRecordData.keys.map { streamName: String ->
                DynamicContainer.dynamicContainer(
                    streamName,
                    listOf(
                        DynamicTest.dynamicTest("discover") { discover(streamName) },
                        DynamicTest.dynamicTest("records") { records(streamName) },
                    ),
                )
            }
        return listOf(discover, read) + cases
    }

    object LazyValues {
        val actualStreams: Map<String, AirbyteStream> by lazy {
            val output: BufferingOutputConsumer = CliRunner.source("discover", config()).run()
            output.catalogs().firstOrNull()?.streams?.filterNotNull()?.associateBy { it.name }
                ?: mapOf()
        }

        val configuredCatalog: ConfiguredAirbyteCatalog by lazy {
            val configuredStreams: List<ConfiguredAirbyteStream> =
                allStreamNamesAndRecordData.keys
                    .mapNotNull { actualStreams[it] }
                    .map(CatalogHelpers::toDefaultConfiguredStream)
            for (configuredStream in configuredStreams) {
                if (configuredStream.stream.supportedSyncModes.contains(SyncMode.INCREMENTAL)) {
                    configuredStream.syncMode = SyncMode.INCREMENTAL
                }
            }
            ConfiguredAirbyteCatalog().withStreams(configuredStreams)
        }

        val allReadMessages: List<AirbyteMessage> by lazy {
            CliRunner.source("read", config(), configuredCatalog).run().messages()
        }

        val actualReads: Map<String, BufferingOutputConsumer> by lazy {
            val result: Map<String, BufferingOutputConsumer> =
                allStreamNamesAndRecordData.keys.associateWith {
                    BufferingOutputConsumer(ClockFactory().fixed())
                }
            for (msg in allReadMessages) {
                result[streamName(msg) ?: continue]?.accept(msg)
            }
            result
        }

        fun streamName(msg: AirbyteMessage): String? =
            when (msg.type) {
                AirbyteMessage.Type.RECORD -> msg.record?.stream
                AirbyteMessage.Type.STATE -> msg.state?.stream?.streamDescriptor?.name
                AirbyteMessage.Type.TRACE ->
                    when (msg.trace?.type) {
                        AirbyteTraceMessage.Type.ERROR -> msg.trace?.error?.streamDescriptor?.name
                        AirbyteTraceMessage.Type.ESTIMATE -> msg.trace?.estimate?.name
                        AirbyteTraceMessage.Type.STREAM_STATUS ->
                            msg.trace?.streamStatus?.streamDescriptor?.name
                        AirbyteTraceMessage.Type.ANALYTICS -> null
                        null -> null
                    }
                else -> null
            }
    }

    private fun discover(streamName: String) {
        val actualStream: AirbyteStream? = LazyValues.actualStreams[streamName]
        log.info { "discover result: ${LazyValues.actualStreams}" }
        log.info { "streamName: $streamName" }
        Assertions.assertNotNull(actualStream)
        log.info {
            "test case $streamName: discovered stream ${
                Jsons.valueToTree<JsonNode>(
                    actualStream,
                )
            }"
        }
        val testCase: TestCase =
            testCases.find { it.streamNamesToRecordData.keys.contains(streamName) }!!
        val isIncrementalSupported: Boolean =
            actualStream!!.supportedSyncModes.contains(SyncMode.INCREMENTAL)
        val jsonSchema: JsonNode = actualStream.jsonSchema?.get("properties")!!
        if (streamName == testCase.tableName) {
            val actualSchema: JsonNode = jsonSchema[testCase.columnName]
            Assertions.assertNotNull(actualSchema)
            val expectedSchema: JsonNode = testCase.airbyteType.asJsonSchema()
            Assertions.assertEquals(expectedSchema, actualSchema)
            if (testCase.cursor) {
                Assertions.assertTrue(isIncrementalSupported)
            } else {
                Assertions.assertFalse(isIncrementalSupported)
            }
        }
    }

    private fun records(streamName: String) {
        val actualRead: BufferingOutputConsumer? = LazyValues.actualReads[streamName]
        Assertions.assertNotNull(actualRead)

        fun sortedRecordData(data: List<JsonNode>): JsonNode =
            Jsons.createArrayNode().apply { addAll(data.sortedBy { it.toString() }) }

        val actualRecords: List<AirbyteRecordMessage> = actualRead?.records() ?: listOf()
        val actual: JsonNode = sortedRecordData(actualRecords.mapNotNull { it.data })
        log.info { "test case $streamName: emitted records $actual" }
        val expected: JsonNode = sortedRecordData(allStreamNamesAndRecordData[streamName]!!)

        Assertions.assertEquals(expected, actual)
    }

    companion object {
        lateinit var dbContainer: MySQLContainer<*>

        fun config(): MysqlSourceConfigurationJsonObject = MysqlContainerFactory.config(dbContainer)

        val connectionFactory: JdbcConnectionFactory by lazy {
            JdbcConnectionFactory(MysqlSourceConfigurationFactory().make(config()))
        }

        val stringValues =
            mapOf(
                "'abcdef'" to """"abcdef"""",
                "'ABCD'" to """"ABCD"""",
                "'OXBEEF'" to """"OXBEEF"""",
            )

        val testCases: List<TestCase> =
            listOf(
                TestCase("VARCHAR(10)", stringValues),
            )

        val allStreamNamesAndRecordData: Map<String, List<JsonNode>> =
            testCases.flatMap { it.streamNamesToRecordData.toList() }.toMap()

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun startAndProvisionTestContainer() {
            dbContainer =
                MysqlContainerFactory.exclusive(
                    "mysql:8.0",
                    MysqlContainerFactory.WithNetwork,
                )
            connectionFactory
                .get()
                .also { it.isReadOnly = false }
                .use { connection: Connection ->
                    for (case in testCases) {
                        for (sql in case.sqlStatements) {
                            log.info { "test case ${case.id}: executing $sql" }
                            connection.createStatement().use { stmt -> stmt.execute(sql) }
                        }
                    }
                }
        }
    }

    data class TestCase(
        val sqlType: String,
        val sqlToAirbyte: Map<String, String>,
        val airbyteType: AirbyteType = LeafAirbyteType.STRING,
        val cursor: Boolean = true,
        val noPK: Boolean = false,
        val customDDL: List<String>? = null,
    ) {
        val id: String
            get() =
                sqlType
                    .replace("[^a-zA-Z0-9]".toRegex(), " ")
                    .trim()
                    .replace(" +".toRegex(), "_")
                    .lowercase()

        val tableName: String
            get() = "tbl_$id"

        val columnName: String
            get() = "col_$id"

        val sqlStatements: List<String>
            get() {
                val ddl: List<String> =
                    listOf(
                        "CREATE DATABASE IF NOT EXISTS test",
                        "USE test",
                        "CREATE TABLE IF NOT EXISTS $tableName " +
                            "($columnName $sqlType ${if (noPK) "" else "PRIMARY KEY"})",
                        "TRUNCATE TABLE $tableName",
                    )
                val dml: List<String> =
                    sqlToAirbyte.keys.map { "INSERT INTO $tableName ($columnName) VALUES ($it)" }

                return ddl + dml
            }

        val streamNamesToRecordData: Map<String, List<JsonNode>>
            get() {
                val recordData: List<JsonNode> =
                    sqlToAirbyte.values.map { Jsons.readTree("""{"${columnName}":$it}""") }
                return mapOf(tableName to recordData)
            }
    }
}
