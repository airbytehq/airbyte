/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.db2

import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.integrations.source.AbstractSourceDatatypeIntegrationTest
import io.airbyte.integrations.source.db2.config.Db2SourceConfigurationFactory
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Timeout
import org.testcontainers.containers.Db2Container

class Db2SourceDatatypeIntegrationTest : AbstractSourceDatatypeIntegrationTest() {

    override val configSpec = Db2ContainerFactory.configSpecification(dbContainer)

    override val jdbcConfig: JdbcSourceConfiguration
        get() = Db2SourceConfigurationFactory().make(configSpec)

    companion object {
        lateinit var dbContainer: Db2Container

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun startAndProvisionTestContainer() {
            dbContainer = Db2ContainerFactory.exclusive()
        }
    }

    private val floatValues =
        mapOf(
            "null" to "null",
            "45.67" to "45.67",
            "98.76" to "98.76",
            "0.12" to "0.12",
        )

    private val intValues =
        mapOf(
            "null" to "null",
            "1" to "1",
            "0" to "0",
            "-1" to "-1",
            "2147483647" to "2147483647",
            "-2147483648" to "-2147483648",
        )

    private val smallIntValues =
        mapOf(
            "null" to "null",
            "1" to "1",
            "0" to "0",
            "-1" to "-1",
            "32767" to "32767",
            "-32768" to "-32768",
        )

    private val bigIntValues =
        mapOf(
            "null" to "null",
            "1" to "1",
            "0" to "0",
            "-1" to "-1",
            "9223372036854775807" to "9223372036854775807",
            "-9223372036854775808" to "-9223372036854775808",
        )

    private val decimalValues =
        mapOf(
            "null" to "null",
            "123456789.123456789" to "123456789.123456789",
            "-123456789.123456789" to "-123456789.123456789",
            "0.000000001" to "0.000000001",
            "9999999999.999999999" to "9999999999.999999999",
            "-9999999999.999999999" to "-9999999999.999999999",
        )

    private val realValues =
        mapOf(
            "null" to "null",
            "3.402E+38" to "3.402E+38",
            "-3.402E+38" to "-3.402E+38",
            "1.175E-37" to "1.175E-37",
            "0.0" to "0.0",
        )

    private val doubleValues =
        mapOf(
            "null" to "null",
            "1.7976931348623157E+308" to "1.7976931348623157E+308",
            "-1.7976931348623157E+308" to "-1.7976931348623157E+308",
            "2.2250738585072014E-308" to "2.2250738585072014E-308",
            "0.0" to "0.0",
        )

    private val decfloatValues =
        mapOf(
            "null" to "null",
            "INFINITY" to "null",
            "-INFINITY" to "null",
            "NaN" to "null",
            "9.9999999999999999E+306" to "9.9999999999999999E+306",
            "-9.9999999999999999E+306" to "-9.9999999999999999E+306",
            "1E-50" to "1E-50",
            "0" to "0",
        )

    private val booleanValues =
        mapOf(
            "null" to "null",
            "true" to "true",
            "false" to "false",
        )

    private val charValues =
        mapOf(
            "null" to "null",
            "'a'" to "\"a\"",
            "'Z'" to "\"Z\"",
            "'1'" to "\"1\"",
            "' '" to "\" \"",
        )

    private val varcharValues =
        mapOf(
            "null" to "null",
            "'Hello'" to "\"Hello\"",
            "'12345'" to "\"12345\"",
            "' '" to "\" \"",
            "''" to "\"\"",
        )

    private val clobValues =
        mapOf("null" to "null", "'Large Text Content'" to "\"Large Text Content\"")

    private val graphicValues =
        mapOf(
            "null" to "null",
            "'GraphicVal'" to "\"GraphicVal\"",
            "'こんにちは'" to "\"こんにちは\"",
            "'你好'" to "\"你好\"",
        )

    private val dbclobValues =
        mapOf("null" to "null", "'Large DBCLOB Content'" to "\"Large DBCLOB Content\"")

    private val blobValues =
        mapOf("null" to "null", "CAST(X'48656C6C6F' AS BLOB)" to "\"SGVsbG8=\"")

    private val binary20Values =
        mapOf(
            "null" to "null",
            "CAST(X'0123' AS VARBINARY)" to "\"ASMAAAAAAAAAAAAAAAAAAAAAAAA=\"",
            "CAST(X'0123456789ABCDEF' AS VARBINARY)" to "\"ASNFZ4mrze8AAAAAAAAAAAAAAAA=\"",
        )

    private val varbinaryValues =
        mapOf(
            "null" to "null",
            "CAST(X'0123' AS VARBINARY)" to "\"ASM=\"",
            "CAST(X'0123456789ABCDEF' AS VARBINARY)" to "\"ASNFZ4mrze8=\"",
        )

    private val dateValues =
        mapOf(
            "null" to "null",
            "'1000-01-01'" to "\"1000-01-01\"",
            "'9999-12-31'" to "\"9999-12-31\"",
        )

    private val timeValues =
        mapOf(
            "null" to "null",
            "'00:00:00'" to "\"00:00:00.000000\"",
            "'23:59:59'" to "\"23:59:59.000000\"",
        )

    private val timestampValues =
        mapOf(
            "null" to "null",
            "'1000-01-01 00:00:00'" to "\"1000-01-01T00:00:00.000000\"",
            "'9999-12-31 23:59:59'" to "\"9999-12-31T23:59:59.000000\"",
        )

    private val xmlValues =
        mapOf(
            "null" to "null",
            "'<root><node>value</node></root>'" to "\"<root><node>value</node></root>\""
        )

    override val testCases: List<TestCase> =
        listOf(
            // Numeric types
            db2TestCase("SMALLINT", LeafAirbyteSchemaType.INTEGER, smallIntValues),
            db2TestCase("INTEGER", LeafAirbyteSchemaType.INTEGER, intValues),
            db2TestCase("INT", LeafAirbyteSchemaType.INTEGER, intValues),
            db2TestCase("BIGINT", LeafAirbyteSchemaType.INTEGER, bigIntValues),
            db2TestCase("DECIMAL(20,9)", LeafAirbyteSchemaType.NUMBER, decimalValues),
            db2TestCase("DEC(20,9)", LeafAirbyteSchemaType.NUMBER, decimalValues),
            db2TestCase("NUMERIC(20,9)", LeafAirbyteSchemaType.NUMBER, decimalValues),
            db2TestCase("REAL", LeafAirbyteSchemaType.NUMBER, realValues),
            db2TestCase("FLOAT", LeafAirbyteSchemaType.NUMBER, floatValues),
            db2TestCase("DOUBLE", LeafAirbyteSchemaType.NUMBER, doubleValues),
            db2TestCase("DOUBLE PRECISION", LeafAirbyteSchemaType.NUMBER, doubleValues),
            db2TestCase("DECFLOAT", LeafAirbyteSchemaType.NUMBER, decfloatValues),

            // String types
            db2TestCase("CHAR(10)", LeafAirbyteSchemaType.STRING, charValues.withLength(10)),
            db2TestCase("CHARACTER(10)", LeafAirbyteSchemaType.STRING, charValues.withLength(10)),
            db2TestCase("VARCHAR(100)", LeafAirbyteSchemaType.STRING, varcharValues),
            db2TestCase("CHARACTER VARYING(100)", LeafAirbyteSchemaType.STRING, varcharValues),
            db2TestCase("CHAR VARYING(100)", LeafAirbyteSchemaType.STRING, varcharValues),
            db2TestCase("CLOB(1M)", LeafAirbyteSchemaType.STRING, clobValues),
            db2TestCase("CHARACTER LARGE OBJECT(1M)", LeafAirbyteSchemaType.STRING, clobValues),
            db2TestCase("CHAR LARGE OBJECT(1M)", LeafAirbyteSchemaType.STRING, clobValues),
            db2TestCase("DBCLOB(1M)", LeafAirbyteSchemaType.STRING, dbclobValues),

            // Graphic string types
            db2TestCase("GRAPHIC(10)", LeafAirbyteSchemaType.STRING, graphicValues.withLength(10)),
            db2TestCase("VARGRAPHIC(100)", LeafAirbyteSchemaType.STRING, graphicValues),

            // Binary types
            db2TestCase("BLOB(1M)", LeafAirbyteSchemaType.BINARY, blobValues),
            db2TestCase("BINARY LARGE OBJECT(1M)", LeafAirbyteSchemaType.BINARY, blobValues),
            db2TestCase("BINARY(20)", LeafAirbyteSchemaType.BINARY, binary20Values),
            db2TestCase("VARBINARY(100)", LeafAirbyteSchemaType.BINARY, varbinaryValues),
            db2TestCase("BINARY VARYING(100)", LeafAirbyteSchemaType.BINARY, varbinaryValues),

            // Date/time types
            db2TestCase("DATE", LeafAirbyteSchemaType.DATE, dateValues),
            db2TestCase("TIME", LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE, timeValues),
            db2TestCase(
                "TIMESTAMP",
                LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
                timestampValues
            ),

            // Boolean type
            db2TestCase("BOOLEAN", LeafAirbyteSchemaType.BOOLEAN, booleanValues),

            // Special types
            db2TestCase("XML", LeafAirbyteSchemaType.STRING, xmlValues),
        )

    private fun db2TestCase(
        sqlType: String,
        type: AirbyteSchemaType,
        values: Map<String, String>
    ): TestCase {
        return TestCase(
            sqlType,
            values,
            { tableName: String, columnName: String ->
                listOf(
                    """
                    CREATE TABLE $tableName
                    (id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    $columnName $sqlType)
                """.trimIndent()
                )
            },
            type
        )
    }

    // pads the json string map values to a fixed length
    private fun Map<String, String>.withLength(length: Int): Map<String, String> {
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
