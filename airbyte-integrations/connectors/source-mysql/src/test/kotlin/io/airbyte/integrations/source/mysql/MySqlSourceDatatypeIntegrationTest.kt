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

class MySqlSourceDatatypeIntegrationTest {

    @TestFactory
    @Timeout(300)
    fun syncTests(): Iterable<DynamicNode> =
        DynamicDatatypeTestFactory(MySqlSourceDatatypeTestOperations).build(dbContainer)

    companion object {

        lateinit var dbContainer: MySQLContainer<*>

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun startAndProvisionTestContainer() {
            dbContainer = MySqlContainerFactory.shared("mysql:8.0", MySqlContainerFactory.WithCdc)
        }
    }
}

object MySqlSourceDatatypeTestOperations :
    DatatypeTestOperations<
        MySQLContainer<*>,
        MySqlSourceConfigurationSpecification,
        MySqlSourceConfiguration,
        MySqlSourceConfigurationFactory,
        MySqlSourceDatatypeTestCase
    > {

    private val log = KotlinLogging.logger {}

    override val withGlobal: Boolean = true
    override val globalCursorMetaField: MetaField = MySqlSourceCdcMetaFields.CDC_CURSOR

    override fun streamConfigSpec(
        container: MySQLContainer<*>
    ): MySqlSourceConfigurationSpecification =
        MySqlContainerFactory.config(container).also { it.setIncrementalValue(UserDefinedCursor) }

    override fun globalConfigSpec(
        container: MySQLContainer<*>
    ): MySqlSourceConfigurationSpecification =
        MySqlContainerFactory.config(container).also { it.setIncrementalValue(Cdc()) }

    override val configFactory: MySqlSourceConfigurationFactory = MySqlSourceConfigurationFactory()

    override fun createStreams(config: MySqlSourceConfiguration) {
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

    override fun populateStreams(config: MySqlSourceConfiguration) {
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

    val longBitValues =
        mapOf(
            "b'10101010'" to """-86""",
        )

    val longBitCdcValues =
        mapOf(
            "b'10101010'" to """"qg=="""",
        )

    val stringValues =
        mapOf(
            "'abcdef'" to """"abcdef"""",
            "'ABCD'" to """"ABCD"""",
            "'OXBEEF'" to """"OXBEEF"""",
        )

    val jsonValues = mapOf("""'{"col1": "v1"}'""" to """"{\"col1\": \"v1\"}"""")

    val jsonCdcValues = mapOf("""'{"col1": "v1"}'""" to """"{\"col1\":\"v1\"}"""")

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

    val floatValues =
        mapOf(
            "123.4567" to """123.4567""",
        )

    val zeroPrecisionDecimalValues =
        mapOf(
            "2" to """2""",
        )

    val zeroPrecisionDecimalCdcValues =
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
            "'2024-09-13T14:40:00+00:00'" to """"2024-09-13T14:40:00.000000""""
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

    override val testCases: Map<String, MySqlSourceDatatypeTestCase> =
        listOf(
                MySqlSourceDatatypeTestCase(
                    "BOOLEAN",
                    booleanValues,
                    LeafAirbyteSchemaType.BOOLEAN,
                ),
                MySqlSourceDatatypeTestCase(
                    "VARCHAR(10)",
                    stringValues,
                    LeafAirbyteSchemaType.STRING,
                ),
                MySqlSourceDatatypeTestCase(
                    "DECIMAL(10,2)",
                    decimalValues,
                    LeafAirbyteSchemaType.NUMBER,
                ),
                MySqlSourceDatatypeTestCase(
                    "DECIMAL(10,2) UNSIGNED",
                    decimalValues,
                    LeafAirbyteSchemaType.NUMBER,
                ),
                MySqlSourceDatatypeTestCase(
                    "DECIMAL UNSIGNED",
                    zeroPrecisionDecimalValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlSourceDatatypeTestCase("FLOAT", floatValues, LeafAirbyteSchemaType.NUMBER),
                MySqlSourceDatatypeTestCase(
                    "FLOAT(34)",
                    floatValues,
                    LeafAirbyteSchemaType.NUMBER,
                ),
                MySqlSourceDatatypeTestCase(
                    "FLOAT(7,4)",
                    floatValues,
                    LeafAirbyteSchemaType.NUMBER,
                ),
                MySqlSourceDatatypeTestCase(
                    "FLOAT(53,8)",
                    floatValues,
                    LeafAirbyteSchemaType.NUMBER,
                ),
                MySqlSourceDatatypeTestCase("DOUBLE", decimalValues, LeafAirbyteSchemaType.NUMBER),
                MySqlSourceDatatypeTestCase(
                    "DOUBLE UNSIGNED",
                    decimalValues,
                    LeafAirbyteSchemaType.NUMBER,
                ),
                MySqlSourceDatatypeTestCase(
                    "TINYINT",
                    tinyintValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlSourceDatatypeTestCase(
                    "TINYINT UNSIGNED",
                    tinyintValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlSourceDatatypeTestCase(
                    "SMALLINT",
                    tinyintValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlSourceDatatypeTestCase(
                    "MEDIUMINT",
                    tinyintValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlSourceDatatypeTestCase("BIGINT", intValues, LeafAirbyteSchemaType.INTEGER),
                MySqlSourceDatatypeTestCase(
                    "SMALLINT UNSIGNED",
                    tinyintValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlSourceDatatypeTestCase(
                    "MEDIUMINT UNSIGNED",
                    tinyintValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlSourceDatatypeTestCase(
                    "BIGINT UNSIGNED",
                    intValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlSourceDatatypeTestCase("INT", intValues, LeafAirbyteSchemaType.INTEGER),
                MySqlSourceDatatypeTestCase(
                    "INT UNSIGNED",
                    intValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlSourceDatatypeTestCase("DATE", dateValues, LeafAirbyteSchemaType.DATE),
                MySqlSourceDatatypeTestCase(
                    "TIMESTAMP",
                    timestampValues,
                    LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE,
                ),
                MySqlSourceDatatypeTestCase(
                    "DATETIME",
                    dateTimeValues,
                    LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
                ),
                MySqlSourceDatatypeTestCase(
                    "TIME",
                    timeValues,
                    LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE,
                ),
                MySqlSourceDatatypeTestCase("YEAR", yearValues, LeafAirbyteSchemaType.INTEGER),
                MySqlSourceDatatypeTestCase(
                    "VARBINARY(255)",
                    binaryValues,
                    LeafAirbyteSchemaType.BINARY,
                ),
                MySqlSourceDatatypeTestCase(
                    "BIT",
                    bitValues,
                    LeafAirbyteSchemaType.BOOLEAN,
                ),
                MySqlSourceDatatypeTestCase(
                    "BIT(8)",
                    longBitValues,
                    LeafAirbyteSchemaType.INTEGER,
                    isGlobal = false,
                ),
                MySqlSourceDatatypeTestCase(
                    "BIT(8)",
                    longBitCdcValues,
                    LeafAirbyteSchemaType.INTEGER,
                    isStream = false,
                ),
                MySqlSourceDatatypeTestCase(
                    "JSON",
                    jsonValues,
                    LeafAirbyteSchemaType.STRING,
                    isGlobal = false,
                ),
                MySqlSourceDatatypeTestCase(
                    "JSON",
                    jsonCdcValues,
                    LeafAirbyteSchemaType.STRING,
                    isStream = false,
                ),
                MySqlSourceDatatypeTestCase(
                    "ENUM('a', 'b', 'c')",
                    enumValues,
                    LeafAirbyteSchemaType.STRING,
                ),
            )
            .associateBy { it.id }
}

data class MySqlSourceDatatypeTestCase(
    val sqlType: String,
    val sqlToAirbyte: Map<String, String>,
    override val expectedAirbyteSchemaType: AirbyteSchemaType,
    override val isGlobal: Boolean = true,
    override val isStream: Boolean = true,
) : DatatypeTestCase {

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
