/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.ClockFactory
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.mssql.*
import io.airbyte.integrations.source.mssql.config_spec.MsSqlServerSourceConfigurationSpecification
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStream
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

class MsSqlServerCdcDatatypeIntegrationTest {
    @TestFactory
    @Timeout(300)
    fun syncTests(): Iterable<DynamicNode> {
        val read: DynamicNode =
            DynamicTest.dynamicTest("read") {
                Assertions.assertFalse(LazyValues.actualReads.isEmpty())
            }
        val cases: List<DynamicNode> =
            allStreamNamesAndRecordData.keys.map { streamName: String ->
                DynamicContainer.dynamicContainer(
                    streamName,
                    listOf(
                        DynamicTest.dynamicTest("records") { records(streamName) },
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
                    .map {
                        CatalogHelpers.toDefaultConfiguredStream(it)
                            .withCursorField(
                                listOf(MsSqlServerStreamFactory.MsSqlServerCdcMetaFields.CDC_CURSOR.id),
                            )
                    }

            for (configuredStream in configuredStreams) {
                if (configuredStream.stream.supportedSyncModes.contains(SyncMode.INCREMENTAL)) {
                    configuredStream.syncMode = SyncMode.INCREMENTAL
                }
            }
            ConfiguredAirbyteCatalog().withStreams(configuredStreams)
        }

        val allReadMessages: List<AirbyteMessage> by lazy {
            // only get messsages from the 2nd run
            val lastStateMessageFromFirstRun =
                CliRunner.source("read", config(), configuredCatalog).run().states().last()

            // insert
            connectionFactory
                .get()
                .also { it.isReadOnly = false }
                .use { connection: Connection ->
                    for (case in testCases) {
                        for (sql in case.sqlInsertStatements) {
                            log.info { "test case ${case.id}: executing $sql" }
                            connection.createStatement().use { stmt -> stmt.execute(sql) }
                        }
                    }
                }

            // Run it in dbz mode on 2nd time:
            CliRunner.source(
                "read",
                config(),
                configuredCatalog,
                listOf(lastStateMessageFromFirstRun)
            )
                .run()
                .messages()
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
                else -> null
            }
    }

    private fun records(streamName: String) {
        val actualRead: BufferingOutputConsumer? = LazyValues.actualReads[streamName]
        Assertions.assertNotNull(actualRead)

        fun sortedRecordData(data: List<JsonNode>): JsonNode =
            Jsons.createArrayNode().apply { addAll(data.sortedBy { it.toString() }) }

        val actualRecords: List<AirbyteRecordMessage> = actualRead?.records() ?: listOf()

        val records = actualRecords.mapNotNull { it.data }

        records.forEach { jsonNode ->
            if (jsonNode is ObjectNode) {
                // Remove unwanted fields
                jsonNode.remove("_ab_cdc_updated_at")
                jsonNode.remove("_ab_cdc_deleted_at")
                jsonNode.remove("_ab_cdc_cursor")
                jsonNode.remove("_ab_cdc_log_file")
                jsonNode.remove("_ab_cdc_log_pos")
            }
        }
        val actual: JsonNode = sortedRecordData(records)

        log.info { "test case $streamName: emitted records $actual" }
        val expected: JsonNode = sortedRecordData(allStreamNamesAndRecordData[streamName]!!)

        Assertions.assertEquals(expected, actual)
    }

    companion object {
        lateinit var dbContainer: MsSqlServercontainer

        fun config(): MsSqlServerSourceConfigurationSpecification = dbContainer.config

        val connectionFactory: JdbcConnectionFactory by lazy {
            JdbcConnectionFactory(MsSqlServerSourceConfigurationFactory().make(config()))
        }

        val bitValues =
            mapOf(
                "b'1'" to "true",
                "b'0'" to "false",
            )

        val longBitValues =
            mapOf(
                "b'10101010'" to """"qg=="""",
            )

        val stringValues =
            mapOf(
                "'abcdef'" to """"abcdef"""",
                "'ABCD'" to """"ABCD"""",
                "'OXBEEF'" to """"OXBEEF"""",
            )

        val yearValues =
            mapOf(
                "1992" to """1992""",
                "2002" to """2002""",
                "70" to """1970""",
            )

        val precisionTwoDecimalValues =
            mapOf(
                "0.2" to """0.2""",
            )

        val floatValues =
            mapOf(
                "123.4567" to """123.4567""",
            )

        val zeroPrecisionDecimalValues =
            mapOf(
                "2" to """2.0""",
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
                "'2024-09-13T14:40:00+00:00'" to """"2024-09-13T14:40:00.000000"""",
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

        val testCases: List<TestCase> =
            listOf(
                /*TestCase(
                    "BOOLEAN",
                    booleanValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.BOOLEAN,
                    cursor = false,
                ),*/
                TestCase(
                    "VARCHAR(10)",
                    stringValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.STRING,
                ),
                /*TestCase(
                    "DECIMAL(10,2)",
                    precisionTwoDecimalValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.NUMBER,
                ),
                TestCase(
                    "FLOAT",
                    precisionTwoDecimalValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.NUMBER
                ),
                TestCase(
                    "FLOAT(7)",
                    floatValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.NUMBER,
                ),
                TestCase(
                    "FLOAT(53)",
                    floatValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.NUMBER,
                ),
                TestCase(
                    "TINYINT",
                    tinyintValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.INTEGER,
                ),
                TestCase(
                    "SMALLINT",
                    tinyintValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.INTEGER,
                ),
                TestCase("BIGINT", intValues, airbyteSchemaType = LeafAirbyteSchemaType.INTEGER),
                TestCase("INT", intValues, airbyteSchemaType = LeafAirbyteSchemaType.INTEGER),
                TestCase("DATE", dateValues, airbyteSchemaType = LeafAirbyteSchemaType.DATE),
                TestCase(
                    "TIMESTAMP",
                    timestampValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE,
                ),
                TestCase(
                    "DATETIME",
                    dateTimeValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
                ),
                TestCase(
                    "TIME",
                    timeValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE,
                ),
                TestCase(
                    "BIT",
                    bitValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.BOOLEAN,
                    cursor = false,
                ),*/
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
                    var exception: Exception? = null
                    for (case in testCases) {
                        for (sql in case.sqlStatements) {
                            log.info { "test case ${case.id}: executing $sql" }
                            try {
                                connection.createStatement().use { stmt -> stmt.execute(sql) }
                            } catch (e: Exception) {
                                log.info { "SGX caught error when executing $sql: $e" }
                                exception = e
                            }
                        }
                    }
                    if (exception != null) {
                        throw exception
                    }
                }
        }
    }

    data class TestCase(
        val sqlType: String,
        val sqlToAirbyte: Map<String, String>,
        val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.STRING,
        val cursor: Boolean = true,
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
                return listOf(
                    "CREATE TABLE $tableName " + "($columnName $sqlType PRIMARY KEY)",
                )
            }

        val sqlInsertStatements: List<String>
            get() {
                val result =
                    listOf("USE test;") +
                            sqlToAirbyte.keys.map {
                                "INSERT INTO $tableName ($columnName) VALUES ($it)"
                            }
                return result
            }

        val streamNamesToRecordData: Map<String, List<JsonNode>>
            get() {
                val recordData: List<JsonNode> =
                    sqlToAirbyte.values.map { Jsons.readTree("""{"${columnName}":$it}""") }
                return mapOf(tableName to recordData)
            }
    }
}
