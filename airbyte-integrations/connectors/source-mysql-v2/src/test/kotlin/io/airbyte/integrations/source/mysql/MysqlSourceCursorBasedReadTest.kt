package io.airbyte.integrations.source.mysql

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.ClockFactory
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.data.AirbyteType
import io.airbyte.cdk.data.LeafAirbyteType
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.mysql.MysqlSourceCursorBasedReadTest.LazyValues.allStateMessages
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.DynamicContainer
import org.junit.jupiter.api.DynamicNode
import org.junit.jupiter.api.DynamicTest
import org.junit.jupiter.api.TestFactory
import org.junit.jupiter.api.Timeout
import org.testcontainers.containers.MySQLContainer
import java.sql.Connection

private val log = KotlinLogging.logger {}

class MysqlSourceCursorBasedReadTest {
    @TestFactory
    @Timeout(300)
    fun syncTests(): Iterable<DynamicNode> {
        val read: DynamicNode =
            DynamicTest.dynamicTest("read") {
                Assertions.assertFalse(LazyValues.actualReads.isEmpty())
            }
        val cases: List<DynamicNode> =
            testCases.map { testCase: TestCase ->
                DynamicContainer.dynamicContainer(
                    testCase.insertValues.toString(),
                    listOf(
                        DynamicTest.dynamicTest("records") { records(testCase) },
                    ),
                )
            }
        return listOf(read) + cases
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

    private fun records(testCase: TestCase) {
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

        val testCases: List<TestCase> =
            listOf(
                TestCase(insertValues = mapOf("stream1" to listOf("test1", "test2"), "stream2" to listOf("test3")),
                         expectedValues =  mapOf("stream1" to listOf("test1", "test2"), "stream2" to listOf("test3")),
                         followUpDDL=listOf("INSERT INTO stream1 (col) VALUES ('test3')")),
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
                            log.info { "test case: executing $sql" }
                            connection.createStatement().use { stmt -> stmt.execute(sql) }
                        }
                    }
                }
        }
    }

    data class TestCase(
        val insertValues: Map<String, List<String>>,
        val expectedValues: Map<String, List<String>>,
        val airbyteType: AirbyteType = LeafAirbyteType.STRING,
        val cursor: Boolean = true,
        val noPK: Boolean = false,
        val followUpDDL: List<String>? = null,
    ) {
        val sqlStatements: List<String>
            get() {

                var ddl: MutableList<String> = mutableListOf("CREATE DATABASE IF NOT EXISTS test",
                    "USE test")
                var dml: MutableList<String> = mutableListOf()
                val columnName = "col"

                insertValues.keys.forEach {
                        ddl.add(
                            "CREATE TABLE IF NOT EXISTS $it " +
                                "(col VARCHAR(20) ${if (noPK) "" else "PRIMARY KEY"})"
                        )
                        ddl.add("TRUNCATE TABLE $it")

                }

                insertValues.forEach {
                    (k: String, v: List<String>) ->
                    run {
                        val tableName = k;
                        v.forEach {
                            dml.add( """INSERT INTO $tableName ($columnName) VALUES ("$it")""" )
                        }
                    }
                }

                return ddl + dml
            }

        val streamNamesToRecordData: Map<String, List<JsonNode>>
            get() {
                val columnName = "col"
                var expectedJsonNodesToStream : MutableMap<String, List<JsonNode>> = mutableMapOf()

                expectedValues.forEach {
                    (k, v) ->
                    run {
                        val tableName = k;

                        val recordData: List<JsonNode> =
                            v.map { Jsons.readTree("""{"${columnName}":"$it"}""") }

                        expectedJsonNodesToStream.put(tableName, recordData)
                    }
                }
                return expectedJsonNodesToStream.toMap()
            }
    }
}
