/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.ArrayAirbyteSchemaType
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.test.fixtures.cleanup.TestAssetResourceNamer
import io.airbyte.cdk.test.fixtures.connector.JdbcTestDbExecutor
import io.airbyte.cdk.test.fixtures.tests.AnsiSql
import io.airbyte.cdk.test.fixtures.tests.ExtendedSql
import io.airbyte.cdk.test.fixtures.tests.FieldTypeMapperTest
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfigurationFactory
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Timeout
import org.testcontainers.containers.PostgreSQLContainer

class PostgresSourceFieldTypeMapperTest : FieldTypeMapperTest() {

    private val schema = TestAssetResourceNamer().getName()
    override val configSpec = PostgresContainerFactory.config(container, listOf(schema))
    override val executor = JdbcTestDbExecutor(schema, jdbcConfig)
    private val jdbcConfig: JdbcSourceConfiguration
        get() = PostgresSourceConfigurationFactory().make(configSpec)

    override val testCases: List<TestCase> = buildList {
        scalarAndArray("BOOLEAN", LeafAirbyteSchemaType.BOOLEAN, AnsiSql.booleanValues)

        // Numeric types
        scalarAndArray("SMALLINT", LeafAirbyteSchemaType.INTEGER, AnsiSql.smallIntValues)
        scalarAndArray("INTEGER", LeafAirbyteSchemaType.INTEGER, AnsiSql.intValues)
        scalarAndArray("INT", LeafAirbyteSchemaType.INTEGER, AnsiSql.intValues)
        scalarAndArray(
            "OID",
            LeafAirbyteSchemaType.INTEGER,
            // unsigned type - nonnegative values only
            mapOf(
                "0" to "0",
                "3000000000::oid" to "3000000000" // requires unsigned: bigger than an int can hold
            )
        )
        scalarAndArray("BIGINT", LeafAirbyteSchemaType.INTEGER, AnsiSql.bigIntValues)
        scalarAndArray(
            "DECIMAL",
            LeafAirbyteSchemaType.NUMBER,
            AnsiSql.decimalValues,
            baseTestName = "DECIMAL SUPPORTED VALS"
        )
        scalarAndArray(
            "DECIMAL",
            LeafAirbyteSchemaType.NUMBER,
            nulledInfinities.plus(nulledNaN),
            arrayIsNulled = true,
            baseTestName = "DECIMAL UNSUPPORTED VALS"
        )
        scalarAndArray("DECIMAL(20,0)", LeafAirbyteSchemaType.INTEGER, AnsiSql.intValues)
        scalarAndArray("DECIMAL(20,9)", LeafAirbyteSchemaType.NUMBER, AnsiSql.decimalValues)
        scalarAndArray("NUMERIC(20,9)", LeafAirbyteSchemaType.NUMBER, AnsiSql.decimalValues)
        scalarAndArray(
            "REAL",
            LeafAirbyteSchemaType.NUMBER,
            AnsiSql.realValues.plus(preservedInfinities).plus(preservedNaN),
        )
        scalarAndArray(
            "DOUBLE PRECISION",
            LeafAirbyteSchemaType.NUMBER,
            AnsiSql.doubleValues.plus(preservedInfinities).plus(preservedNaN)
        )

        // Character types
        scalarAndArray("TEXT", LeafAirbyteSchemaType.STRING, AnsiSql.charValues)
        // In Postgres, "CHAR(N)" is an alias for BPCHAR(N). Our tests use canonical names only.
        scalarAndArray(
            "BPCHAR(10)",
            LeafAirbyteSchemaType.STRING,
            AnsiSql.charValues.withLength(10)
        )
        scalarAndArray(
            "CHARACTER(10)",
            LeafAirbyteSchemaType.STRING,
            AnsiSql.charValues.withLength(10)
        )
        scalarAndArray("VARCHAR(100)", LeafAirbyteSchemaType.STRING, AnsiSql.varcharValues)

        // Binary types
        // CHAR is a distinct type from CHAR(N). It contains a single byte without encoding.
        scalarAndArray(
            "CHAR",
            LeafAirbyteSchemaType.STRING,
            mapOf(
                "'A'" to "\"A\"",
            )
        )
        scalarAndArray(
            "BIT(1)",
            LeafAirbyteSchemaType.BOOLEAN,
            mapOf("B'0'" to "false", "B'1'" to "true")
        )
        scalarAndArray(
            "BIT(10)",
            LeafAirbyteSchemaType.STRING,
            mapOf(
                "B'0000000000'" to "\"0000000000\"",
                "B'1111111111'" to "\"1111111111\"",
            )
        )
        scalarAndArray(
            "BIT VARYING",
            LeafAirbyteSchemaType.STRING,
            mapOf(
                "B'00000'" to "\"00000\"",
                "B'11111'" to "\"11111\"",
            )
        )
        scalarAndArray(
            "BYTEA",
            LeafAirbyteSchemaType.BINARY,
            mapOf(
                "decode('someBase64xx', 'base64')" to "\"someBase64xx\"",
            )
        )

        // Semi-structured types
        scalarAndArray(
            "JSON",
            LeafAirbyteSchemaType.STRING,
            ExtendedSql.jsonValues.mapKeys { "${it.key}::json" }
        )
        scalarAndArray(
            "JSONB",
            LeafAirbyteSchemaType.STRING,
            ExtendedSql.jsonValues.mapKeys { "${it.key}::jsonb" }
        )
        scalarAndArray(
            "XML",
            LeafAirbyteSchemaType.STRING,
            ExtendedSql.xmlValues.mapKeys { "${it.key}::xml" }
        )
        scalarAndArray(
            "HSTORE",
            LeafAirbyteSchemaType.STRING,
            mapOf(
                "null" to "null",
                "hstore('color','red')" to "\"{\\\"color\\\":\\\"red\\\"}\"",
                // Requires ObjectMapper with SerializationFeature.WRITE_NULL_MAP_VALUES
                "hstore('size', NULL)" to "\"{\\\"size\\\":null}\""
            )
        )

        // Date/time types
        scalarAndArray(
            "DATE",
            LeafAirbyteSchemaType.DATE,
            AnsiSql.dateValues.mapKeys { "${it.key}::date" },
            baseTestName = "DATE SUPPORTED VALS"
        )
        scalarAndArray(
            "DATE",
            LeafAirbyteSchemaType.DATE,
            nulledInfinities.mapKeys { "${it.key}::date" },
            baseTestName = "DATE UNSUPPORTED VALS",
            arrayIsNulled = true
        )
        scalarAndArray(
            "TIME",
            LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE,
            AnsiSql.timeValues.mapKeys { "${it.key}::time" }
        )
        scalarAndArray(
            "TIMESTAMP",
            LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
            AnsiSql.timestampValues.mapKeys { "${it.key}::timestamp" },
            baseTestName = "TIMESTAMP SUPPORTED VALS",
        )
        scalarAndArray(
            "TIMESTAMP",
            LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
            nulledInfinities.mapKeys { "${it.key}::timestamp" },
            baseTestName = "TIMESTAMP UNSUPPORTED VALS",
            arrayIsNulled = true
        )
        scalarAndArray(
            "TIMESTAMP WITH TIME ZONE",
            LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE,
            AnsiSql.timestampWithTzValues.mapKeys { "${it.key}::timestamptz" },
            baseTestName = "TIMESTAMP WITH TIME ZONE SUPPORTED VALS",
        )
        scalarAndArray(
            "TIMESTAMP WITH TIME ZONE",
            LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE,
            nulledInfinities.mapKeys { "${it.key}::timestamptz" },
            baseTestName = "TIMESTAMP WITH TIME ZONE UNSUPPORTED VALS",
            arrayIsNulled = true
        )

        // Geometric types
        scalarAndArray(
            "CIRCLE",
            LeafAirbyteSchemaType.STRING,
            mapOf("'<(1.5,2.5),3.0>'::circle" to "\"<(1.5,2.5),3.0>\"")
        )
        scalarAndArray(
            "BOX",
            LeafAirbyteSchemaType.STRING,
            mapOf("'((0.0,0.0),(2.0,2.0))'::box" to "\"(2.0,2.0),(0.0,0.0)\"")
        )
        scalarAndArray(
            "LINE",
            LeafAirbyteSchemaType.STRING,
            mapOf("'{0.0,1.0,2.0}'::line" to "\"{0.0,1.0,2.0}\"")
        )
        scalarAndArray(
            "LSEG",
            LeafAirbyteSchemaType.STRING,
            mapOf("'[(0.0,0.0),(1.0,1.0)]'::lseg" to "\"[(0.0,0.0),(1.0,1.0)]\"")
        )
        scalarAndArray(
            "PATH",
            LeafAirbyteSchemaType.STRING,
            mapOf(
                "'[(0.0,0.0),(1.0,0.0),(1.0,1.0)]'::path" to "\"[(0.0,0.0),(1.0,0.0),(1.0,1.0)]\""
            )
        )
        scalarAndArray(
            "POINT",
            LeafAirbyteSchemaType.STRING,
            mapOf("'(1.0,2.0)'::point" to "\"(1.0,2.0)\"")
        )
        scalarAndArray(
            "POLYGON",
            LeafAirbyteSchemaType.STRING,
            mapOf(
                "'((0.0,0.0),(1.0,0.0),(1.0,1.0))'::polygon" to
                    "\"((0.0,0.0),(1.0,0.0),(1.0,1.0))\""
            )
        )
    }

    companion object {
        lateinit var container: PostgreSQLContainer<*>

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun startAndProvisionTestContainer() {
            container = PostgresContainerFactory.shared17()
            val schema = TestAssetResourceNamer().getName()
            val configSpec = PostgresContainerFactory.config(container, listOf(schema))
            val jdbcConfig = PostgresSourceConfigurationFactory().make(configSpec)
            val executor = JdbcTestDbExecutor(schema, jdbcConfig)
            executor.executeUpdate("CREATE EXTENSION IF NOT EXISTS hstore;")
        }
        private val preservedInfinities =
            mapOf(
                "'Infinity'" to "\"Infinity\"",
                "'-Infinity'" to "\"-Infinity\"",
            )
        private val nulledInfinities =
            mapOf(
                "'Infinity'" to "null",
                "'-Infinity'" to "null",
            )
        private val preservedNaN = mapOf("'NaN'" to "\"NaN\"")
        private val nulledNaN = mapOf("'NaN'" to "null")
    }

    override val setupDdl: List<String> =
        listOf("CREATE SCHEMA \"$schema\"")
            .plus(
                testCases.map {
                    """
                    CREATE TABLE "$schema"."${it.tableName}"
                    ("id" BIGSERIAL PRIMARY KEY,
                    "${it.columnName}" ${it.sqlType})
                    """.trimIndent()
                }
            )

    private fun testCase(
        sqlType: String,
        type: AirbyteSchemaType,
        values: Map<String, String>,
        testName: String
    ): TestCase {
        return TestCase(schema, sqlType, values, type, testName)
    }

    private fun MutableList<TestCase>.scalarAndArray(
        sqlType: String,
        type: AirbyteSchemaType,
        values: Map<String, String>,
        arrayIsNulled: Boolean = false,
        baseTestName: String = sqlType,
    ) {
        val valsWithNull = values.plus("null" to "null")
        add(testCase(sqlType, type, valsWithNull, baseTestName))
        val arrayType = "$sqlType[]"
        add(
            testCase(
                arrayType,
                ArrayAirbyteSchemaType(type),
                valsWithNull.toArrayVals(arrayType, arrayIsNulled),
                "$baseTestName ARRAY"
            )
        )
    }

    // We created maps of inserted values to expected values to be used in tests of scalar types.
    // Here we flatten one of these for use in an array test, e.g.:
    //   input:  {"'1'" to "\"1\"", "'A'" to "\"A\""}
    //   output: {"['1', 'A']" to "[\"1\", \"A\"]"}
    private fun Map<String, String>.toArrayVals(
        sqlType: String,
        nullResult: Boolean = false
    ): Map<String, String> {
        return mapOf(
            this.keys.joinToString(", ", "array[", "]::$sqlType") { it } to
                // When an array field contains an unsupported value, the entire field is set to
                // null
                if (nullResult) {
                    "null"
                } else {
                    this.values.joinToString(",", "[", "]") { it }
                }
        )
    }
}
