/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.test.fixtures.cleanup.TestAssetResourceNamer
import io.airbyte.cdk.test.fixtures.connector.JdbcTestDbExecutor
import io.airbyte.cdk.test.fixtures.tests.CursorBasedSyncTest
import io.airbyte.integrations.source.postgres.config.EncryptionDisable
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfigurationFactory
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfigurationSpecification
import io.airbyte.integrations.source.postgres.config.StandardReplicationMethodConfigurationSpecification
import io.airbyte.integrations.source.postgres.legacy.PostgresTestDatabase
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Timeout
import org.testcontainers.containers.PostgreSQLContainer

class PostgresSourceCursorBasedSyncTest : CursorBasedSyncTest() {

    private val schema = TestAssetResourceNamer().getName()
    override val configSpec = config(testdb.container, listOf(schema))
    override val executor = JdbcTestDbExecutor(schema, jdbcConfig)
    private val jdbcConfig: JdbcSourceConfiguration
        get() = PostgresSourceConfigurationFactory().make(configSpec)

    override val testCases: List<TestCase> = buildList {
        // Numeric types
        add(
            testCase(
                "smallint",
                mapOf("1" to "1"),
                mapOf("2" to "2"),
                mapOf("3" to "3", "4" to "4")
            )
        )
        add(
            testCase(
                "integer",
                mapOf("10" to "10"),
                mapOf("20" to "20"),
                mapOf("30" to "30", "40" to "40")
            )
        )
        add(
            testCase(
                "bigint",
                mapOf("100" to "100"),
                mapOf("200" to "200"),
                mapOf("300" to "300", "400" to "400")
            )
        )
        add(
            testCase(
                "real",
                mapOf("1.5" to "1.5"),
                mapOf("2.5" to "2.5"),
                mapOf("3.5" to "3.5", "4.5" to "4.5")
            )
        )
        add(
            testCase(
                "double precision",
                mapOf("1.5" to "1.5"),
                mapOf("2.5" to "2.5"),
                mapOf("3.5" to "3.5", "4.5" to "4.5")
            )
        )
        add(
            testCase("numeric", mapOf("1" to "1"), mapOf("2" to "2"), mapOf("3" to "3", "4" to "4"))
        )

        // String types
        add(
            testCase(
                "text",
                mapOf("'apple'" to "\"apple\""),
                mapOf("'banana'" to "\"banana\""),
                mapOf("'cherry'" to "\"cherry\"", "'date'" to "\"date\"")
            )
        )
        add(
            testCase(
                "character varying(100)",
                mapOf("'apple'" to "\"apple\""),
                mapOf("'banana'" to "\"banana\""),
                mapOf("'cherry'" to "\"cherry\"", "'date'" to "\"date\"")
            )
        )

        // Date/time types
        add(
            testCase(
                "date",
                mapOf("'2020-01-01'::date" to "\"2020-01-01\""),
                mapOf("'2021-01-01'::date" to "\"2021-01-01\""),
                mapOf(
                    "'2022-01-01'::date" to "\"2022-01-01\"",
                    "'2023-01-01'::date" to "\"2023-01-01\""
                )
            )
        )
        add(
            testCase(
                "time without time zone",
                mapOf("'01:00:00.123456'::time" to "\"01:00:00.123456\""),
                mapOf("'02:00:00.123456'::time" to "\"02:00:00.123456\""),
                mapOf(
                    "'03:00:00.123456'::time" to "\"03:00:00.123456\"",
                    "'04:00:00.123456'::time" to "\"04:00:00.123456\""
                )
            )
        )
        add(
            testCase(
                "time with time zone",
                mapOf("'01:00:00.123456+00'::timetz" to "\"01:00:00.123456Z\""),
                mapOf("'02:00:00.123456+00'::timetz" to "\"02:00:00.123456Z\""),
                mapOf(
                    "'03:00:00.123456+00'::timetz" to "\"03:00:00.123456Z\"",
                    "'04:00:00.123456+00'::timetz" to "\"04:00:00.123456Z\""
                )
            )
        )
        add(
            testCase(
                "timestamp without time zone",
                mapOf("'2020-01-01 00:00:00'::timestamp" to "\"2020-01-01T00:00:00.000000\""),
                mapOf("'2021-01-01 00:00:00'::timestamp" to "\"2021-01-01T00:00:00.000000\""),
                mapOf(
                    "'2022-01-01 00:00:00'::timestamp" to "\"2022-01-01T00:00:00.000000\"",
                    "'2023-01-01 00:00:00'::timestamp" to "\"2023-01-01T00:00:00.000000\""
                )
            )
        )
        add(
            testCase(
                "timestamp with time zone",
                mapOf("'2020-01-01 00:00:00'::timestamptz" to "\"2020-01-01T00:00:00.000000Z\""),
                mapOf("'2021-01-01 00:00:00'::timestamptz" to "\"2021-01-01T00:00:00.000000Z\""),
                mapOf(
                    "'2022-01-01 00:00:00'::timestamptz" to "\"2022-01-01T00:00:00.000000Z\"",
                    "'2023-01-01 00:00:00'::timestamptz" to "\"2023-01-01T00:00:00.000000Z\""
                )
            )
        )
    }

    override val setupDdl: List<String> =
        listOf("CREATE SCHEMA \"$schema\"")
            .plus(
                testCases.map {
                    """
                    CREATE TABLE "$schema"."${it.tableName}"
                    ("id" BIGSERIAL PRIMARY KEY,
                    "$CURSOR_FIELD" ${it.sqlType})
                    """.trimIndent()
                }
            )

    private fun testCase(
        sqlType: String,
        initialRows: Map<String, String>,
        boundaryRows: Map<String, String> = emptyMap(),
        additionalRows: Map<String, String>,
    ): TestCase =
        TestCase(
            namespace = schema,
            sqlType = sqlType,
            cursorField = CURSOR_FIELD,
            initialRows = initialRows,
            boundaryRows = boundaryRows,
            additionalRows = additionalRows,
        )

    companion object {
        private const val CURSOR_FIELD = "cursor_col"

        private lateinit var testdb: PostgresTestDatabase

        protected val serverImage: PostgresTestDatabase.BaseImage
            get() = PostgresTestDatabase.BaseImage.POSTGRES_17

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
            testdb = PostgresTestDatabase.`in`(serverImage)
        }
    }
}
