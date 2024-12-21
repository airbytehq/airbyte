/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.ClockFactory
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.mssql.config_spec.MsSqlServerSourceConfigurationSpecification
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

private val log = KotlinLogging.logger {}

class MsSqlServerSourceDatatypeIntegrationTest {
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
            val expectedSchema: JsonNode = testCase.airbyteSchemaType.asJsonSchema()
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
        lateinit var dbContainer: MsSqlServercontainer

        fun config(): MsSqlServerSourceConfigurationSpecification =
            dbContainer.config

        val connectionFactory: JdbcConnectionFactory by lazy {
            JdbcConnectionFactory(MsSqlServerSourceConfigurationFactory().make(config()))
        }

        val bitValues =
            mapOf(
                "'1'" to "true",
                "'0'" to "false",
            )

        val longBitValues =
            mapOf(
                "'10101010'" to """-86""",
            )

        val stringValues =
            mapOf(
                "'abcdef'" to """"abcdef"""",
                "'ABCD'" to """"ABCD"""",
                "'OXBEEF'" to """"OXBEEF"""",
            )

        val jsonValues = mapOf("""'{"col1": "v1"}'""" to """"{\"col1\": \"v1\"}"""")

        val yearValues =
            mapOf(
                "1992" to """1992""",
                "2002" to """2002""",
                "70" to """1970""",
            )

        val decimalValues =
            mapOf(
                "0.2" to """0.2""",
            )

        val zeroPrecisionDecimalValues =
            mapOf(
                "2" to """2""",
            )

        val tinyintValues =
            mapOf(
                "10" to "10",
                "4" to "4",
                "2" to "2",
            )

        val intValues =
            mapOf(
                "10" to "10",
                "100000000" to "100000000",
                "200000000" to "200000000",
            )

        val dateValues =
            mapOf(
                "'2022-01-01'" to """"2022-01-01"""",
            )

        val timeValues =
            mapOf(
                "'14:30:00'" to """"14:30:00.000000"""",
            )

        val dateTimeValues =
            mapOf(
                "'2024-09-13 14:30:00'" to """"2024-09-13T14:30:00.000000"""",
                //"'2024-09-13T14:40:00.000+00:00'" to """"2024-09-13T14:40:00.000000""""
            )

        val timestampValues =
            mapOf(
                "'2024-09-12 14:30:00'" to """"2024-09-12T14:30:00.000000Z"""",
                "CONVERT_TZ('2024-09-12 14:30:00', 'America/Los_Angeles', 'UTC')" to
                    """"2024-09-12T21:30:00.000000Z"""",
            )

        val booleanValues =
            mapOf(
                "TRUE" to "true",
                "FALSE" to "false",
            )

        val enumValues =
            mapOf(
                "'a'" to """"a"""",
                "'b'" to """"b"""",
                "'c'" to """"c"""",
            )

        // Encoded into base64
        val binaryValues =
            mapOf(
                "0x89504E470D0A1A0A0000000D49484452" to """"iVBORw0KGgoAAAANSUhEUg=="""",
            )

        val testCases: List<TestCase> =
            listOf(
                TestCase(
                    "VARCHAR(10)",
                    stringValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.STRING
                ),
                TestCase(
                    "DECIMAL(10,2)",
                    decimalValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.NUMBER
                ),
                TestCase("FLOAT", decimalValues, airbyteSchemaType = LeafAirbyteSchemaType.NUMBER),
                TestCase(
                    "FLOAT(7)",
                    decimalValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.NUMBER
                ),
                TestCase(
                    "FLOAT(53)",
                    decimalValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.NUMBER
                ),
                TestCase(
                    "TINYINT",
                    tinyintValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.INTEGER
                ),
                TestCase(
                    "SMALLINT",
                    tinyintValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.INTEGER
                ),
                TestCase("BIGINT", intValues, airbyteSchemaType = LeafAirbyteSchemaType.INTEGER),
                TestCase("INT", intValues, airbyteSchemaType = LeafAirbyteSchemaType.INTEGER),
                TestCase("DATE", dateValues, airbyteSchemaType = LeafAirbyteSchemaType.DATE),
                TestCase(
                    "DATETIME",
                    dateTimeValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
                ),
                TestCase(
                    "TIME",
                    timeValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE
                ),
                TestCase(
                    "VARBINARY(255)",
                    binaryValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.BINARY,
                    cursor = true,
                    noPK = false
                ),
                TestCase(
                    "BIT",
                    bitValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.BOOLEAN,
                    cursor = false
                ),
            )

        val allStreamNamesAndRecordData: Map<String, List<JsonNode>> =
            testCases.flatMap { it.streamNamesToRecordData.toList() }.toMap()

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun startAndProvisionTestContainer() {
            dbContainer =
                MsSqlServerContainerFactory.exclusive(
                    MsSqlServerImage.SQLSERVER_2022,
                    MsSqlServerContainerFactory.WithNetwork,
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
        val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.STRING,
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
                        "CREATE TABLE ${dbContainer.schemaName}.$tableName " +
                            "($columnName $sqlType ${if (noPK) "" else "PRIMARY KEY"})",
                    )
                val dml: List<String> =
                    sqlToAirbyte.keys.map { "INSERT INTO ${dbContainer.schemaName}.$tableName ($columnName) VALUES ($it)" }

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
