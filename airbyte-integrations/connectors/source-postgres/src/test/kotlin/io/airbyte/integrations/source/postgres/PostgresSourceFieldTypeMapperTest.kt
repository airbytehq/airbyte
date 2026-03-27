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
import io.airbyte.integrations.source.postgres.config.EncryptionDisable
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfigurationFactory
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfigurationSpecification
import io.airbyte.integrations.source.postgres.config.StandardReplicationMethodConfigurationSpecification
import io.airbyte.integrations.source.postgres.legacy.PostgresTestDatabase
import io.airbyte.integrations.source.postgres.legacy.PostgresTestDatabase.BaseImage
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Timeout
import org.testcontainers.containers.PostgreSQLContainer

class PostgresSourceFieldTypeMapperTest : FieldTypeMapperTest() {

    private val schema = TestAssetResourceNamer().getName()
    override val configSpec = config(testdb.container, listOf(schema))
    override val executor = JdbcTestDbExecutor(schema, jdbcConfig)
    private val jdbcConfig: JdbcSourceConfiguration
        get() = PostgresSourceConfigurationFactory().make(configSpec)

    override val testCases: List<TestCase> = buildList {
        scalarAndArray("BOOLEAN", LeafAirbyteSchemaType.BOOLEAN, AnsiSql.booleanValues)

        // Numeric types
        scalarAndArray("SMALLINT", LeafAirbyteSchemaType.INTEGER, AnsiSql.smallIntValues)
        scalarAndArray("INTEGER", LeafAirbyteSchemaType.INTEGER, AnsiSql.intValues)
        scalarAndArray("INT", LeafAirbyteSchemaType.INTEGER, AnsiSql.intValues)

        add(
            testCase(
                "OID",
                LeafAirbyteSchemaType.INTEGER,
                // unsigned type - nonnegative values only
                mapOf(
                    "null" to "null",
                    "0" to "0",
                    // requires unsigned: bigger than an int can hold
                    "3000000000::oid" to "3000000000"
                ),
                "OID"
            )
        )
        add(
            testCase(
                "OID[]",
                // TODO (https://github.com/airbytehq/airbyte-internal-issues/issues/15946):
                //  Legacy array mapping inconsistent with scalar. Should be ARRAY<INTEGER>.
                ArrayAirbyteSchemaType(LeafAirbyteSchemaType.NUMBER),
                // unsigned type - nonnegative values only
                mapOf(
                        "null" to "null",
                        "0" to "0",
                        // requires unsigned: bigger than an int can hold
                        "3000000000::oid" to "3000000000"
                    )
                    .toArrayVals("OID[]", false),
                "OID ARRAY"
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
        add(
            testCase(
                "DECIMAL(20,0)",
                LeafAirbyteSchemaType.INTEGER,
                AnsiSql.bigIntValues,
                "DECIMAL(20,0)"
            )
        )
        add(
            testCase(
                "DECIMAL(20,0)[]",
                // TODO (https://github.com/airbytehq/airbyte-internal-issues/issues/15879):
                //  Fix type handling for numeric arrays.
                ArrayAirbyteSchemaType(LeafAirbyteSchemaType.NUMBER),
                AnsiSql.bigIntValues.toArrayVals("DECIMAL(20,0)[]"),
                "DECIMAL(20,0) ARRAY"
            )
        )

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
        add(
            testCase(
                "BIT(1)",
                LeafAirbyteSchemaType.STRING,
                mapOf("B'0'" to "\"0\"", "B'1'" to "\"1\""),
                "BIT"
            )
        )
        add(
            testCase(
                "BIT(1)[]",
                // TODO (https://github.com/airbytehq/airbyte-internal-issues/issues/15946):
                //  Legacy array mapping inconsistent with scalar.
                //  Currently: bit(1) -> STRING; _bit(1) -> ARRAY<BOOLEAN>
                ArrayAirbyteSchemaType(LeafAirbyteSchemaType.BOOLEAN),
                mapOf("B'0'" to "false", "B'1'" to "true").toArrayVals("BIT[]", false),
                "BIT(1) ARRAY"
            )
        )
        add(
            testCase(
                "BIT(10)",
                LeafAirbyteSchemaType.STRING,
                mapOf("B'0000000000'" to "\"0000000000\"", "B'1111111111'" to "\"1111111111\""),
                "BIT"
            )
        )
        add(
            testCase(
                "BIT(10)[]",
                // TODO (https://github.com/airbytehq/airbyte-internal-issues/issues/15946):
                //  Legacy array mapping inconsistent with scalar.
                //  Currently: bit(10) -> STRING; _bit(10) -> ARRAY<BOOLEAN>
                ArrayAirbyteSchemaType(LeafAirbyteSchemaType.BOOLEAN),
                // TODO: Legacy mapping only maps "1" to true, all else are false
                mapOf("B'0000000000'" to "false", "B'1111111111'" to "false")
                    .toArrayVals("BIT(10)[]", false),
                "BIT(10) ARRAY"
            )
        )
        add(
            testCase(
                "BIT VARYING",
                LeafAirbyteSchemaType.STRING,
                mapOf("B'0000000000'" to "\"0000000000\"", "B'1111111111'" to "\"1111111111\""),
                "BIT VARYING"
            )
        )
        add(
            testCase(
                "BIT VARYING[]",
                // TODO (https://github.com/airbytehq/airbyte-internal-issues/issues/15946):
                //  Legacy array mapping inconsistent with scalar.
                //  Currently: varbit -> STRING; _varbit -> ARRAY<BOOLEAN>
                ArrayAirbyteSchemaType(LeafAirbyteSchemaType.BOOLEAN),
                // TODO: Legacy mapping only maps "1" to true, all else are false
                mapOf("B'0000000000'" to "false", "B'1111111111'" to "false")
                    .toArrayVals("BIT VARYING[]", false),
                "BIT VARYING ARRAY"
            )
        )

        add(
            testCase(
                "BYTEA",
                LeafAirbyteSchemaType.STRING,
                mapOf("decode('someBase64xx', 'base64')" to "\"\\\\xb2899e05ab1eeb8c71\""),
                "BYTEA",
            )
        )
        add(
            testCase(
                "BYTEA[]",
                ArrayAirbyteSchemaType(LeafAirbyteSchemaType.STRING),
                // TODO (https://github.com/airbytehq/airbyte-internal-issues/issues/15946):
                //  Legacy representation of array values inconsistent with scalar.
                mapOf("decode('someBase64xx', 'base64')" to "\"someBase64xx\"")
                    .toArrayVals("BYTEA[]"),
                "BYTEA ARRAY",
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
                "hstore('addr','123 Main St, Suite 5')" to
                    "\"{\\\"addr\\\":\\\"123 Main St, Suite 5\\\"}\"",
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
            mapOf(
                    "null" to "null",
                    // TODO: inconsistent mapping: We only preserve trailing 0s except on zero value
                    "'00:00:00'" to "\"00:00:00.000000\"",
                    "'23:59:59'" to "\"23:59:59\"",
                )
                .mapKeys { "${it.key}::time" }
        )
        scalarAndArray(
            "TIMETZ",
            LeafAirbyteSchemaType.TIME_WITH_TIMEZONE,
            mapOf(
                    "null" to "null",
                    // TODO: inconsistent mapping: We only preserve trailing 0s on zero value
                    "'00:00:00+00'" to "\"00:00:00.000000Z\"",
                    "'23:59:59+00'" to "\"23:59:59Z\"",
                )
                .mapKeys { "${it.key}::timetz" }
        )
        scalarAndArray(
            "TIMESTAMP",
            LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
            mapOf(
                    "null" to "null",
                    // TODO: inconsistent mapping: We only preserve trailing 0s on zero value
                    "'1000-01-01 00:00:00'" to "\"1000-01-01T00:00:00.000000\"",
                    "'9999-12-31 23:59:59'" to "\"9999-12-31T23:59:59\"",
                )
                .mapKeys { "${it.key}::timestamp" },
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
        private lateinit var testdb: PostgresTestDatabase

        protected val serverImage: BaseImage
            get() = BaseImage.POSTGRES_17

        fun config(
            postgresContainer: PostgreSQLContainer<*>,
            schemas: List<String> = listOf("public"),
        ): PostgresSourceConfigurationSpecification =
            PostgresSourceConfigurationSpecification().apply {
                host = postgresContainer.host
                port = postgresContainer.getMappedPort(PostgreSQLContainer.POSTGRESQL_PORT)
                username = postgresContainer.username
                password = postgresContainer.password
                jdbcUrlParams = ""
                encryptionJson = EncryptionDisable
                database = "test"
                this.schemas = schemas
                checkpointTargetIntervalSeconds = 60
                maxDbConnections = 1
                setIncrementalConfigurationSpecificationValue(
                    StandardReplicationMethodConfigurationSpecification
                )
            }

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun startAndProvisionTestContainer() {
            testdb = PostgresTestDatabase.`in`(this.serverImage)
            val schema = TestAssetResourceNamer().getName()
            val configSpec = config(testdb.container, listOf(schema))
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
