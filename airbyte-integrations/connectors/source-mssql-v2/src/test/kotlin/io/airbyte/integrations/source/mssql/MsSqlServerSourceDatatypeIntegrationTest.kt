/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.ClockFactory
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.LeafAirbyteSchemaType
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
import org.testcontainers.containers.MSSQLServerContainer

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
        lateinit var dbContainer: MSSQLServerContainer<*>

        fun config(): MsSqlServerSourceConfigurationSpecification =
            MsSqlServerContainerFactory.config(dbContainer)

        val connectionFactory: JdbcConnectionFactory by lazy {
            JdbcConnectionFactory(MsSqlServerSourceConfigurationFactory().make(config()))
        }

        // Integer types with comprehensive coverage
        val bigintValues =
            mapOf(
                "-9223372036854775808" to "-9223372036854775808",
                "9223372036854775807" to "9223372036854775807",
                "0" to "0",
                "null" to "null",
            )

        val intValues =
            mapOf(
                "10" to "10",
                "100000000" to "100000000",
                "200000000" to "200000000",
            )

        val smallintValues =
            mapOf(
                "-32768" to "-32768",
                "32767" to "32767",
                "null" to "null",
            )

        val tinyintValues =
            mapOf(
                "0" to "0",
                "255" to "255",
                "10" to "10",
                "4" to "4",
                "2" to "2",
                "null" to "null",
            )

        // Boolean/Bit types
        val bitValues =
            mapOf(
                "'1'" to "true",
                "'0'" to "false",
            )

        // Decimal and numeric types
        val decimalValues =
            mapOf(
                "0.2" to "0.2",
            )

        val numericValues =
            mapOf(
                "'99999'" to "99999",
                "null" to "null",
            )

        val moneyValues =
            mapOf(
                "'9990000.3647'" to "9990000.3647",
                "null" to "null",
            )

        val smallmoneyValues =
            mapOf(
                "'-214748.3648'" to "-214748.3648",
                "214748.3647" to "214748.3647",
                "null" to "null",
            )

        val floatValues =
            mapOf(
                "'123'" to "123.0",
                "'1234567890.1234567'" to "1.2345678901234567E9",
                "null" to "null",
            )

        val realValues =
            mapOf(
                "'123'" to "123.0",
                "'1234567890.1234567'" to "1234568000",
                "null" to "null",
            )

        // Date and time types with comprehensive coverage
        val dateValues =
            mapOf(
                "'2022-01-01'" to """"2022-01-01"""",
            )

        val smalldatetimeValues =
            mapOf(
                "'1900-01-01'" to """"1900-01-01T00:00:00.000000"""",
                "'2079-06-06'" to """"2079-06-06T00:00:00.000000"""",
                "null" to "null",
            )

        val datetimeValues =
            mapOf(
                "'1753-01-01'" to """"1753-01-01T00:00:00.000000"""",
                "'9999-12-31'" to """"9999-12-31T00:00:00.000000"""",
                "'9999-12-31T13:00:04'" to """"9999-12-31T13:00:04.000000"""",
                "'9999-12-31T13:00:04.123'" to """"9999-12-31T13:00:04.123000"""",
                "'2024-09-13 14:30:00'" to """"2024-09-13T14:30:00.000000"""",
                "null" to "null",
            )

        val datetime2Values =
            mapOf(
                "'0001-01-01'" to """"0001-01-01T00:00:00.000000"""",
                "'9999-12-31'" to """"9999-12-31T00:00:00.000000"""",
                "'9999-12-31T13:00:04.123456'" to """"9999-12-31T13:00:04.123456"""",
                "'2023-11-08T01:20:11.3733338'" to """"2023-11-08T01:20:11.373333"""",
                "null" to "null",
            )

        val timeValues =
            mapOf(
                "'13:00:01'" to """"13:00:01.000000"""",
                "'13:00:04Z'" to """"13:00:04.000000"""",
                "'13:00:04.123456Z'" to """"13:00:04.123456"""",
                "'14:30:00'" to """"14:30:00.000000"""",
                "null" to "null",
            )

        val datetimeoffsetValues =
            mapOf(
                "'2001-01-10 00:00:00 +01:00'" to """"2001-01-10T00:00:00.000000+01:00"""",
                "'9999-01-10 00:00:00 +01:00'" to """"9999-01-10T00:00:00.000000+01:00"""",
                "'2024-05-10 19:00:01.604805 +03:00'" to """"2024-05-10T19:00:01.604805+03:00"""",
                "'2024-03-02 19:08:07.1234567 +09:00'" to """"2024-03-02T19:08:07.123456+09:00"""",
                "'2024-03-02 19:08:07.12345678 +09:00'" to """"2024-03-02T19:08:07.123456+09:00"""",
                "'0001-01-01 00:00:00.0000000 +00:00'" to """"0001-01-01T00:00:00.000000Z"""",
                "null" to "null",
            )

        // String types with comprehensive Unicode and edge case coverage
        val charValues =
            mapOf(
                "'a'" to """"a"""",
                "'*'" to """"*"""",
                "null" to "null",
            )

        val varcharValues =
            mapOf(
                "'abcdef'" to """"abcdef"""",
                "'ABCD'" to """"ABCD"""",
                "'OXBEEF'" to """"OXBEEF"""",
            )

        val textValues =
            mapOf(
                "'a'" to """"a"""",
                "'abc'" to """"abc"""",
                "'Some test text 123$%^&*()_'" to """"Some test text 123$%^&*()_"""",
                "''" to """""""",
                "null" to "null",
            )

        val ncharValues =
            mapOf(
                "'a'" to """"a"""",
                "'*'" to """"*"""",
                "N'ї'" to """"ї"""",
                "null" to "null",
            )

        val nvarcharValues =
            mapOf(
                "'a'" to """"a"""",
                "'abc'" to """"abc"""",
                "N'Миші йдуть на південь, не питай чому;'" to
                    """"Миші йдуть на південь, не питай чому;"""",
                "N'櫻花分店'" to """"櫻花分店"""",
                "''" to """""""",
                "N'\\xF0\\x9F\\x9A\\x80'" to """"\\xF0\\x9F\\x9A\\x80"""",
                "null" to "null",
            )

        val ntextValues =
            mapOf(
                "'a'" to """"a"""",
                "'abc'" to """"abc"""",
                "N'Миші йдуть на південь, не питай чому;'" to
                    """"Миші йдуть на південь, не питай чому;"""",
                "N'櫻花分店'" to """"櫻花分店"""",
                "''" to """""""",
                "N'\\xF0\\x9F\\x9A\\x80'" to """"\\xF0\\x9F\\x9A\\x80"""",
                "null" to "null",
            )

        // Binary types
        val binaryValues =
            mapOf(
                "CAST( 'A' AS BINARY(1))" to """"QQ=="""",
                "null" to "null",
            )

        val varbinaryValues =
            mapOf(
                "CAST( 'ABC' AS VARBINARY)" to """"QUJD"""",
                "null" to "null",
            )

        // Special types
        val uniqueidentifierValues =
            mapOf(
                "'375CFC44-CAE3-4E43-8083-821D2DF0E626'" to
                    """"375CFC44-CAE3-4E43-8083-821D2DF0E626"""",
                "null" to "null",
            )

        val xmlValues =
            mapOf(
                "'<user><user_id>1</user_id></user>'" to """"<user><user_id>1</user_id></user>"""",
                "''" to """""""",
                "null" to "null",
            )

        // Spatial types
        val geometryValues =
            mapOf(
                "geometry::STGeomFromText('LINESTRING (100 100, 20 180, 180 180)', 0)" to
                    """"LINESTRING(100 100, 20 180, 180 180)"""",
                "null" to "null",
            )

        val geographyValues =
            mapOf(
                "geography::STGeomFromText('LINESTRING(-122.360 47.656, -122.343 47.656 )', 4326)" to
                    """"LINESTRING(-122.36 47.656, -122.343 47.656)"""",
                "null" to "null",
            )

        // Non-CDC only types
        val hierarchyidValues =
            mapOf(
                "'/1/1/'" to """"/1/1/"""",
                "null" to "null",
            )

        val sqlVariantValues =
            mapOf(
                "'a'" to """"a"""",
                "'abc'" to """"abc"""",
                "N'Миші йдуть на південь, не питай чому;'" to
                    """"Миші йдуть на південь, не питай чому;"""",
                "N'櫻花分店'" to """"櫻花分店"""",
                "''" to """""""",
                "N'\\xF0\\x9F\\x9A\\x80'" to """"\\xF0\\x9F\\x9A\\x80"""",
                "null" to "null",
            )

        // Additional test case for default values
        val intWithDefaultValues =
            mapOf(
                "1234" to "1234",
                "7878" to "7878",
                "null" to "null",
            )

        val testCases: List<TestCase> =
            listOf(
                // Integer types
                TestCase(
                    "BIGINT",
                    bigintValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.INTEGER,
                    cursor = true
                ),
                TestCase(
                    "INT",
                    intValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.INTEGER,
                    cursor = true
                ),
                TestCase(
                    "SMALLINT",
                    smallintValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.INTEGER,
                    cursor = true
                ),
                TestCase(
                    "TINYINT",
                    tinyintValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.INTEGER,
                    cursor = true
                ),
                // Boolean type
                TestCase(
                    "BIT",
                    bitValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.BOOLEAN,
                    cursor = false
                ),
                // Decimal types
                TestCase(
                    "DECIMAL(5,2)",
                    decimalValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.NUMBER,
                    cursor = true
                ),
                TestCase(
                    "NUMERIC",
                    numericValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.NUMBER,
                    cursor = true
                ),
                TestCase(
                    "MONEY",
                    moneyValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.NUMBER,
                    cursor = true
                ),
                TestCase(
                    "SMALLMONEY",
                    smallmoneyValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.NUMBER,
                    cursor = true
                ),
                TestCase(
                    "FLOAT",
                    floatValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.NUMBER,
                    cursor = true
                ),
                TestCase(
                    "REAL",
                    realValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.NUMBER,
                    cursor = true
                ),
                // Date/Time types
                TestCase(
                    "DATE",
                    dateValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.DATE,
                    cursor = true
                ),
                TestCase(
                    "SMALLDATETIME",
                    smalldatetimeValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
                    cursor = true
                ),
                TestCase(
                    "DATETIME",
                    datetimeValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
                    cursor = true
                ),
                TestCase(
                    "DATETIME2",
                    datetime2Values,
                    airbyteSchemaType = LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
                    cursor = true
                ),
                TestCase(
                    "TIME",
                    timeValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE,
                    cursor = true
                ),
                TestCase(
                    "DATETIMEOFFSET",
                    datetimeoffsetValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE,
                    cursor = true
                ),
                // String types
                TestCase(
                    "CHAR",
                    charValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.STRING,
                    cursor = true
                ),
                TestCase(
                    "VARCHAR(MAX) COLLATE Latin1_General_100_CI_AI_SC_UTF8",
                    varcharValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.STRING,
                    cursor = true
                ),
                TestCase(
                    "TEXT",
                    textValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.STRING,
                    cursor = true
                ),
                TestCase(
                    "NCHAR",
                    ncharValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.STRING,
                    cursor = true
                ),
                TestCase(
                    "NVARCHAR(MAX)",
                    nvarcharValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.STRING,
                    cursor = true
                ),
                TestCase(
                    "NTEXT",
                    ntextValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.STRING,
                    cursor = true
                ),
                // Binary types
                TestCase(
                    "BINARY",
                    binaryValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.BINARY,
                    cursor = true
                ),
                TestCase(
                    "VARBINARY(3)",
                    varbinaryValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.BINARY,
                    cursor = true
                ),
                // Special types
                TestCase(
                    "UNIQUEIDENTIFIER",
                    uniqueidentifierValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.STRING,
                    cursor = true
                ),
                TestCase(
                    "XML",
                    xmlValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.STRING,
                    cursor = true
                ),
                // Spatial types
                TestCase(
                    "GEOMETRY",
                    geometryValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.STRING,
                    cursor = true
                ),
                TestCase(
                    "GEOGRAPHY",
                    geographyValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.STRING,
                    cursor = true
                ),
                // Non-CDC only types (for source-mssql-v2 which doesn't use CDC)
                TestCase(
                    "HIERARCHYID",
                    hierarchyidValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.STRING,
                    cursor = true
                ),
                TestCase(
                    "SQL_VARIANT",
                    sqlVariantValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.STRING,
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
                MsSqlServerContainerFactory.shared(
                    "mcr.microsoft.com/mssql/server:2022-latest",
                    MsSqlServerContainerFactory.WithNetwork,
                    MsSqlServerContainerFactory.WithTestDatabase
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
                    if (customDDL != null) {
                        customDDL.map { it.format(tableName, columnName, columnName, sqlType) }
                    } else {
                        listOf(
                            "DROP TABLE IF EXISTS $tableName",
                            "CREATE TABLE $tableName " + "($columnName $sqlType)",
                        )
                    }
                val dml: List<String> =
                    sqlToAirbyte.keys.map { "INSERT INTO $tableName ($columnName) VALUES ($it)" }

                return ddl + dml
            }

        val streamNamesToRecordData: Map<String, List<JsonNode>>
            get() {
                val recordData: List<JsonNode> =
                    sqlToAirbyte.values.map { Jsons.readTree("""{"$columnName":$it}""") }
                return mapOf(tableName to recordData)
            }
    }
}
