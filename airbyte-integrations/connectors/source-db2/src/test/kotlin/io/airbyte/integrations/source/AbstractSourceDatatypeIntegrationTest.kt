/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.ClockFactory
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteLogMessage
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Connection
import java.util.function.Supplier
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.DynamicContainer
import org.junit.jupiter.api.DynamicNode
import org.junit.jupiter.api.DynamicTest
import org.junit.jupiter.api.TestFactory
import org.junit.jupiter.api.Timeout
import org.junit.jupiter.api.function.Executable

// Note: This abstract test framework is a WIP and will be moved to the CDK in the future
abstract class AbstractSourceDatatypeIntegrationTest {
    private val log = KotlinLogging.logger {}

    abstract val configSpec: ConfigurationSpecification
    abstract val jdbcConfig: JdbcSourceConfiguration
    abstract val testCases: List<TestCase>

    private val allStreamNamesAndRecordData: Map<String, List<JsonNode>> by lazy {
        testCases.flatMap { it.streamNamesToRecordData.toList() }.toMap()
    }

    private fun findTestCase(streamName: String): TestCase? {
        return testCases.find { streamName.uppercase() in it.streamNamesToRecordData.keys }
    }

    @TestFactory
    @Timeout(300)
    fun syncTests(): Iterable<DynamicNode> {
        val actual =
            DiscoverAndReadAll(configSpec, jdbcConfig, testCases, allStreamNamesAndRecordData)
        val discoverAndReadAllTest: DynamicNode =
            DynamicTest.dynamicTest("discover-and-read-all", actual)
        val testCases: List<DynamicNode> =
            allStreamNamesAndRecordData.keys.map { streamName: String ->
                DynamicContainer.dynamicContainer(streamName, dynamicTests(actual, streamName))
            }
        return listOf(discoverAndReadAllTest) + testCases
    }

    private fun dynamicTests(actual: DiscoverAndReadAll, streamName: String): List<DynamicTest> {
        return listOf(
            DynamicTest.dynamicTest("discover-jdbc") {
                discover(streamName, actual.jdbcStreams[streamName])
            },
            DynamicTest.dynamicTest("records-jdbc") {
                records(streamName, actual.jdbcMessagesByStream[streamName])
            },
        )
    }

    private fun discover(streamName: String, actualStream: AirbyteStream?) {
        Assertions.assertNotNull(actualStream)
        log.info {
            "test case $streamName: discovered stream ${
                Jsons.valueToTree<JsonNode>(
                    actualStream,
                )
            }"
        }
        val testCase: TestCase = findTestCase(streamName)!!
        val jsonSchema: JsonNode = actualStream!!.jsonSchema?.get("properties")!!
        val actualSchema: JsonNode? = jsonSchema[testCase.columnName.uppercase()]
        Assertions.assertNotNull(actualSchema)
        val expectedSchema: JsonNode = testCase.airbyteSchemaType.asJsonSchema()
        Assertions.assertEquals(expectedSchema, actualSchema)
    }

    private fun records(streamName: String, actualRead: BufferingOutputConsumer?) {
        Assertions.assertNotNull(actualRead)
        fun sortedRecordData(data: List<JsonNode>): JsonNode =
            Jsons.createArrayNode().apply { addAll(data.sortedBy { it.toString() }) }

        val actualRecords: List<AirbyteRecordMessage> = actualRead?.records() ?: listOf()
        val actualRecordData: List<JsonNode> =
            actualRecords.mapNotNull {
                val data: ObjectNode = it.data as? ObjectNode ?: return@mapNotNull null
                data.deepCopy().apply {
                    for (fieldName in data.fieldNames()) {
                        if (
                            fieldName.uppercase() == "ID" ||
                                fieldName.startsWith(MetaField.META_PREFIX)
                        ) {
                            remove(fieldName)
                        }
                    }
                }
            }
        val actual = Jsons.writeValueAsString(sortedRecordData(actualRecordData))
        log.info { "test case $streamName: emitted records $actual" }
        val expected =
            Jsons.writeValueAsString(sortedRecordData(allStreamNamesAndRecordData[streamName]!!))

        Assertions.assertEquals(expected, actual)
    }

    class DiscoverAndReadAll(
        private val configSpec: ConfigurationSpecification,
        private val jdbcConfig: JdbcSourceConfiguration,
        private val testCases: List<TestCase>,
        private val allStreamNamesAndRecordData: Map<String, List<JsonNode>>,
    ) : Executable {
        private val log = KotlinLogging.logger {}

        // JDBC DISCOVER and READ intermediate values and final results.
        // Intermediate values are present here as `lateinit var` instead of local variables
        // to make debugging of individual test cases easier.
        lateinit var jdbcConnectionFactory: JdbcConnectionFactory
        lateinit var jdbcStreams: Map<String, AirbyteStream>
        lateinit var jdbcConfiguredCatalog: ConfiguredAirbyteCatalog
        lateinit var jdbcReadOutput: BufferingOutputConsumer
        lateinit var jdbcMessages: List<AirbyteMessage>
        lateinit var jdbcMessagesByStream: Map<String, BufferingOutputConsumer>

        private val connectionFactory: Supplier<Connection> = JdbcConnectionFactory(jdbcConfig)

        override fun execute() {
            jdbcConnectionFactory = JdbcConnectionFactory(jdbcConfig)
            log.info { "Executing DDL statements." }
            connectionFactory.get().use { connection: Connection ->
                for (case in testCases) {
                    for (sql in case.ddl) {
                        log.info { "test case ${case.id}: executing $sql" }
                        connection.createStatement().use { stmt -> stmt.execute(sql) }
                    }
                }
            }
            log.info { "Executing DML statements." }
            jdbcConnectionFactory.get().use { connection: Connection ->
                for (case in testCases) {
                    for (sql in case.dml) {
                        log.info { "test case ${case.id}: executing $sql" }
                        connection.createStatement().use { stmt -> stmt.execute(sql) }
                    }
                }
            }
            log.info { "Running JDBC DISCOVER operation." }
            jdbcStreams = discover(configSpec)
            jdbcConfiguredCatalog = configuredCatalog(jdbcStreams)
            log.info { "Running JDBC READ operation." }
            jdbcReadOutput = CliRunner.source("read", configSpec, jdbcConfiguredCatalog).run()
            Assertions.assertNotEquals(emptyList<AirbyteStateMessage>(), jdbcReadOutput.states())
            Assertions.assertNotEquals(emptyList<AirbyteRecordMessage>(), jdbcReadOutput.records())
            Assertions.assertEquals(emptyList<AirbyteLogMessage>(), jdbcReadOutput.logs())
            jdbcMessages = jdbcReadOutput.messages()
            jdbcMessagesByStream = byStream(jdbcMessages)
            log.info { "Done." }
        }

        private fun discover(configSpec: ConfigurationSpecification): Map<String, AirbyteStream> {
            val output: BufferingOutputConsumer = CliRunner.source("discover", configSpec).run()
            val streams: Map<String, AirbyteStream> =
                output.catalogs().firstOrNull()?.streams?.filterNotNull()?.associateBy { it.name }
                    ?: mapOf()
            Assertions.assertFalse(streams.isEmpty())
            return streams
        }

        private fun configuredCatalog(
            streams: Map<String, AirbyteStream>
        ): ConfiguredAirbyteCatalog {
            val configuredStreams: List<ConfiguredAirbyteStream> =
                allStreamNamesAndRecordData.keys
                    .mapNotNull { streams[it] }
                    .map(CatalogHelpers::toDefaultConfiguredStream)
            for (configuredStream in configuredStreams) {
                if (
                    configuredStream.stream.supportedSyncModes.contains(SyncMode.INCREMENTAL) &&
                        configuredStream.stream.sourceDefinedCursor == true
                ) {
                    configuredStream.syncMode = SyncMode.INCREMENTAL
                    // TODO: add support for sourceDefinedCursor
                    // configuredStream.cursorField = listOf(...)
                } else {
                    configuredStream.syncMode = SyncMode.FULL_REFRESH
                }
            }
            return ConfiguredAirbyteCatalog().withStreams(configuredStreams)
        }

        private fun byStream(messages: List<AirbyteMessage>): Map<String, BufferingOutputConsumer> {
            val result: Map<String, BufferingOutputConsumer> =
                allStreamNamesAndRecordData.keys.associateWith {
                    BufferingOutputConsumer(ClockFactory().fixed())
                }
            for (msg in messages) {
                result[streamName(msg) ?: continue]?.accept(msg)
            }
            return result
        }

        private fun streamName(msg: AirbyteMessage): String? =
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

    data class TestCase(
        val sqlType: String,
        val values: Map<String, String>,
        val ddlFunction: (tableName: String, columnName: String) -> List<String>,
        val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.STRING,
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

        val ddl: List<String>
            get() = ddlFunction(tableName, columnName)

        val dml: List<String>
            get() {
                return values.keys.map { "INSERT INTO $tableName ($columnName) VALUES ($it)" }
            }

        val streamNamesToRecordData: Map<String, List<JsonNode>>
            get() {
                return mapOf(
                    tableName.uppercase() to
                        values.values.map {
                            Jsons.readTree("""{"${columnName.uppercase()}":$it}""")
                        }
                )
            }
    }
}
