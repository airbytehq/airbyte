/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.DatatypeTestCase
import io.airbyte.cdk.read.DatatypeTestOperations
import io.airbyte.cdk.read.DynamicDatatypeTestFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Connection
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.DynamicNode
import org.junit.jupiter.api.TestFactory
import org.junit.jupiter.api.Timeout
import org.testcontainers.containers.MSSQLServerContainer

class MsSqlServerDatatypeIntegrationTest {

    @TestFactory
    @Timeout(300)
    fun syncTests(): Iterable<DynamicNode> =
        DynamicDatatypeTestFactory(MsSqlServerDatatypeTestOperations).build(dbContainer)

    companion object {

        lateinit var dbContainer: MSSQLServerContainer<*>

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
        }
    }
}

object MsSqlServerDatatypeTestOperations :
    DatatypeTestOperations<
        MSSQLServerContainer<*>,
        MsSqlServerSourceConfigurationSpecification,
        MsSqlServerSourceConfiguration,
        MsSqlServerSourceConfigurationFactory,
        MsSqlServerDatatypeTestCase
    > {

    private val log = KotlinLogging.logger {}

    override val withGlobal: Boolean = true
    override val globalCursorMetaField: MetaField =
        MsSqlSourceOperations.MsSqlServerCdcMetaFields.CDC_CURSOR

    override fun streamConfigSpec(
        container: MSSQLServerContainer<*>
    ): MsSqlServerSourceConfigurationSpecification =
        MsSqlServerContainerFactory.config(container).also {
            it.setIncrementalValue(UserDefinedCursor())
        }

    override fun globalConfigSpec(
        container: MSSQLServerContainer<*>
    ): MsSqlServerSourceConfigurationSpecification =
        MsSqlServerContainerFactory.config(container).also { it.setIncrementalValue(Cdc()) }

    override val configFactory: MsSqlServerSourceConfigurationFactory =
        MsSqlServerSourceConfigurationFactory()

    override fun createStreams(config: MsSqlServerSourceConfiguration) {
        JdbcConnectionFactory(config).get().use { connection: Connection ->
            connection.isReadOnly = false

            // Enable CDC on the database (required before enabling CDC on tables)
            try {
                val enableDbCdcSql = "EXEC sys.sp_cdc_enable_db"
                log.info { "Enabling CDC on database: $enableDbCdcSql" }
                connection.createStatement().use { stmt -> stmt.execute(enableDbCdcSql) }
                log.info { "Successfully enabled CDC on database" }
            } catch (e: Exception) {
                log.warn {
                    "Failed to enable CDC on database (may already be enabled): ${e.message}"
                }
            }

            // Activate CDC to ensure initial LSN is available for testing
            activateCdcWithInitialLsn(connection)

            for ((_, case) in testCases) {
                for (ddl in case.ddl) {
                    log.info { "test case ${case.id}: executing $ddl" }
                    connection.createStatement().use { stmt -> stmt.execute(ddl) }
                }

                // Enable CDC for tables that support it (CDC-compatible data types)
                if (case.isGlobal) {
                    try {
                        val enableCdcSql =
                            "EXEC sys.sp_cdc_enable_table @source_schema = 'dbo', @source_name = '${case.id}', @role_name = 'CDC'"
                        log.info { "test case ${case.id}: enabling CDC with $enableCdcSql" }
                        connection.createStatement().use { stmt -> stmt.execute(enableCdcSql) }
                        log.info { "test case ${case.id}: successfully enabled CDC on table" }
                    } catch (e: Exception) {
                        log.warn { "test case ${case.id}: failed to enable CDC: ${e.message}" }
                    }
                }
            }
        }
    }

    override fun populateStreams(config: MsSqlServerSourceConfiguration) {
        JdbcConnectionFactory(config).get().use { connection: Connection ->
            connection.isReadOnly = false
            for ((_, case) in testCases) {
                for (dml in case.dml) {
                    log.info { "test case ${case.id}: executing $dml" }
                    connection.createStatement().use { stmt -> stmt.execute(dml) }
                }
            }
        }

        // Open a NEW connection to force CDC scan after commit
        JdbcConnectionFactory(config).get().use { connection: Connection ->
            try {
                connection.createStatement().use { stmt ->
                    // Manually run the CDC scan to capture all pending changes
                    stmt.execute("EXEC sys.sp_cdc_scan")
                    log.info {
                        "Executed sp_cdc_scan in new connection to capture committed changes"
                    }
                }
            } catch (e: Exception) {
                log.error { "Failed to force CDC scan after data population: ${e.message}" }
            }
        }
    }

    /**
     * Activates CDC and generates initial LSN required for testing. Creates a dummy table, enables
     * CDC on it, inserts data, and ensures LSN is available.
     */
    private fun activateCdcWithInitialLsn(connection: Connection) {
        try {
            connection.createStatement().use { stmt ->
                // Drop and recreate dummy table to ensure clean state
                stmt.execute("DROP TABLE IF EXISTS dbo.cdc_dummy")
                stmt.execute("CREATE TABLE dbo.cdc_dummy (id INT PRIMARY KEY)")
                stmt.execute(
                    "EXEC sys.sp_cdc_enable_table @source_schema = 'dbo', @source_name = 'cdc_dummy', @role_name = NULL"
                )

                // Insert data to generate LSN
                stmt.execute(
                    "INSERT INTO dbo.cdc_dummy (id) SELECT COALESCE(MAX(id), 0) + 1 FROM dbo.cdc_dummy"
                )

                // Start CDC capture job and trigger scan
                try {
                    stmt.execute("EXEC sys.sp_cdc_start_job @job_type = 'capture'")
                    Thread.sleep(2000)
                } catch (e: Exception) {
                    log.debug { "CDC capture job start failed: ${e.message}" }
                }

                try {
                    stmt.execute("EXEC sys.sp_cdc_scan")
                    Thread.sleep(1000)
                } catch (e: Exception) {
                    log.debug { "Manual CDC scan failed: ${e.message}" }
                }

                log.info { "CDC activated with dummy data for testing" }
            }
        } catch (e: Exception) {
            log.warn { "CDC activation failed: ${e.message}" }
        }
    }

    // Data type test values
    val booleanValues =
        mapOf(
            "0" to "false",
            "1" to "true",
            "'true'" to "true",
            "'false'" to "false",
            "NULL" to "null",
        )

    val integerValues =
        mapOf(
            "10" to "10",
            "100000000" to "100000000",
            "200000000" to "200000000",
            "-2147483648" to "-2147483648",
            "2147483647" to "2147483647",
            "NULL" to "null",
        )

    val bigintValues =
        mapOf(
            "-9223372036854775808" to "-9223372036854775808",
            "9223372036854775807" to "9223372036854775807",
            "0" to "0",
            "NULL" to "null",
        )

    val smallintValues =
        mapOf(
            "-32768" to "-32768",
            "32767" to "32767",
            "NULL" to "null",
        )

    val tinyintValues =
        mapOf(
            "0" to "0",
            "255" to "255",
            "NULL" to "null",
        )

    val decimalValues =
        mapOf(
            "999.33" to "999.33",
            "NULL" to "null",
        )

    val numericValues =
        mapOf(
            "'99999'" to "99999",
            "NULL" to "null",
        )

    val moneyValues =
        mapOf(
            "'9990000.3647'" to "9990000.3647",
            "NULL" to "null",
        )

    val smallmoneyValues =
        mapOf(
            "'-214748.3648'" to "-214748.3648",
            "214748.3647" to "214748.3647",
            "NULL" to "null",
        )

    val floatValues =
        mapOf(
            "'123'" to "123.0",
            "'1234567890.1234567'" to "1234567890.1234567",
            "NULL" to "null",
        )

    val realValues =
        mapOf(
            "'123'" to "123.0",
            "'1234567890.1234567'" to "1234568000",
            "NULL" to "null",
        )

    val dateValues =
        mapOf(
            "'0001-01-01'" to """"0001-01-01"""",
            "'9999-12-31'" to """"9999-12-31"""",
            "'1999-01-08'" to """"1999-01-08"""",
            "NULL" to "null",
        )

    val smalldatetimeValues =
        mapOf(
            "'1900-01-01'" to """"1900-01-01T00:00:00.000000"""",
            "'2079-06-06'" to """"2079-06-06T00:00:00.000000"""",
            "NULL" to "null",
        )

    val datetimeValues =
        mapOf(
            "'1753-01-01'" to """"1753-01-01T00:00:00.000000"""",
            "'9999-12-31'" to """"9999-12-31T00:00:00.000000"""",
            "'9999-12-31T13:00:04'" to """"9999-12-31T13:00:04.000000"""",
            "'9999-12-31T13:00:04.123'" to """"9999-12-31T13:00:04.123000"""",
            "NULL" to "null",
        )

    val datetime2Values =
        mapOf(
            "'0001-01-01'" to """"0001-01-01T00:00:00.000000"""",
            "'9999-12-31'" to """"9999-12-31T00:00:00.000000"""",
            "'9999-12-31T13:00:04.123456'" to """"9999-12-31T13:00:04.123456"""",
            "'2023-11-08T01:20:11.3733338'" to """"2023-11-08T01:20:11.373333"""",
            "NULL" to "null",
        )

    val timeValues =
        mapOf(
            "'13:00:01'" to """"13:00:01.000000"""",
            "'13:00:04Z'" to """"13:00:04.000000"""",
            "'13:00:04.123456Z'" to """"13:00:04.123456"""",
            "NULL" to "null",
        )

    val datetimeoffsetValues =
        mapOf(
            "'2001-01-10 00:00:00 +01:00'" to """"2001-01-10T00:00:00.000000+01:00"""",
            "'9999-01-10 00:00:00 +01:00'" to """"9999-01-10T00:00:00.000000+01:00"""",
            "'2024-05-10 19:00:01.604805 +03:00'" to """"2024-05-10T19:00:01.604805+03:00"""",
            "'2024-03-02 19:08:07.1234567 +09:00'" to """"2024-03-02T19:08:07.123456+09:00"""",
            "'0001-01-01 00:00:00.0000000 +00:00'" to """"0001-01-01T00:00:00.000000Z"""",
            "NULL" to "null",
        )

    val charValues =
        mapOf(
            "'a'" to """"a                                                 """",
            "'*'" to """"*                                                 """",
            "'abc'" to """"abc                                               """",
            "'Hello World!'" to """"Hello World!                                      """",
            "'Test123'" to """"Test123                                           """",
            "''" to """"                                                  """",
            "NULL" to "null",
        )

    val varcharValues =
        mapOf(
            "''" to """""""",
            "'*'" to """"*"""",
            "'a'" to """"a"""",
            "'abc'" to """"abc"""",
            "N'Миші йдуть на південь, не питай чому;'" to
                """"Миші йдуть на південь, не питай чому;"""",
            "N'櫻花分店'" to """"櫻花分店"""",
            "NULL" to "null",
        )

    val textValues =
        mapOf(
            "''" to """""""",
            "'Some test text 123\$%^&*()_'" to """"Some test text 123$%^&*()_"""",
            "'a'" to """"a"""",
            "'abc'" to """"abc"""",
            "NULL" to "null",
        )

    val ncharValues =
        mapOf(
            "'a'" to """"a                                                 """",
            "'*'" to """"*                                                 """",
            "'abc'" to """"abc                                               """",
            "N'Миші йдуть на південь, не питай чому;'" to
                """"Миші йдуть на південь, не питай чому;             """",
            "N'櫻花分店'" to """"櫻花分店                                              """",
            "''" to """"                                                  """",
            "NULL" to "null",
        )

    val nvarcharValues =
        mapOf(
            "''" to """""""",
            "'*'" to """"*"""",
            "'a'" to """"a"""",
            "'abc'" to """"abc"""",
            "N'Миші йдуть на південь, не питай чому;'" to
                """"Миші йдуть на південь, не питай чому;"""",
            "N'櫻花分店'" to """"櫻花分店"""",
            "NULL" to "null",
        )

    val binaryValues =
        mapOf(
            "CAST( 'A' AS BINARY(1))" to """"QQ=="""",
            "NULL" to "null",
        )

    val varbinaryValues =
        mapOf(
            "CAST( 'ABC' AS VARBINARY)" to """"QUJD"""",
            "NULL" to "null",
        )

    val uniqueidentifierValues =
        mapOf(
            "'375CFC44-CAE3-4E43-8083-821D2DF0E626'" to
                """"375CFC44-CAE3-4E43-8083-821D2DF0E626"""",
            "NULL" to "null",
        )

    val xmlValues =
        mapOf(
            "''" to """""""",
            "'<user><user_id>1</user_id></user>'" to """"<user><user_id>1</user_id></user>"""",
            "NULL" to "null",
        )

    val geometryValues =
        mapOf(
            "geometry::STGeomFromText('LINESTRING (100 100, 20 180, 180 180)', 0)" to
                """"LINESTRING(100 100, 20 180, 180 180)"""",
            "NULL" to "null",
        )

    val geographyValues =
        mapOf(
            "geography::STGeomFromText('LINESTRING(-122.360 47.656, -122.343 47.656 )', 4326)" to
                """"LINESTRING(-122.36 47.656, -122.343 47.656)"""",
            "NULL" to "null",
        )

    val hierarchyidValues =
        mapOf(
            "'/1/1/'" to """"/1/1/"""",
            "NULL" to "null",
        )

    override val testCases: Map<String, MsSqlServerDatatypeTestCase> =
        listOf(
                // Integer types
                MsSqlServerDatatypeTestCase(
                    "BIGINT",
                    bigintValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MsSqlServerDatatypeTestCase(
                    "INT",
                    integerValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MsSqlServerDatatypeTestCase(
                    "SMALLINT",
                    smallintValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MsSqlServerDatatypeTestCase(
                    "TINYINT",
                    tinyintValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                // Boolean type
                MsSqlServerDatatypeTestCase(
                    "BIT",
                    booleanValues,
                    LeafAirbyteSchemaType.BOOLEAN,
                ),
                // Decimal types
                MsSqlServerDatatypeTestCase(
                    "DECIMAL(5,2)",
                    decimalValues,
                    LeafAirbyteSchemaType.NUMBER,
                ),
                MsSqlServerDatatypeTestCase(
                    "NUMERIC",
                    numericValues,
                    LeafAirbyteSchemaType.NUMBER,
                ),
                MsSqlServerDatatypeTestCase(
                    "MONEY",
                    moneyValues,
                    LeafAirbyteSchemaType.NUMBER,
                ),
                MsSqlServerDatatypeTestCase(
                    "SMALLMONEY",
                    smallmoneyValues,
                    LeafAirbyteSchemaType.NUMBER,
                ),
                // Float types
                MsSqlServerDatatypeTestCase(
                    "FLOAT",
                    floatValues,
                    LeafAirbyteSchemaType.NUMBER,
                ),
                MsSqlServerDatatypeTestCase(
                    "REAL",
                    realValues,
                    LeafAirbyteSchemaType.NUMBER,
                ),
                // Date/Time types
                MsSqlServerDatatypeTestCase(
                    "DATE",
                    dateValues,
                    LeafAirbyteSchemaType.DATE,
                ),
                MsSqlServerDatatypeTestCase(
                    "SMALLDATETIME",
                    smalldatetimeValues,
                    LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
                ),
                MsSqlServerDatatypeTestCase(
                    "DATETIME",
                    datetimeValues,
                    LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
                ),
                MsSqlServerDatatypeTestCase(
                    "DATETIME2",
                    datetime2Values,
                    LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
                ),
                MsSqlServerDatatypeTestCase(
                    "TIME",
                    timeValues,
                    LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE,
                ),
                MsSqlServerDatatypeTestCase(
                    "DATETIMEOFFSET",
                    datetimeoffsetValues,
                    LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE,
                ),
                // String types
                MsSqlServerDatatypeTestCase(
                    "CHAR(50)",
                    charValues,
                    LeafAirbyteSchemaType.STRING,
                ),
                MsSqlServerDatatypeTestCase(
                    "NVARCHAR(MAX)",
                    varcharValues,
                    LeafAirbyteSchemaType.STRING,
                ),
                MsSqlServerDatatypeTestCase(
                    "TEXT",
                    textValues,
                    LeafAirbyteSchemaType.STRING,
                ),
                MsSqlServerDatatypeTestCase(
                    "NCHAR(50)",
                    ncharValues,
                    LeafAirbyteSchemaType.STRING,
                ),
                MsSqlServerDatatypeTestCase(
                    "NVARCHAR(MAX)",
                    nvarcharValues,
                    LeafAirbyteSchemaType.STRING,
                ),
                MsSqlServerDatatypeTestCase(
                    "NTEXT",
                    nvarcharValues,
                    LeafAirbyteSchemaType.STRING,
                ),
                // Binary types
                MsSqlServerDatatypeTestCase(
                    "BINARY(1)",
                    binaryValues,
                    LeafAirbyteSchemaType.BINARY,
                ),
                MsSqlServerDatatypeTestCase(
                    "VARBINARY(3)",
                    varbinaryValues,
                    LeafAirbyteSchemaType.BINARY,
                ),
                // Special types
                MsSqlServerDatatypeTestCase(
                    "UNIQUEIDENTIFIER",
                    uniqueidentifierValues,
                    LeafAirbyteSchemaType.STRING,
                ),
                MsSqlServerDatatypeTestCase(
                    "XML",
                    xmlValues,
                    LeafAirbyteSchemaType.STRING,
                ),
                // Spatial types
                MsSqlServerDatatypeTestCase(
                    "GEOMETRY",
                    geometryValues,
                    LeafAirbyteSchemaType.STRING,
                ),
                MsSqlServerDatatypeTestCase(
                    "GEOGRAPHY",
                    geographyValues,
                    LeafAirbyteSchemaType.STRING,
                ),
                // Hierarchy type - only for non-CDC tests
                MsSqlServerDatatypeTestCase(
                    "HIERARCHYID",
                    hierarchyidValues,
                    LeafAirbyteSchemaType.STRING,
                    isGlobal = false, // CDC doesn't support hierarchyid properly
                ),
            )
            .associateBy { it.id }
}

data class MsSqlServerDatatypeTestCase(
    val sqlType: String,
    val sqlToAirbyte: Map<String, String>,
    override val expectedAirbyteSchemaType: AirbyteSchemaType,
    override val isGlobal: Boolean = true,
) : DatatypeTestCase {

    override val isStream: Boolean
        get() = true

    private val typeName: String
        get() =
            sqlType
                .replace("[^a-zA-Z0-9]".toRegex(), " ")
                .trim()
                .replace(" +".toRegex(), "_")
                .lowercase()

    override val id: String
        get() = "tbl_$typeName"

    override val fieldName: String
        get() = "col_$typeName"

    override val expectedData: List<String>
        get() = sqlToAirbyte.values.map { """{"${fieldName}":$it}""" }

    val ddl: List<String>
        get() =
            listOf(
                "DROP TABLE IF EXISTS $id",
                "CREATE TABLE $id " + "(pk INT IDENTITY(1,1) PRIMARY KEY, $fieldName $sqlType)",
            )

    val dml: List<String>
        get() =
            sqlToAirbyte.keys.map {
                if (it == "NULL") {
                    "INSERT INTO $id DEFAULT VALUES"
                } else {
                    "INSERT INTO $id ($fieldName) VALUES ($it)"
                }
            }
}
