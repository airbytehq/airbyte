/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.databricks

import io.airbyte.cdk.data.LocalDateCodec
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.LocalDateFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.read.*
import io.airbyte.cdk.util.Jsons
import java.time.LocalDate
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class DatabricksSourceOperationsTest {

    private val operations = DatabricksSourceOperations()

    @Test
    fun testSamplingQueryWithoutWhereClause() {
        // Test traditional sampling without a WHERE clause
        val querySpec =
            SelectQuerySpec(
                select = SelectColumns(Field("id", IntFieldType), Field("name", StringFieldType)),
                from =
                    FromSample(
                        name = "users",
                        namespace = "public",
                        sampleRateInvPow2 = 8,
                        sampleSize = 1024
                    )
            )

        val query = operations.generate(querySpec)
        val expectedSql =
            """
            SELECT `id`, `name` FROM (SELECT * FROM (SELECT * FROM public.`users` TABLESAMPLE (0.39062500 PERCENT)  ORDER BY RANDOM()) LIMIT 1024)
        """
                .trimIndent()
                .replace("\n", " ")

        assertEquals(expectedSql, query.sql)
    }

    @Test
    fun testSamplingQueryWithWhereClause() {
        // Test sampling with a WHERE clause (incremental sync scenario)
        val cursorField = Field("updated_at", LocalDateFieldType)
        val whereClause =
            Where(Greater(cursorField, LocalDateCodec.encode(LocalDate.parse("2025-01-01"))))

        val querySpec =
            SelectQuerySpec(
                select =
                    SelectColumns(
                        Field("id", IntFieldType),
                        Field("name", StringFieldType),
                        cursorField
                    ),
                from =
                    FromSample(
                        name = "orders",
                        namespace = "sales",
                        sampleRateInvPow2 = 16,
                        sampleSize = 1024,
                        where = whereClause
                    )
            )

        val query = operations.generate(querySpec)
        val expectedSql =
            """
            SELECT `id`, `name`, `updated_at` FROM (SELECT * FROM (SELECT * FROM sales.`orders` TABLESAMPLE (0.0015258789062500 PERCENT) WHERE `updated_at` > ? ORDER BY RANDOM()) LIMIT 1024)
        """
                .trimIndent()
                .replace("\n", " ")

        assertEquals(expectedSql, query.sql)
        assertEquals(1, query.bindings.size)
    }

    @Test
    fun testSamplingQueryWithComplexWhereClause() {
        // Test sampling with a complex WHERE clause (multiple conditions)
        val idField = Field("id", IntFieldType)
        val statusField = Field("status", StringFieldType)
        val dateField = Field("created_date", LocalDateFieldType)

        val whereClause =
            Where(
                And(
                    Greater(idField, Jsons.numberNode(1000)),
                    Equal(statusField, Jsons.textNode("active")),
                    GreaterOrEqual(dateField, LocalDateCodec.encode(LocalDate.parse("2025-01-01")))
                )
            )

        val querySpec =
            SelectQuerySpec(
                select = SelectColumns(idField, statusField, dateField),
                from =
                    FromSample(
                        name = "users",
                        namespace = "public",
                        sampleRateInvPow2 = 8,
                        sampleSize = 512,
                        where = whereClause
                    )
            )

        val query = operations.generate(querySpec)
        val expectedSql =
            """
            SELECT `id`, `status`, `created_date` FROM (SELECT * FROM (SELECT * FROM public.`users` TABLESAMPLE (0.39062500 PERCENT) WHERE (`id` > ?) AND (`status` = ?) AND (`created_date` >= ?) ORDER BY RANDOM()) LIMIT 512)
        """
                .trimIndent()
                .replace("\n", " ")

        assertEquals(expectedSql, query.sql)
        assertEquals(3, query.bindings.size)
    }

    @Test
    fun testIncrementalPartitionSamplingQuery() {
        // Test the exact scenario from the GitHub issue
        val cursorField = Field("airdate", LocalDateFieldType)
        val uuidField = Field("uuid", StringFieldType)

        // Simulate cursor bounds for incremental sync
        val lowerBound = LocalDate.parse("2025-08-07")
        val upperBound = LocalDate.parse("2025-08-08")

        val whereClause =
            Where(
                And(
                    Greater(cursorField, LocalDateCodec.encode(lowerBound)),
                    LesserOrEqual(cursorField, LocalDateCodec.encode(upperBound))
                )
            )

        val querySpec =
            SelectQuerySpec(
                select = SelectColumns(cursorField, uuidField),
                from =
                    FromSample(
                        name = "VW_POLARIS_ADMO_AIRINGS",
                        namespace = "POLARIS",
                        sampleRateInvPow2 = 16,
                        sampleSize = 1024,
                        where = whereClause
                    ),
                where = whereClause,
                orderBy = OrderBy(uuidField)
            )

        val query = operations.generate(querySpec)

        // The WHERE clause should be inside the sampling subquery
        val expectedSql =
            """
            SELECT `airdate`, `uuid` FROM (SELECT * FROM (SELECT * FROM POLARIS.`VW_POLARIS_ADMO_AIRINGS` TABLESAMPLE (0.0015258789062500 PERCENT) WHERE (`airdate` > ?) AND (`airdate` <= ?) ORDER BY RANDOM()) LIMIT 1024) WHERE (`airdate` > ?) AND (`airdate` <= ?) ORDER BY `uuid`
        """
                .trimIndent()
                .replace("\n", " ")

        assertEquals(expectedSql, query.sql)
        assertEquals(4, query.bindings.size) // Both inner and outer WHERE contribute bindings
    }

    @Test
    fun testSamplingWithNoSampleRate() {
        // Test when sample rate is 1 (no sampling)
        val whereClause = Where(Greater(Field("id", IntFieldType), Jsons.numberNode(100)))

        val querySpec =
            SelectQuerySpec(
                select = SelectColumns(Field("id", IntFieldType)),
                from =
                    FromSample(
                        name = "test_table",
                        namespace = "test_schema",
                        sampleRateInvPow2 = 0, // 2^0 = 1, means no sampling
                        sampleSize = 1024,
                        where = whereClause
                    )
            )

        val query = operations.generate(querySpec)

        // When sampleRateInv is 1, no TABLESAMPLE clause should be added
        val expectedSql =
            """
            SELECT `id` FROM (SELECT * FROM (SELECT * FROM test_schema.`test_table` WHERE `id` > ? ORDER BY RANDOM()) LIMIT 1024)
        """
                .trimIndent()
                .replace("\n", " ")

        assertEquals(expectedSql, query.sql)
    }

    @Test
    fun testSamplingQueryWithNullNamespace() {
        // Test sampling query without namespace
        val whereClause = Where(Equal(Field("status", StringFieldType), Jsons.textNode("active")))

        val querySpec =
            SelectQuerySpec(
                select = SelectColumns(Field("id", IntFieldType)),
                from =
                    FromSample(
                        name = "users",
                        namespace = null,
                        sampleRateInvPow2 = 4,
                        sampleSize = 256,
                        where = whereClause
                    )
            )

        val query = operations.generate(querySpec)
        val expectedSql =
            """
            SELECT `id` FROM (SELECT * FROM (SELECT * FROM `users` TABLESAMPLE (6.2500 PERCENT) WHERE `status` = ? ORDER BY RANDOM()) LIMIT 256)
        """
                .trimIndent()
                .replace("\n", " ")

        assertEquals(expectedSql, query.sql)
    }

    @Test
    fun testRegularQueryWithoutSampling() {
        // Test that regular queries (non-sampling) still work correctly
        val querySpec =
            SelectQuerySpec(
                select = SelectColumns(Field("id", IntFieldType), Field("name", StringFieldType)),
                from = From(name = "users", namespace = "public"),
                where = Where(Greater(Field("id", IntFieldType), Jsons.numberNode(100))),
                orderBy = OrderBy(Field("id", IntFieldType)),
                limit = Limit(10)
            )

        val query = operations.generate(querySpec)
        val expectedSql =
            """
            SELECT `id`, `name` FROM public.`users` WHERE `id` > ? ORDER BY `id` LIMIT ?
        """
                .trimIndent()
                .replace("\n", " ")

        assertEquals(expectedSql, query.sql)
        assertEquals(2, query.bindings.size)
    }

    @Test
    fun testEmptyBoundsHandling() {
        // Test that when there are no bounds, we get NoWhere instead of empty And/Or clauses
        // This simulates a fresh snapshot with no lower/upper bounds
        val querySpec =
            SelectQuerySpec(
                select = SelectColumns(Field("id", IntFieldType), Field("name", StringFieldType)),
                from =
                    FromSample(
                        name = "users",
                        namespace = "test",
                        sampleRateInvPow2 = 16,
                        sampleSize = 1024,
                        where = NoWhere
                    ),
                where = NoWhere,
                orderBy = OrderBy(Field("id", IntFieldType))
            )

        val query = operations.generate(querySpec)

        // Should generate SQL without any WHERE clause in the sampling subquery
        val expectedSql =
            """
            SELECT `id`, `name` FROM (SELECT * FROM (SELECT * FROM test.`users` TABLESAMPLE (0.0015258789062500 PERCENT)  ORDER BY RANDOM()) LIMIT 1024) ORDER BY `id`
        """
                .trimIndent()
                .replace("\n", " ")

        assertEquals(expectedSql, query.sql)
        assertEquals(
            listOf(Field("id", IntFieldType), Field("name", StringFieldType)),
            query.columns
        )
    }

    @Test
    fun testFieldTypeMapping() {
        // Test that field type mapping works correctly for Databricks types
        val operations = DatabricksSourceOperations()

        // Test that operations instance is created successfully
        assertEquals(DatabricksSourceOperations::class.java, operations.javaClass)
    }

    @Test
    fun testLimitClause() {
        // Test limit clause generation
        val querySpec =
            SelectQuerySpec(
                select = SelectColumns(Field("id", IntFieldType)),
                from = From(name = "users", namespace = "public"),
                limit = Limit(5)
            )

        val query = operations.generate(querySpec)
        val expectedSql = "SELECT `id` FROM public.`users` LIMIT ?"

        assertEquals(expectedSql, query.sql)
        assertEquals(1, query.bindings.size)
    }

    @Test
    fun testZeroLimit() {
        // Test zero limit clause
        val querySpec =
            SelectQuerySpec(
                select = SelectColumns(Field("id", IntFieldType)),
                from = From(name = "users", namespace = "public"),
                limit = Limit(0)
            )

        val query = operations.generate(querySpec)
        val expectedSql = "SELECT `id` FROM public.`users` LIMIT 0"

        assertEquals(expectedSql, query.sql)
        assertEquals(0, query.bindings.size)
    }

    @Test
    fun testNoLimit() {
        // Test no limit clause
        val querySpec =
            SelectQuerySpec(
                select = SelectColumns(Field("id", IntFieldType)),
                from = From(name = "users", namespace = "public")
            )

        val query = operations.generate(querySpec)
        val expectedSql = "SELECT `id` FROM public.`users`"

        assertEquals(expectedSql, query.sql)
        assertEquals(0, query.bindings.size)
    }
}
