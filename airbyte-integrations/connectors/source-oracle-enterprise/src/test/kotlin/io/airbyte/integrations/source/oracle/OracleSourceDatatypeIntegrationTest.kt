/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.oracle

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.ClockFactory
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.ArrayAirbyteSchemaType
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
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.DynamicContainer
import org.junit.jupiter.api.DynamicNode
import org.junit.jupiter.api.DynamicTest
import org.junit.jupiter.api.TestFactory
import org.junit.jupiter.api.Timeout
import org.junit.jupiter.api.function.Executable
import org.testcontainers.containers.OracleContainer

class OracleSourceDatatypeIntegrationTest {
    private val log = KotlinLogging.logger {}

    @TestFactory
    @Timeout(300)
    fun syncTests(): Iterable<DynamicNode> {
        val actual = DiscoverAndReadAll { dbContainer }
        val discoverAndReadAllTest: DynamicNode =
            DynamicTest.dynamicTest("discover-and-read-all", actual)
        val testCases: List<DynamicNode> =
            OracleDatatypeTestCases.allStreamNamesAndRecordData.keys.map { streamName: String ->
                DynamicContainer.dynamicContainer(streamName, dynamicTests(actual, streamName))
            }
        return listOf(discoverAndReadAllTest) + testCases
    }

    private fun dynamicTests(actual: DiscoverAndReadAll, streamName: String): List<DynamicTest> {
        val jdbcTests: List<DynamicTest> =
            listOf(
                DynamicTest.dynamicTest("discover-jdbc") {
                    discover(streamName, actual.jdbcStreams[streamName])
                },
                DynamicTest.dynamicTest("records-jdbc") {
                    records(streamName, actual.jdbcMessagesByStream[streamName])
                },
            )
        if (!isCdcStream(streamName)) {
            return jdbcTests
        }
        val cdcTests: List<DynamicTest> =
            listOf(
                DynamicTest.dynamicTest("discover-cdc") {
                    discover(streamName, actual.cdcStreams[streamName])
                },
                DynamicTest.dynamicTest("records-cdc") {
                    records(streamName, actual.cdcMessagesByStream[streamName])
                },
            )
        return jdbcTests + cdcTests
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
        val testCase: OracleDatatypeTestCases.TestCase = findTestCase(streamName)!!
        val jsonSchema: JsonNode = actualStream!!.jsonSchema?.get("properties")!!
        if (streamName == testCase.tableName.uppercase()) {
            val actualSchema: JsonNode? = jsonSchema[testCase.columnName.uppercase()]
            Assertions.assertNotNull(actualSchema)
            val expectedSchema: JsonNode = testCase.AirbyteSchemaType.asJsonSchema()
            Assertions.assertEquals(expectedSchema, actualSchema)
        } else {
            val actualSchema: JsonNode? = jsonSchema[testCase.varrayColumnName.uppercase()]
            Assertions.assertNotNull(actualSchema)
            val expectedSchema: JsonNode =
                if (testCase.AirbyteSchemaType == LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE) {
                    // Annoying edge case.
                    ArrayAirbyteSchemaType(LeafAirbyteSchemaType.STRING).asJsonSchema()
                } else {
                    ArrayAirbyteSchemaType(testCase.AirbyteSchemaType).asJsonSchema()
                }
            Assertions.assertEquals(expectedSchema, actualSchema)
        }
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
        val actual: JsonNode = sortedRecordData(actualRecordData)
        log.info { "test case $streamName: emitted records $actual" }
        val expected: JsonNode =
            sortedRecordData(OracleDatatypeTestCases.allStreamNamesAndRecordData[streamName]!!)

        val testCase: OracleDatatypeTestCases.TestCase = findTestCase(streamName)!!
        if (
            streamName == testCase.varrayTableName.uppercase() &&
                testCase.AirbyteSchemaType == LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE
        ) {
            // Annoying edge case.
            return
        }
        Assertions.assertEquals(expected, actual)
    }

    companion object {
        lateinit var dbContainer: OracleContainer

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun startAndProvisionTestContainer() {
            dbContainer =
                OracleContainerFactory.exclusive(
                    "gvenzl/oracle-free:23.6-full-faststart",
                    OracleContainerFactory.WithCdc,
                )
        }
    }
}

private fun isCdcStream(streamName: String): Boolean {
    if (streamName.length > 30) {
        // LogMiner does not support table and column names exceeding 30 characters.
        // https://docs.oracle.com/en/database/oracle/oracle-database/23/sutil/oracle-logminer-utility.html
        return false
    }
    val testCase: OracleDatatypeTestCases.TestCase = findTestCase(streamName) ?: return false
    if (testCase.noLogMinerSupport) {
        // LogMiner does not support all Oracle Database datatypes.
        // https://docs.oracle.com/en/database/oracle/oracle-database/23/sutil/oracle-logminer-utility.html
        return false
    }
    if (testCase.varrayTableName.uppercase() == streamName) {
        // LogMiner does not support UDTs, which include VARRAYs.
        // https://docs.oracle.com/en/database/oracle/oracle-database/23/sutil/oracle-logminer-utility.html
        return false
    }
    return true
}

private fun findTestCase(streamName: String): OracleDatatypeTestCases.TestCase? =
    OracleDatatypeTestCases.testCases.find {
        streamName.uppercase() in it.streamNamesToRecordData.keys
    }

class DiscoverAndReadAll(databaseContainerSupplier: () -> OracleContainer) : Executable {
    private val log = KotlinLogging.logger {}
    private val dbContainer: OracleContainer by lazy { databaseContainerSupplier() }

    // CDC DISCOVER and READ intermediate values and final results.
    // Intermediate values are present here as `lateinit var` instead of local variables
    // to make debugging of individual test cases easier.
    lateinit var cdcConfigSpec: OracleSourceConfigurationSpecification
    lateinit var cdcConfig: OracleSourceConfiguration
    lateinit var cdcStreams: Map<String, AirbyteStream>
    lateinit var cdcConfiguredCatalog: ConfiguredAirbyteCatalog
    lateinit var cdcInitialReadOutput: BufferingOutputConsumer
    lateinit var cdcCheckpoint: AirbyteStateMessage
    lateinit var cdcSubsequentReadOutput: BufferingOutputConsumer
    lateinit var cdcMessages: List<AirbyteMessage>
    lateinit var cdcMessagesByStream: Map<String, BufferingOutputConsumer>
    // Same as above but for JDBC.
    lateinit var jdbcConfigSpec: OracleSourceConfigurationSpecification
    lateinit var jdbcConfig: OracleSourceConfiguration
    lateinit var jdbcConnectionFactory: JdbcConnectionFactory
    lateinit var jdbcStreams: Map<String, AirbyteStream>
    lateinit var jdbcConfiguredCatalog: ConfiguredAirbyteCatalog
    lateinit var jdbcReadOutput: BufferingOutputConsumer
    lateinit var jdbcMessages: List<AirbyteMessage>
    lateinit var jdbcMessagesByStream: Map<String, BufferingOutputConsumer>

    override fun execute() {
        log.info { "Generating JDBC config." }
        jdbcConfigSpec = OracleContainerFactory.configSpecification(dbContainer)
        jdbcConfig = OracleSourceConfigurationFactory().make(jdbcConfigSpec)
        jdbcConnectionFactory = JdbcConnectionFactory(jdbcConfig)
        log.info { "Generating CDC config." }
        cdcConfigSpec =
            OracleContainerFactory.configSpecification(dbContainer).apply {
                setIncrementalConfigurationSpecificationValue(CdcCursorConfigurationSpecification())
            }
        cdcConfig = OracleSourceConfigurationFactory().make(cdcConfigSpec)
        log.info { "Executing DDL statements." }
        jdbcConnectionFactory.get().use { connection: Connection ->
            for (case in OracleDatatypeTestCases.testCases) {
                for (sql in case.ddlSqlStatements) {
                    log.info { "test case ${case.id}: executing $sql" }
                    connection.createStatement().use { stmt -> stmt.execute(sql) }
                }
            }
        }
        log.info { "Running JDBC DISCOVER operation." }
        jdbcStreams = discover(jdbcConfigSpec)
        jdbcConfiguredCatalog = configuredCatalog(jdbcStreams)
        log.info { "Running CDC DISCOVER operation." }
        cdcStreams = discover(cdcConfigSpec)
        cdcConfiguredCatalog =
            configuredCatalog(
                cdcStreams.filterKeys { streamName: String -> isCdcStream(streamName) }
            )
        log.info { "Running initial CDC READ operation." }
        cdcInitialReadOutput = CliRunner.source("read", cdcConfigSpec, cdcConfiguredCatalog).run()
        Assertions.assertNotEquals(emptyList<AirbyteStateMessage>(), cdcInitialReadOutput.states())
        cdcCheckpoint = cdcInitialReadOutput.states().last()
        Assertions.assertEquals(emptyList<AirbyteRecordMessage>(), cdcInitialReadOutput.records())
        Assertions.assertEquals(emptyList<AirbyteLogMessage>(), cdcInitialReadOutput.logs())
        log.info { "Executing DML statements." }
        jdbcConnectionFactory.get().use { connection: Connection ->
            for (case in OracleDatatypeTestCases.testCases) {
                for (sql in case.dmlSqlStatements) {
                    log.info { "test case ${case.id}: executing $sql" }
                    connection.createStatement().use { stmt -> stmt.execute(sql) }
                }
            }
        }
        log.info { "Running subsequent CDC READ operation." }
        cdcSubsequentReadOutput =
            CliRunner.source("read", cdcConfigSpec, cdcConfiguredCatalog, listOf(cdcCheckpoint))
                .run()
        Assertions.assertNotEquals(
            emptyList<AirbyteStateMessage>(),
            cdcSubsequentReadOutput.states()
        )
        Assertions.assertNotEquals(
            emptyList<AirbyteRecordMessage>(),
            cdcSubsequentReadOutput.records()
        )
        Assertions.assertEquals(emptyList<AirbyteLogMessage>(), cdcSubsequentReadOutput.logs())
        cdcMessages = cdcSubsequentReadOutput.messages()
        cdcMessagesByStream = byStream(cdcMessages)
        log.info { "Running JDBC READ operation." }
        jdbcReadOutput = CliRunner.source("read", jdbcConfigSpec, jdbcConfiguredCatalog).run()
        Assertions.assertNotEquals(emptyList<AirbyteStateMessage>(), jdbcReadOutput.states())
        Assertions.assertNotEquals(emptyList<AirbyteRecordMessage>(), jdbcReadOutput.records())
        Assertions.assertEquals(emptyList<AirbyteLogMessage>(), jdbcReadOutput.logs())
        jdbcMessages = jdbcReadOutput.messages()
        jdbcMessagesByStream = byStream(jdbcMessages)
        log.info { "Done." }
    }

    private fun discover(
        configSpec: OracleSourceConfigurationSpecification
    ): Map<String, AirbyteStream> {
        val output: BufferingOutputConsumer = CliRunner.source("discover", configSpec).run()
        val streams: Map<String, AirbyteStream> =
            output.catalogs().firstOrNull()?.streams?.filterNotNull()?.associateBy { it.name }
                ?: mapOf()
        Assertions.assertFalse(streams.isEmpty())
        return streams
    }

    private fun transformCdcStreams(
        streams: Map<String, AirbyteStream>
    ): Map<String, AirbyteStream> =
        streams.filterKeys { streamName: String -> isCdcStream(streamName) }

    private fun configuredCatalog(streams: Map<String, AirbyteStream>): ConfiguredAirbyteCatalog {
        val configuredStreams: List<ConfiguredAirbyteStream> =
            OracleDatatypeTestCases.allStreamNamesAndRecordData.keys
                .mapNotNull { streams[it] }
                .map(CatalogHelpers::toDefaultConfiguredStream)
        for (configuredStream in configuredStreams) {
            if (
                configuredStream.stream.supportedSyncModes.contains(SyncMode.INCREMENTAL) &&
                    configuredStream.stream.sourceDefinedCursor == true
            ) {
                configuredStream.syncMode = SyncMode.INCREMENTAL
                configuredStream.cursorField = listOf(OracleSourceCdcScn.id)
            } else {
                configuredStream.syncMode = SyncMode.FULL_REFRESH
            }
        }
        return ConfiguredAirbyteCatalog().withStreams(configuredStreams)
    }

    private fun byStream(messages: List<AirbyteMessage>): Map<String, BufferingOutputConsumer> {
        val result: Map<String, BufferingOutputConsumer> =
            OracleDatatypeTestCases.allStreamNamesAndRecordData.keys.associateWith {
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

/**
 * Reference: https://docs.oracle.com/en/database/oracle/oracle-database/23/sqlrf/Data-Types.html
 */
object OracleDatatypeTestCases {

    val noValues = mapOf<String, String>()

    var char1Values =
        mapOf(
            "'a'" to """"a"""",
            "'b'" to """"b"""",
            "'c'" to """"c"""",
        )
    val char10Values =
        mapOf(
            "'abcdef'" to """"abcdef    """",
            "'ABCDEF'" to """"ABCDEF    """",
            "'OXBEEF'" to """"OXBEEF    """",
        )
    val stringValues =
        mapOf(
            "'abcdef'" to """"abcdef"""",
            "'ABCDEF'" to """"ABCDEF"""",
            "'OXBEEF'" to """"OXBEEF"""",
        )
    val intValues =
        mapOf(
            "123" to "123",
            "456" to "456",
            "789" to "789",
        )
    val numValues =
        mapOf(
            "45.67" to "45.67",
            "98.76" to "98.76",
            "0.12" to "0.12",
        )
    val longValues =
        mapOf(
            "utl_raw.cast_to_raw('ABC')" to """"NDE0MjQz"""",
            "utl_raw.cast_to_raw('DEF')" to """"NDQ0NTQ2"""",
            "utl_raw.cast_to_raw('GHI')" to """"NDc0ODQ5"""",
        )
    val rawValues =
        mapOf(
            "utl_raw.cast_to_raw('ABC')" to """"QUJD"""",
            "utl_raw.cast_to_raw('DEF')" to """"REVG"""",
            "utl_raw.cast_to_raw('GHI')" to """"R0hJ"""",
        )
    val dateValues =
        mapOf(
            "TO_DATE('2024-03-01','YYYY-MM-DD')" to """"2024-03-01T00:00:00.000000"""",
            "TO_DATE('2024-02-29','YYYY-MM-DD')" to """"2024-02-29T00:00:00.000000"""",
            "TO_DATE('2024-02-28 12:34:56','YYYY-MM-DD HH24:MI:SS')" to
                """"2024-02-28T12:34:56.000000"""",
        )
    val tsValues =
        mapOf(
            "TIMESTAMP '2024-03-01 06:07:08.9'" to """"2024-03-01T06:07:08.900000"""",
        )
    val tsTzValues =
        mapOf(
            "TIMESTAMP '2024-03-01 06:07:08.9 Europe/Paris'" to
                """"2024-03-01T06:07:08.900000+01:00"""",
        )
    val tsLocalTzValues =
        mapOf(
            "TIMESTAMP '2024-03-01 06:07:08.9'" to """"2024-03-01T06:07:08.900000"""",
        )
    val ymValues =
        mapOf(
            "TO_YMINTERVAL('P10Y10M')" to """"10-10"""",
            "TO_YMINTERVAL('P1Y2M')" to """"1-2"""",
            "TO_YMINTERVAL('P2Y3M')" to """"2-3"""",
        )
    val ds2Values =
        mapOf(
            "'+00 00:00:01.234567'" to """"0 0:0:1.23"""",
        )
    val dsValues =
        mapOf(
            "'+00 00:00:01.234567'" to """"0 0:0:1.234567"""",
        )
    val jsonValues =
        mapOf(
            """'{"foo":"bar"}'""" to """{"foo":"bar"}""",
        )
    val boolValues =
        mapOf(
            "1 = 1" to "true",
            "0 = 1" to "false",
        )
    val xmlValues =
        mapOf(
            "'<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + "<list_book></list_book>'" to
                """"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<list_book/>\n"""",
        )

    val testCases: List<TestCase> =
        listOf(
            // character datatypes
            TestCase("CHAR(10 BYTE)", char10Values),
            TestCase("CHAR(10 CHAR)", char10Values),
            TestCase("CHAR(10)", char10Values),
            TestCase("CHAR", char1Values),
            TestCase("VARCHAR2(10 BYTE)", stringValues),
            TestCase("VARCHAR2(10 CHAR)", stringValues),
            TestCase("VARCHAR2(10)", stringValues),
            TestCase("NCHAR(10)", char10Values),
            TestCase("NCHAR", char1Values),
            TestCase("NVARCHAR2(10)", stringValues),
            // number datatypes
            TestCase("NUMBER(10,2)", numValues, LeafAirbyteSchemaType.NUMBER),
            TestCase("NUMBER(10)", intValues, LeafAirbyteSchemaType.INTEGER),
            TestCase("NUMBER", numValues, LeafAirbyteSchemaType.NUMBER),
            TestCase("FLOAT(10)", numValues, LeafAirbyteSchemaType.NUMBER),
            TestCase("FLOAT", numValues, LeafAirbyteSchemaType.NUMBER),
            TestCase("BINARY_FLOAT", numValues, LeafAirbyteSchemaType.NUMBER),
            TestCase("BINARY_DOUBLE", numValues, LeafAirbyteSchemaType.NUMBER),
            // long and raw datatypes
            TestCase(
                "LONG",
                longValues,
                LeafAirbyteSchemaType.BINARY,
                cursor = false,
                noVarray = true,
                noLogMinerSupport = true,
            ),
            TestCase(
                "LONG RAW",
                rawValues,
                LeafAirbyteSchemaType.BINARY,
                cursor = false,
                noVarray = true,
                noLogMinerSupport = true,
            ),
            TestCase(
                "RAW(10)",
                rawValues,
                LeafAirbyteSchemaType.BINARY,
                cursor = false,
            ),
            // datetime datatypes
            TestCase("DATE", dateValues, LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE),
            TestCase(
                "TIMESTAMP(2) WITH LOCAL TIME ZONE",
                tsLocalTzValues,
                LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
            ),
            TestCase(
                "TIMESTAMP(2) WITH TIME ZONE",
                tsTzValues,
                LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE,
            ),
            TestCase(
                "TIMESTAMP(2)",
                tsValues,
                LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
            ),
            TestCase(
                "TIMESTAMP WITH LOCAL TIME ZONE",
                tsLocalTzValues,
                LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
            ),
            TestCase(
                "TIMESTAMP WITH TIME ZONE",
                tsTzValues,
                LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE,
            ),
            TestCase(
                "TIMESTAMP",
                tsValues,
                LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
            ),
            TestCase("INTERVAL YEAR(4) TO MONTH", ymValues),
            TestCase("INTERVAL YEAR TO MONTH", ymValues),
            TestCase("INTERVAL DAY(1) TO SECOND(2)", ds2Values),
            TestCase("INTERVAL DAY(1) TO SECOND", dsValues),
            TestCase("INTERVAL DAY TO SECOND(2)", ds2Values),
            TestCase("INTERVAL DAY TO SECOND", dsValues),
            // large object datatypes
            TestCase(
                "BLOB",
                rawValues,
                LeafAirbyteSchemaType.BINARY,
                cursor = false,
                noVarray = true,
                noLogMinerSupport = true,
            ),
            TestCase(
                "CLOB",
                stringValues,
                cursor = false,
                noVarray = true,
                noLogMinerSupport = true
            ),
            TestCase(
                "NCLOB",
                stringValues,
                cursor = false,
                noVarray = true,
                noLogMinerSupport = true
            ),
            TestCase(
                "BFILE",
                noValues,
                LeafAirbyteSchemaType.BINARY,
                cursor = false,
                noLogMinerSupport = true
            ),
            // rowid datatypes
            TestCase("ROWID", noValues, cursor = false, noVarray = true, noLogMinerSupport = true),
            TestCase(
                "UROWID(100)",
                noValues,
                cursor = false,
                noVarray = true,
                noLogMinerSupport = true
            ),
            TestCase("UROWID", noValues, cursor = false, noVarray = true, noLogMinerSupport = true),
            // json datatype
            TestCase(
                "JSON",
                jsonValues,
                LeafAirbyteSchemaType.JSONB,
                cursor = false,
                noVarray = true,
                noLogMinerSupport = true,
            ),
            // boolean datatype
            TestCase(
                "BOOLEAN",
                boolValues,
                LeafAirbyteSchemaType.BOOLEAN,
                cursor = false,
                noLogMinerSupport = true
            ),
            TestCase(
                "BOOL",
                boolValues,
                LeafAirbyteSchemaType.BOOLEAN,
                cursor = false,
                noLogMinerSupport = true
            ),
            // ANSI supported datatypes
            TestCase("CHARACTER VARYING (10)", stringValues),
            TestCase("CHARACTER (10)", char10Values),
            TestCase("CHAR VARYING (10)", stringValues),
            TestCase("NCHAR VARYING (10)", stringValues),
            TestCase("VARCHAR(10)", stringValues),
            TestCase("NATIONAL CHARACTER VARYING (10)", stringValues),
            TestCase("NATIONAL CHARACTER (10)", char10Values),
            TestCase("NATIONAL CHAR VARYING (10)", stringValues),
            TestCase("NATIONAL CHAR (10)", char10Values),
            TestCase("NUMERIC(10,2)", numValues, LeafAirbyteSchemaType.NUMBER),
            TestCase("NUMERIC(10)", intValues, LeafAirbyteSchemaType.INTEGER),
            TestCase("NUMERIC", intValues, LeafAirbyteSchemaType.INTEGER),
            TestCase("DECIMAL(10,2)", numValues, LeafAirbyteSchemaType.NUMBER),
            TestCase("DECIMAL(10)", intValues, LeafAirbyteSchemaType.INTEGER),
            TestCase("DECIMAL", intValues, LeafAirbyteSchemaType.INTEGER),
            TestCase("DEC(10,2)", numValues, LeafAirbyteSchemaType.NUMBER),
            TestCase("DEC(10)", intValues, LeafAirbyteSchemaType.INTEGER),
            TestCase("DEC", intValues, LeafAirbyteSchemaType.INTEGER),
            TestCase("INTEGER", intValues, LeafAirbyteSchemaType.INTEGER),
            TestCase("INT", intValues, LeafAirbyteSchemaType.INTEGER),
            TestCase("SMALLINT", intValues, LeafAirbyteSchemaType.INTEGER),
            TestCase("DOUBLE PRECISION", numValues, LeafAirbyteSchemaType.NUMBER),
            TestCase("REAL", numValues, LeafAirbyteSchemaType.NUMBER),
            // any types
            TestCase(
                "SYS.AnyData",
                noValues,
                cursor = false,
                noVarray = true,
                noLogMinerSupport = true
            ),
            TestCase(
                "SYS.AnyType",
                noValues,
                cursor = false,
                noVarray = true,
                noLogMinerSupport = true
            ),
            TestCase(
                "SYS.AnyDataSet",
                noValues,
                cursor = false,
                noVarray = true,
                noLogMinerSupport = true
            ),
            // xml types
            TestCase(
                "XMLType",
                xmlValues,
                cursor = false,
                noVarray = true,
                noLogMinerSupport = true
            ),
            TestCase("URItype", noValues, cursor = false, noLogMinerSupport = true),
            // spatial types
            TestCase("SDO_Geometry", noValues, cursor = false, noLogMinerSupport = true),
            TestCase("SDO_Topo_Geometry", noValues, cursor = false, noLogMinerSupport = true),
            // user-defined types
            TestCase(
                "fibo_objtyp",
                noValues,
                cursor = false,
                noLogMinerSupport = true,
                customDDL =
                    listOf(
                        """
    CREATE TYPE fibo_objtyp AS OBJECT (
        predecessor INTEGER, 
        n INTEGER,
        MEMBER FUNCTION getSuccessor RETURN INTEGER)""",
                        """
    CREATE TYPE BODY fibo_objtyp AS
        MEMBER FUNCTION getSuccessor RETURN INTEGER AS
        BEGIN
            RETURN predecessor + n;
        END getSuccessor;
    END""",
                        """
    CREATE TABLE tbl_fibo_objtyp (
        id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
        col_fibo_objtyp fibo_objtyp
    )""",
                        """
    ALTER TABLE tbl_fibo_objtyp ADD SUPPLEMENTAL LOG DATA (ALL) COLUMNS""",
                        """
    CREATE TYPE varray_fibo_objtyp AS VARRAY(2) OF fibo_objtyp""",
                        """
    CREATE TABLE tbl_varray_fibo_objtyp (
        id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
        col_varray_fibo_objtyp varray_fibo_objtyp
    )""",
                        """
    ALTER TABLE tbl_varray_fibo_objtyp ADD SUPPLEMENTAL LOG DATA (ALL) COLUMNS""",
                    ),
            ),
            TestCase(
                "fibo_tbltyp",
                noValues,
                cursor = false,
                noVarray = true,
                noLogMinerSupport = true,
                customDDL =
                    listOf(
                        """
    CREATE TYPE fibo_tbltyp AS TABLE OF fibo_objtyp""",
                        """
    CREATE TABLE tbl_fibo_tbltyp (
        id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
        col_fibo_tbltyp fibo_tbltyp
    ) NESTED TABLE col_fibo_tbltyp STORE AS fibo_nt""",
                        """
    ALTER TABLE tbl_fibo_tbltyp ADD SUPPLEMENTAL LOG DATA (ALL) COLUMNS""",
                    ),
            ),
            TestCase(
                "REF fibo_objtyp",
                noValues,
                cursor = false,
                noVarray = true,
                noLogMinerSupport = true,
                customDDL =
                    listOf(
                        """
    CREATE TABLE fibo_ref_source OF fibo_objtyp""",
                        """
    CREATE TABLE tbl_ref_fibo_objtyp (
        id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
        col_ref_fibo_objtyp REF fibo_objtyp SCOPE IS fibo_ref_source
    )""",
                        """
    ALTER TABLE tbl_ref_fibo_objtyp ADD SUPPLEMENTAL LOG DATA (ALL) COLUMNS""",
                    ),
            ),
        )

    val allStreamNamesAndRecordData: Map<String, List<JsonNode>> =
        testCases.flatMap { it.streamNamesToRecordData.toList() }.toMap()

    data class TestCase(
        val sqlType: String,
        val sqlToAirbyte: Map<String, String>,
        val AirbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.STRING,
        val cursor: Boolean = true,
        val noVarray: Boolean = false,
        val noLogMinerSupport: Boolean = false,
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

        val varraySqlType: String
            get() = "varray_$id"

        val varrayTableName: String
            get() = "tbl_varray_$id"

        val columnName: String
            get() = "col_$id"

        val varrayColumnName: String
            get() = "col_varray_$id"

        val ddlSqlStatements: List<String>
            get() {
                if (customDDL != null) return customDDL
                val vanillaDDL: List<String> =
                    listOf(
                        "CREATE TABLE $tableName " +
                            "(id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY," +
                            " $columnName $sqlType)",
                        "ALTER TABLE $tableName ADD SUPPLEMENTAL LOG DATA (ALL) COLUMNS",
                    )
                if (noVarray) return vanillaDDL
                val varrayDDL: List<String> =
                    listOf(
                        "CREATE TYPE $varraySqlType AS VARRAY(2) OF $sqlType",
                        "CREATE TABLE $varrayTableName " +
                            "(id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY," +
                            " $varrayColumnName $varraySqlType)",
                        "ALTER TABLE $varrayTableName ADD SUPPLEMENTAL LOG DATA (ALL) COLUMNS",
                    )
                return vanillaDDL + varrayDDL
            }

        val dmlSqlStatements: List<String>
            get() {
                val vanillaDML: List<String> =
                    sqlToAirbyte.keys.map { "INSERT INTO $tableName ($columnName) VALUES ($it)" }
                if (noVarray) return vanillaDML
                val varrayDML: List<String> =
                    sqlToAirbyte.keys.map {
                        "INSERT INTO $varrayTableName ($varrayColumnName) " +
                            "VALUES ($varraySqlType($it, $it))"
                    }
                return vanillaDML + varrayDML
            }

        val streamNamesToRecordData: Map<String, List<JsonNode>>
            get() {
                val recordData: List<JsonNode> =
                    sqlToAirbyte.values.map {
                        Jsons.readTree("""{"${columnName.uppercase()}":$it}""")
                    }
                if (noVarray) {
                    return mapOf(tableName.uppercase() to recordData)
                }
                val varrayRecordData: List<JsonNode> =
                    sqlToAirbyte.values.map {
                        Jsons.readTree("""{"${varrayColumnName.uppercase()}":[$it,$it]}""")
                    }
                return mapOf(
                    tableName.uppercase() to recordData,
                    varrayTableName.uppercase() to varrayRecordData,
                )
            }
    }
}
