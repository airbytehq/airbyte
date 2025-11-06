/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.test.fixtures.tests

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.ClockFactory
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.test.fixtures.cleanup.TestAssetResourceNamer
import io.airbyte.cdk.test.fixtures.connector.IntegrationTestOperations
import io.airbyte.cdk.test.fixtures.connector.TestDbExecutor
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
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.DynamicContainer
import org.junit.jupiter.api.DynamicNode
import org.junit.jupiter.api.DynamicTest
import org.junit.jupiter.api.TestFactory
import org.junit.jupiter.api.Timeout
import org.junit.jupiter.api.function.Executable

abstract class FieldTypeMapperTest {
    private val log = KotlinLogging.logger {}

    abstract val configSpec: ConfigurationSpecification
    abstract val executor: TestDbExecutor
    abstract val setupDdl: List<String>
    abstract val testCases: List<TestCase>

    private val allStreamNamesAndRecordData: Map<String, List<JsonNode>> by lazy {
        testCases.flatMap { it.streamNamesToRecordData.toList() }.toMap()
    }

    private fun findTestCase(streamName: String): TestCase? {
        return testCases.find { streamName.uppercase() in it.streamNamesToRecordData.keys }
    }

    @TestFactory
    @Timeout(300)
    fun tests(): Iterable<DynamicNode> {
        log.info { "Executing setup DDL statements." }
        for (stmt in setupDdl) {
            executor.executeUpdate(stmt)
        }
        log.info { "Executing insert DML statements." }
        for (stmt in testCases.flatMap { case -> case.dml }) {
            executor.executeUpdate(stmt)
        }
        val actual =
            DiscoverAndReadAll(IntegrationTestOperations(configSpec), allStreamNamesAndRecordData)
        val discoverAndReadAllTest: DynamicNode =
            DynamicTest.dynamicTest("discover-and-read-all", actual)
        val testCases: List<DynamicNode> =
            testCases.map {
                DynamicContainer.dynamicContainer(it.testName, dynamicTests(actual, it.tableName))
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
        val actualSchema: JsonNode? = jsonSchema[testCase.columnName]
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
        private val ops: IntegrationTestOperations,
        private val allStreamNamesAndRecordData: Map<String, List<JsonNode>>,
    ) : Executable {
        private val log = KotlinLogging.logger {}

        // JDBC DISCOVER and READ intermediate values and final results.
        // Intermediate values are present here as `lateinit var` instead of local variables
        // to make debugging of individual test cases easier.
        lateinit var jdbcStreams: Map<String, AirbyteStream>
        lateinit var jdbcConfiguredCatalog: ConfiguredAirbyteCatalog
        lateinit var jdbcReadOutput: BufferingOutputConsumer
        lateinit var jdbcMessages: List<AirbyteMessage>
        lateinit var jdbcMessagesByStream: Map<String, BufferingOutputConsumer>

        override fun execute() {
            log.info { "Running JDBC DISCOVER operation." }
            jdbcStreams = ops.discover()
            jdbcConfiguredCatalog = configuredCatalog(jdbcStreams)
            log.info { "Running JDBC READ operation." }
            jdbcReadOutput = ops.sync(jdbcConfiguredCatalog)
            Assertions.assertNotEquals(emptyList<AirbyteStateMessage>(), jdbcReadOutput.states())
            Assertions.assertNotEquals(emptyList<AirbyteRecordMessage>(), jdbcReadOutput.records())
            Assertions.assertEquals(emptyList<AirbyteLogMessage>(), jdbcReadOutput.logs())
            jdbcMessages = jdbcReadOutput.messages()
            jdbcMessagesByStream = byStream(jdbcMessages)
            log.info { "Done." }
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
                    //  configuredStream.cursorField = listOf(...)
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
        val namespace: String,
        val sqlType: String,
        val values: Map<String, String>,
        val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.STRING,
        val testName: String =
            sqlType
                .replace("\\[]".toRegex(), "_array")
                .replace("[^a-zA-Z0-9]".toRegex(), " ")
                .trim()
                .replace(" +".toRegex(), "_")
                .uppercase()
    ) {
        companion object {
            val testAssetResourceNamer = TestAssetResourceNamer()
        }

        val tableName = testAssetResourceNamer.getName()

        val columnName = "TYPE_COL"

        val dml: List<String>
            get() {
                return values.keys.map {
                    "INSERT INTO \"$namespace\".\"$tableName\" (\"$columnName\") VALUES ($it)"
                }
            }

        val streamNamesToRecordData: Map<String, List<JsonNode>>
            get() {
                return mapOf(
                    tableName.uppercase() to
                        values.values.map { Jsons.readTree("""{"${columnName}":$it}""") }
                )
            }
    }

    // pads the json string map values to a fixed length
    protected fun Map<String, String>.withLength(length: Int): Map<String, String> {
        return this.mapValues {
            val currentLength = it.value.length - 2 // exclude the quotes
            if (currentLength > length) {
                throw IllegalArgumentException("$length is out of bounds")
            } else {
                // make it longer
                it.value.replace("\"$".toRegex(), "\"".padStart(length - currentLength + 1))
            }
        }
    }
}

object AnsiSql {

    val intValues =
        mapOf(
            "null" to "null",
            "1" to "1",
            "0" to "0",
            "-1" to "-1",
            "2147483647" to "2147483647",
            "-2147483648" to "-2147483648",
        )

    val smallIntValues =
        mapOf(
            "null" to "null",
            "1" to "1",
            "0" to "0",
            "-1" to "-1",
            "32767" to "32767",
            "-32768" to "-32768",
        )

    val bigIntValues =
        mapOf(
            "null" to "null",
            "1" to "1",
            "0" to "0",
            "-1" to "-1",
            "9223372036854775807" to "9223372036854775807",
            "-9223372036854775808" to "-9223372036854775808",
        )

    val decimalValues =
        mapOf(
            "null" to "null",
            "123456789.123456789" to "123456789.123456789",
            "-123456789.123456789" to "-123456789.123456789",
            "0.000000001" to "0.000000001",
            "9999999999.999999999" to "9999999999.999999999",
            "-9999999999.999999999" to "-9999999999.999999999",
        )

    val realValues =
        mapOf(
            "null" to "null",
            "3.402E+38" to "3.402E+38",
            "-3.402E+38" to "-3.402E+38",
            "1.175E-37" to "1.175E-37",
            "0.0" to "0.0",
        )

    val doubleValues =
        mapOf(
            "null" to "null",
            "1.7976931348623157E+308" to "1.7976931348623157E+308",
            "-1.7976931348623157E+308" to "-1.7976931348623157E+308",
            "2.2250738585072014E-308" to "2.2250738585072014E-308",
            "0.0" to "0.0",
        )

    val booleanValues =
        mapOf(
            "null" to "null",
            "true" to "true",
            "false" to "false",
        )

    val charValues =
        mapOf(
            "null" to "null",
            "'a'" to "\"a\"",
            "'Z'" to "\"Z\"",
            "'1'" to "\"1\"",
            "' '" to "\" \"",
        )

    val varcharValues =
        mapOf(
            "null" to "null",
            "'Hello'" to "\"Hello\"",
            "'12345'" to "\"12345\"",
            "' '" to "\" \"",
            "''" to "\"\"",
        )

    val dateValues =
        mapOf(
            "null" to "null",
            "'1000-01-01'" to "\"1000-01-01\"",
            "'9999-12-31'" to "\"9999-12-31\"",
        )

    val timeValues =
        mapOf(
            "null" to "null",
            "'00:00:00'" to "\"00:00:00.000000\"",
            "'23:59:59'" to "\"23:59:59.000000\"",
        )

    val timestampValues =
        mapOf(
            "null" to "null",
            "'1000-01-01 00:00:00'" to "\"1000-01-01T00:00:00.000000\"",
            "'9999-12-31 23:59:59'" to "\"9999-12-31T23:59:59.000000\"",
        )

    val timestampWithTzValues =
        mapOf(
            "null" to "null",
            "'1000-01-01 00:00:00'" to "\"1000-01-01T00:00:00.000000Z\"",
            "'9999-12-31 23:59:59'" to "\"9999-12-31T23:59:59.000000Z\"",
        )
}

object ExtendedSql {
    val xmlValues =
        mapOf(
            "null" to "null",
            "'<root><node>value</node></root>'" to "\"<root><node>value</node></root>\""
        )

    val jsonValues =
        mapOf(
            "'{}'" to "\"{}\"",
            "'{\"k\": null}'" to "\"{\\\"k\\\": null}\"",
            "'{\"k\": \"v\"}'" to "\"{\\\"k\\\": \\\"v\\\"}\""
        )
}
