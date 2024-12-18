/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

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
import org.testcontainers.containers.MySQLContainer

class MySqlDatatypeIntegrationTest {

    @TestFactory
    @Timeout(300)
    fun syncTests(): Iterable<DynamicNode> =
        DynamicDatatypeTestFactory(MySqlDatatypeTestOperations).build(dbContainer)

    companion object {

        lateinit var dbContainer: MySQLContainer<*>

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun startAndProvisionTestContainer() {
            dbContainer = MysqlContainerFactory.shared("mysql:8.0", MysqlContainerFactory.WithCdc)
        }
    }
}

object MySqlDatatypeTestOperations :
    DatatypeTestOperations<
        MySQLContainer<*>,
        MysqlSourceConfigurationSpecification,
        MysqlSourceConfiguration,
        MysqlSourceConfigurationFactory,
        MySqlDatatypeTestCase
    > {

    private val log = KotlinLogging.logger {}

    override val withGlobal: Boolean = true
    override val globalCursorMetaField: MetaField = MysqlCdcMetaFields.CDC_CURSOR

    override fun streamConfigSpec(
        container: MySQLContainer<*>
    ): MysqlSourceConfigurationSpecification =
        MysqlContainerFactory.config(container).also { it.setMethodValue(UserDefinedCursor) }

    override fun globalConfigSpec(
        container: MySQLContainer<*>
    ): MysqlSourceConfigurationSpecification =
        MysqlContainerFactory.config(container).also { it.setMethodValue(CdcCursor()) }

    override val configFactory: MysqlSourceConfigurationFactory = MysqlSourceConfigurationFactory()

    override fun createStreams(config: MysqlSourceConfiguration) {
        JdbcConnectionFactory(config).get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { it.execute("CREATE DATABASE IF NOT EXISTS test") }
            connection.createStatement().use { it.execute("USE test") }
            for ((_, case) in testCases) {
                for (ddl in case.ddl) {
                    log.info { "test case ${case.id}: executing $ddl" }
                    connection.createStatement().use { stmt -> stmt.execute(ddl) }
                }
            }
        }
    }

    override fun populateStreams(config: MysqlSourceConfiguration) {
        JdbcConnectionFactory(config).get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { it.execute("USE test") }
            for ((_, case) in testCases) {
                for (dml in case.dml) {
                    log.info { "test case ${case.id}: executing $dml" }
                    connection.createStatement().use { stmt -> stmt.execute(dml) }
                }
            }
        }
    }

    val bitValues =
        mapOf(
            "b'1'" to "true",
            "b'0'" to "false",
        )

    val multiBitValues =
        mapOf(
            "b'10101010'" to """"qg=="""",
        )

    val stringValues =
        mapOf(
            "'abcdef'" to """"abcdef"""",
            "'ABCD'" to """"ABCD"""",
            "'OXBEEF'" to """"OXBEEF"""",
        )

    val jsonValues = mapOf("""'{"col1": "v1"}'""" to """{"col1":"v1"}""")

    val yearValues =
        mapOf(
            "1992" to """1992""",
            "2002" to """2002""",
            "70" to """1970""",
        )

    val bigDecimalValues =
        mapOf(
            "10000000000000000000000000000000000000000.0001" to
                "10000000000000000000000000000000000000000.0001",
        )

    val bigIntegerValues =
        mapOf(
            "10000000000000000000000000000000000000000" to
                "10000000000000000000000000000000000000000",
        )

    val decimalValues =
        mapOf(
            "0.2" to """0.2""",
        )

    val floatValues =
        mapOf(
            "123.4567" to """123.4567""",
        )

    val doubleValues =
        mapOf(
            "123.4567" to """123.45670318603516""",
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
            "'0600-12-02'" to """"0600-12-02"""",
            "'1752-09-09'" to """"1752-09-09"""",
        )

    val timeValues =
        mapOf(
            "'14:30:00'" to """"14:30:00.000000"""",
        )

    val dateTimeValues =
        mapOf(
            "'2024-09-13 14:30:00'" to """"2024-09-13T14:30:00.000000"""",
            "'2024-09-13T14:40:00+00:00'" to """"2024-09-13T14:40:00.000000"""",
            "'1752-09-01 14:30:00'" to """"1752-09-01T14:30:00.000000"""",
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
            "X'89504E470D0A1A0A0000000D49484452'" to """"iVBORw0KGgoAAAANSUhEUg=="""",
        )

    override val testCases: Map<String, MySqlDatatypeTestCase> =
        listOf(
                MySqlDatatypeTestCase(
                    "BOOLEAN",
                    booleanValues,
                    LeafAirbyteSchemaType.BOOLEAN,
                ),
                MySqlDatatypeTestCase(
                    "VARCHAR(10)",
                    stringValues,
                    LeafAirbyteSchemaType.STRING,
                ),
                MySqlDatatypeTestCase(
                    "DECIMAL(60,4)",
                    bigDecimalValues,
                    LeafAirbyteSchemaType.NUMBER,
                ),
                MySqlDatatypeTestCase(
                    "DECIMAL(60,0)",
                    bigIntegerValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlDatatypeTestCase(
                    "DECIMAL(10,2)",
                    decimalValues,
                    LeafAirbyteSchemaType.NUMBER,
                ),
                MySqlDatatypeTestCase(
                    "DECIMAL(10,2) UNSIGNED",
                    decimalValues,
                    LeafAirbyteSchemaType.NUMBER,
                ),
                MySqlDatatypeTestCase(
                    "DECIMAL UNSIGNED",
                    zeroPrecisionDecimalValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlDatatypeTestCase("FLOAT", floatValues, LeafAirbyteSchemaType.NUMBER),
                MySqlDatatypeTestCase(
                    "FLOAT(34)",
                    floatValues,
                    LeafAirbyteSchemaType.NUMBER,
                ),
                MySqlDatatypeTestCase(
                    "FLOAT(7,4)",
                    floatValues,
                    LeafAirbyteSchemaType.NUMBER,
                    // Disable CDC testing for this case:
                    //  - 123.4567 is rendered as 123.45670318603516
                    //    not strictly equal due to IEEE754 encoding artifacts, but acceptable.
                    isGlobal = false,
                ),
                MySqlDatatypeTestCase(
                    "FLOAT(53,8)",
                    doubleValues,
                    LeafAirbyteSchemaType.NUMBER,
                ),
                MySqlDatatypeTestCase("DOUBLE", decimalValues, LeafAirbyteSchemaType.NUMBER),
                MySqlDatatypeTestCase(
                    "DOUBLE UNSIGNED",
                    decimalValues,
                    LeafAirbyteSchemaType.NUMBER,
                ),
                MySqlDatatypeTestCase(
                    "TINYINT",
                    tinyintValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlDatatypeTestCase(
                    "TINYINT UNSIGNED",
                    tinyintValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlDatatypeTestCase(
                    "SMALLINT",
                    tinyintValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlDatatypeTestCase(
                    "MEDIUMINT",
                    tinyintValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlDatatypeTestCase("BIGINT", intValues, LeafAirbyteSchemaType.INTEGER),
                MySqlDatatypeTestCase(
                    "SMALLINT UNSIGNED",
                    tinyintValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlDatatypeTestCase(
                    "MEDIUMINT UNSIGNED",
                    tinyintValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlDatatypeTestCase(
                    "BIGINT UNSIGNED",
                    intValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlDatatypeTestCase("INT", intValues, LeafAirbyteSchemaType.INTEGER),
                MySqlDatatypeTestCase(
                    "INT UNSIGNED",
                    intValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlDatatypeTestCase("DATE", dateValues, LeafAirbyteSchemaType.DATE),
                MySqlDatatypeTestCase(
                    "TIMESTAMP",
                    timestampValues,
                    LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE,
                ),
                MySqlDatatypeTestCase(
                    "DATETIME",
                    dateTimeValues,
                    LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
                ),
                MySqlDatatypeTestCase(
                    "TIME",
                    timeValues,
                    LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE,
                ),
                MySqlDatatypeTestCase("YEAR", yearValues, LeafAirbyteSchemaType.INTEGER),
                MySqlDatatypeTestCase(
                    "VARBINARY(255)",
                    binaryValues,
                    LeafAirbyteSchemaType.BINARY,
                ),
                MySqlDatatypeTestCase(
                    "BIT",
                    bitValues,
                    LeafAirbyteSchemaType.BOOLEAN,
                ),
                MySqlDatatypeTestCase(
                    "BIT(8)",
                    multiBitValues,
                    LeafAirbyteSchemaType.BINARY,
                ),
                MySqlDatatypeTestCase(
                    "JSON",
                    jsonValues,
                    LeafAirbyteSchemaType.JSONB,
                ),
                MySqlDatatypeTestCase(
                    "ENUM('a', 'b', 'c')",
                    enumValues,
                    LeafAirbyteSchemaType.STRING,
                ),
            )
            .associateBy { it.id }
}

data class MySqlDatatypeTestCase(
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
                "CREATE TABLE IF NOT EXISTS $id " +
                    "(pk INT AUTO_INCREMENT, $fieldName $sqlType, PRIMARY KEY (pk))",
                "TRUNCATE TABLE $id",
            )

    val dml: List<String>
        get() = sqlToAirbyte.keys.map { "INSERT INTO $id ($fieldName) VALUES ($it)" }
}
