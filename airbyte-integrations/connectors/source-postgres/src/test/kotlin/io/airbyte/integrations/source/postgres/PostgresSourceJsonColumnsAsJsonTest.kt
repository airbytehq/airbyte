/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.ArrayAirbyteSchemaType
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.test.fixtures.cleanup.TestAssetResourceNamer
import io.airbyte.cdk.test.fixtures.connector.JdbcTestDbExecutor
import io.airbyte.cdk.test.fixtures.tests.FieldTypeMapperTest
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfigurationFactory
import io.airbyte.integrations.source.postgres.legacy.PostgresTestDatabase
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Timeout

/** json and jsonb columns with json_columns_as_json on. */
class PostgresSourceJsonColumnsAsJsonTest : FieldTypeMapperTest() {

    private val schema = TestAssetResourceNamer().getName()
    override val configSpec =
        PostgresSourceFieldTypeMapperTest.config(testdb.container, listOf(schema)).apply {
            jsonColumnsAsJson = true
        }
    override val executor = JdbcTestDbExecutor(schema, jdbcConfig)
    private val jdbcConfig: JdbcSourceConfiguration
        get() = PostgresSourceConfigurationFactory().make(configSpec)

    override val testCases: List<TestCase> = buildList {
        for (sqlType in listOf("JSON", "JSONB")) {
            add(
                testCase(
                    sqlType,
                    LeafAirbyteSchemaType.JSONB,
                    jsonValues.mapKeys { "${it.key}::$sqlType" },
                ),
            )
            add(
                testCase(
                    "$sqlType[]",
                    ArrayAirbyteSchemaType(LeafAirbyteSchemaType.STRING),
                    mapOf(
                        "array['{\"k\": \"v\"}']::$sqlType[]" to "[\"{\\\"k\\\": \\\"v\\\"}\"]",
                        "null" to "null",
                    ),
                ),
            )
        }
    }

    override val setupDdl: List<String> =
        listOf("CREATE SCHEMA \"$schema\"")
            .plus(
                testCases.map {
                    """
                    CREATE TABLE "$schema"."${it.tableName}"
                    ("id" BIGSERIAL PRIMARY KEY,
                    "${it.columnName}" ${it.sqlType})
                    """
                        .trimIndent()
                },
            )

    private fun testCase(
        sqlType: String,
        type: AirbyteSchemaType,
        values: Map<String, String>,
    ): TestCase = TestCase(schema, sqlType, values, type, "$sqlType AS JSON")

    companion object {
        private lateinit var testdb: PostgresTestDatabase

        // Every shape a json value takes, scalars included.
        private val jsonValues =
            mapOf(
                "'{}'" to "{}",
                "'{\"k\": null}'" to "{\"k\":null}",
                "'{\"k\": \"v\", \"n\": [1, 2.5, true, {\"d\": \"é\"}]}'" to
                    "{\"k\":\"v\",\"n\":[1,2.5,true,{\"d\":\"é\"}]}",
                "'[1, \"a\", {\"b\": null}]'" to "[1,\"a\",{\"b\":null}]",
                "'\"text\"'" to "\"text\"",
                "'42'" to "42",
                "'true'" to "true",
                "'null'" to "null",
                "null" to "null",
            )

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun startTestContainer() {
            testdb = PostgresTestDatabase.`in`(PostgresTestDatabase.BaseImage.POSTGRES_17)
        }
    }
}
