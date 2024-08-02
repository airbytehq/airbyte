/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.oracle

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.TestClockFactory
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.consumers.BufferingOutputConsumer
import io.airbyte.cdk.data.AirbyteType
import io.airbyte.cdk.data.ArrayAirbyteType
import io.airbyte.cdk.data.LeafAirbyteType
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
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
import org.testcontainers.containers.OracleContainer

private val log = KotlinLogging.logger {}

/**
 * Reference: https://docs.oracle.com/en/database/oracle/oracle-database/23/sqlrf/Data-Types.html
 */
class OracleSourceDatatypeIntegrationTest {
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
            val output: BufferingOutputConsumer = CliRunner.runSource("discover", config())
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
            CliRunner.runSource("read", config(), configuredCatalog).messages()
        }

        val actualReads: Map<String, BufferingOutputConsumer> by lazy {
            val result: Map<String, BufferingOutputConsumer> =
                allStreamNamesAndRecordData.keys.associateWith {
                    BufferingOutputConsumer(TestClockFactory().fixed())
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
        if (streamName == testCase.tableName.uppercase()) {
            val actualSchema: JsonNode? = jsonSchema[testCase.columnName.uppercase()]
            Assertions.assertNotNull(actualSchema)
            val expectedSchema: JsonNode = testCase.airbyteType.asJsonSchema()
            Assertions.assertEquals(expectedSchema, actualSchema)
            if (testCase.cursor) {
                Assertions.assertTrue(isIncrementalSupported)
            } else {
                Assertions.assertFalse(isIncrementalSupported)
            }
        } else {
            val actualSchema: JsonNode? = jsonSchema[testCase.varrayColumnName.uppercase()]
            Assertions.assertNotNull(actualSchema)
            val expectedSchema: JsonNode =
                if (testCase.airbyteType == LeafAirbyteType.TIMESTAMP_WITH_TIMEZONE) {
                    // Annoying edge case.
                    ArrayAirbyteType(LeafAirbyteType.STRING).asJsonSchema()
                } else {
                    ArrayAirbyteType(testCase.airbyteType).asJsonSchema()
                }
            Assertions.assertEquals(expectedSchema, actualSchema)
            Assertions.assertFalse(isIncrementalSupported)
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

        val testCase: TestCase =
            testCases.find { it.streamNamesToRecordData.keys.contains(streamName) }!!
        if (
            streamName == testCase.varrayTableName.uppercase() &&
                testCase.airbyteType == LeafAirbyteType.TIMESTAMP_WITH_TIMEZONE
        ) {
            // Annoying edge case.
            return
        }
        Assertions.assertEquals(expected, actual)
    }

    companion object {
        lateinit var dbContainer: OracleContainer

        fun config(): OracleSourceConfigurationJsonObject =
            OracleContainerFactory.config(dbContainer)

        val connectionFactory: JdbcConnectionFactory by lazy {
            JdbcConnectionFactory(OracleSourceConfigurationFactory().make(config()))
        }

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
                "TO_DATE('2024-03-01','YYYY-MM-DD')" to """"2024-03-01"""",
                "TO_DATE('2024-02-29','YYYY-MM-DD')" to """"2024-02-29"""",
                "TO_DATE('2024-02-28','YYYY-MM-DD')" to """"2024-02-28"""",
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
                "" + "TO_YMINTERVAL('P10Y10M')" to """"10-10"""",
                "TO_YMINTERVAL('P1Y2M')" to """"1-2"""",
                "TO_YMINTERVAL('P2Y3M')" to """"2-3"""",
            )
        val ds2Values =
            mapOf(
                "" + "'+00 00:00:01.234567'" to """"0 0:0:1.23"""",
            )
        val dsValues =
            mapOf(
                "" + "'+00 00:00:01.234567'" to """"0 0:0:1.234567"""",
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
                TestCase("NUMBER(10,2)", numValues, LeafAirbyteType.NUMBER),
                TestCase("NUMBER(10)", intValues, LeafAirbyteType.INTEGER),
                TestCase("NUMBER", numValues, LeafAirbyteType.NUMBER),
                TestCase("FLOAT(10)", numValues, LeafAirbyteType.NUMBER),
                TestCase("FLOAT", numValues, LeafAirbyteType.NUMBER),
                TestCase("BINARY_FLOAT", numValues, LeafAirbyteType.NUMBER),
                TestCase("BINARY_DOUBLE", numValues, LeafAirbyteType.NUMBER),
                // long and raw datatypes
                TestCase(
                    "LONG",
                    longValues,
                    LeafAirbyteType.BINARY,
                    cursor = false,
                    noPK = true,
                    noVarray = true,
                ),
                TestCase(
                    "LONG RAW",
                    rawValues,
                    LeafAirbyteType.BINARY,
                    cursor = false,
                    noPK = true,
                    noVarray = true,
                ),
                TestCase(
                    "RAW(10)",
                    rawValues,
                    LeafAirbyteType.BINARY,
                    cursor = false,
                ),
                // datetime datatypes
                TestCase("DATE", dateValues, LeafAirbyteType.DATE),
                TestCase(
                    "TIMESTAMP(2) WITH LOCAL TIME ZONE",
                    tsLocalTzValues,
                    LeafAirbyteType.TIMESTAMP_WITHOUT_TIMEZONE,
                    noPK = true,
                ),
                TestCase(
                    "TIMESTAMP(2) WITH TIME ZONE",
                    tsTzValues,
                    LeafAirbyteType.TIMESTAMP_WITH_TIMEZONE,
                    noPK = true,
                ),
                TestCase(
                    "TIMESTAMP(2)",
                    tsValues,
                    LeafAirbyteType.TIMESTAMP_WITHOUT_TIMEZONE,
                    noPK = true,
                ),
                TestCase(
                    "TIMESTAMP WITH LOCAL TIME ZONE",
                    tsLocalTzValues,
                    LeafAirbyteType.TIMESTAMP_WITHOUT_TIMEZONE,
                    noPK = true,
                ),
                TestCase(
                    "TIMESTAMP WITH TIME ZONE",
                    tsTzValues,
                    LeafAirbyteType.TIMESTAMP_WITH_TIMEZONE,
                    noPK = true,
                ),
                TestCase(
                    "TIMESTAMP",
                    tsValues,
                    LeafAirbyteType.TIMESTAMP_WITHOUT_TIMEZONE,
                    noPK = true,
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
                    LeafAirbyteType.BINARY,
                    cursor = false,
                    noPK = true,
                    noVarray = true,
                ),
                TestCase("CLOB", stringValues, cursor = false, noPK = true, noVarray = true),
                TestCase("NCLOB", stringValues, cursor = false, noPK = true, noVarray = true),
                TestCase("BFILE", noValues, LeafAirbyteType.BINARY, cursor = false, noPK = true),
                // rowid datatypes
                TestCase("ROWID", noValues, cursor = false, noVarray = true),
                TestCase("UROWID(100)", noValues, cursor = false, noVarray = true),
                TestCase("UROWID", noValues, cursor = false, noVarray = true),
                // json datatype
                TestCase(
                    "JSON",
                    jsonValues,
                    LeafAirbyteType.JSONB,
                    cursor = false,
                    noPK = true,
                    noVarray = true,
                ),
                // boolean datatype
                TestCase("BOOLEAN", boolValues, LeafAirbyteType.BOOLEAN, cursor = false),
                TestCase("BOOL", boolValues, LeafAirbyteType.BOOLEAN, cursor = false),
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
                TestCase("NUMERIC(10,2)", numValues, LeafAirbyteType.NUMBER),
                TestCase("NUMERIC(10)", intValues, LeafAirbyteType.INTEGER),
                TestCase("NUMERIC", intValues, LeafAirbyteType.INTEGER),
                TestCase("DECIMAL(10,2)", numValues, LeafAirbyteType.NUMBER),
                TestCase("DECIMAL(10)", intValues, LeafAirbyteType.INTEGER),
                TestCase("DECIMAL", intValues, LeafAirbyteType.INTEGER),
                TestCase("DEC(10,2)", numValues, LeafAirbyteType.NUMBER),
                TestCase("DEC(10)", intValues, LeafAirbyteType.INTEGER),
                TestCase("DEC", intValues, LeafAirbyteType.INTEGER),
                TestCase("INTEGER", intValues, LeafAirbyteType.INTEGER),
                TestCase("INT", intValues, LeafAirbyteType.INTEGER),
                TestCase("SMALLINT", intValues, LeafAirbyteType.INTEGER),
                TestCase("FLOAT(10)", numValues, LeafAirbyteType.NUMBER),
                TestCase("FLOAT", numValues, LeafAirbyteType.NUMBER),
                TestCase("DOUBLE PRECISION", numValues, LeafAirbyteType.NUMBER),
                TestCase("REAL", numValues, LeafAirbyteType.NUMBER),
                // any types
                TestCase("SYS.AnyData", noValues, cursor = false, noPK = true, noVarray = true),
                TestCase("SYS.AnyType", noValues, cursor = false, noPK = true, noVarray = true),
                TestCase("SYS.AnyDataSet", noValues, cursor = false, noPK = true, noVarray = true),
                // xml types
                TestCase("XMLType", xmlValues, cursor = false, noPK = true, noVarray = true),
                TestCase("URItype", noValues, cursor = false, noPK = true),
                // spatial types
                TestCase("SDO_Geometry", noValues, cursor = false, noPK = true),
                TestCase("SDO_Topo_Geometry", noValues, cursor = false, noPK = true),
                // user-defined types
                TestCase(
                    "fibo_objtyp",
                    noValues,
                    cursor = false,
                    noPK = true,
                    customDDL =
                        listOf(
                            """
    CREATE TYPE IF NOT EXISTS fibo_objtyp AS OBJECT (
        predecessor INTEGER, 
        n INTEGER,
        MEMBER FUNCTION getSuccessor RETURN INTEGER)""",
                            """
    CREATE TYPE BODY IF NOT EXISTS fibo_objtyp AS
        MEMBER FUNCTION getSuccessor RETURN INTEGER AS
        BEGIN
            RETURN predecessor + n;
        END getSuccessor;
    END""",
                            """
    CREATE TABLE IF NOT EXISTS tbl_fibo_objtyp (col_fibo_objtyp fibo_objtyp)""",
                            """
    CREATE TYPE IF NOT EXISTS varray_fibo_objtyp AS VARRAY(2) OF fibo_objtyp""",
                            """
    CREATE TABLE IF NOT EXISTS tbl_varray_fibo_objtyp (
        col_varray_fibo_objtyp varray_fibo_objtyp
    )""",
                            """
    TRUNCATE TABLE tbl_varray_fibo_objtyp CASCADE""",
                        ),
                ),
                TestCase(
                    "fibo_tbltyp",
                    noValues,
                    cursor = false,
                    noPK = true,
                    noVarray = true,
                    customDDL =
                        listOf(
                            """
    CREATE TYPE IF NOT EXISTS fibo_tbltyp AS TABLE OF fibo_objtyp""",
                            """
    CREATE TABLE IF NOT EXISTS tbl_fibo_tbltyp (
        col_fibo_tbltyp fibo_tbltyp
    ) NESTED TABLE col_fibo_tbltyp STORE AS fibo_nt""",
                            """
    TRUNCATE TABLE tbl_fibo_tbltyp CASCADE""",
                        ),
                ),
                TestCase(
                    "REF fibo_objtyp",
                    noValues,
                    cursor = false,
                    noPK = true,
                    noVarray = true,
                    customDDL =
                        listOf(
                            """
    CREATE TABLE IF NOT EXISTS fibo_ref_source OF fibo_objtyp""",
                            """
    CREATE TABLE IF NOT EXISTS tbl_ref_fibo_objtyp (
        col_ref_fibo_objtyp REF fibo_objtyp SCOPE IS fibo_ref_source
    )""",
                            """
    TRUNCATE TABLE tbl_ref_fibo_objtyp CASCADE""",
                        ),
                ),
            )

        val allStreamNamesAndRecordData: Map<String, List<JsonNode>> =
            testCases.flatMap { it.streamNamesToRecordData.toList() }.toMap()

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun startAndProvisionTestContainer() {
            dbContainer =
                OracleContainerFactory.exclusive(
                    "gvenzl/oracle-free:latest-faststart",
                    OracleContainerFactory.WithNetwork,
                )
            connectionFactory.get().use { connection: Connection ->
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
        val noVarray: Boolean = false,
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

        val sqlStatements: List<String>
            get() {
                val vanillaDDL: List<String> =
                    listOf(
                        "CREATE TABLE IF NOT EXISTS $tableName " +
                            "($columnName $sqlType ${if (noPK) "" else "PRIMARY KEY"})",
                        "TRUNCATE TABLE $tableName CASCADE",
                    )
                val vanillaDML: List<String> =
                    sqlToAirbyte.keys.map { "INSERT INTO $tableName ($columnName) VALUES ($it)" }
                val varrayDDL: List<String> =
                    listOf(
                        "CREATE TYPE IF NOT EXISTS $varraySqlType AS VARRAY(2) OF $sqlType",
                        "CREATE TABLE IF NOT EXISTS $varrayTableName " +
                            "($varrayColumnName $varraySqlType)",
                        "TRUNCATE TABLE $varrayTableName",
                    )
                val varrayDML: List<String> =
                    sqlToAirbyte.keys.map {
                        "INSERT INTO $varrayTableName ($varrayColumnName) " +
                            "VALUES ($varraySqlType($it, $it))"
                    }
                val ddl: List<String> =
                    if (customDDL != null) {
                        customDDL
                    } else if (noVarray) {
                        vanillaDDL
                    } else {
                        vanillaDDL + varrayDDL
                    }
                val dml: List<String> =
                    if (noVarray) {
                        vanillaDML
                    } else {
                        vanillaDML + varrayDML
                    }
                return ddl + dml
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
