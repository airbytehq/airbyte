/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

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

/**
 * Tests SQL generation for sampling queries (FromSample) and basic SELECT queries, without date
 * bound configuration.
 */
class SnowflakeSamplingQueryTest : SnowflakeOperationsBaseTest() {

    @Test
    fun testSamplingQueryWithoutWhereClause() {
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

        val query = queryGenerator.generate(querySpec)
        assertEquals(
            """SELECT "id", "name" FROM (SELECT * FROM (SELECT * FROM "public"."users" SAMPLE (0.39062500)  ORDER BY RANDOM()) LIMIT 1024)""",
            query.sql,
        )
    }

    @Test
    fun testSamplingQueryWithWhereClause() {
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

        val query = queryGenerator.generate(querySpec)
        assertEquals(
            """SELECT "id", "name", "updated_at" FROM (SELECT * FROM (SELECT * FROM "sales"."orders" SAMPLE (0.0015258789062500) WHERE "updated_at" > ? ORDER BY RANDOM()) LIMIT 1024)""",
            query.sql,
        )
        assertEquals(1, query.bindings.size)
    }

    @Test
    fun testSamplingQueryWithComplexWhereClause() {
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

        val query = queryGenerator.generate(querySpec)
        assertEquals(
            """SELECT "id", "status", "created_date" FROM (SELECT * FROM (SELECT * FROM "public"."users" SAMPLE (0.39062500) WHERE ("id" > ?) AND ("status" = ?) AND ("created_date" >= ?) ORDER BY RANDOM()) LIMIT 512)""",
            query.sql,
        )
        assertEquals(3, query.bindings.size)
    }

    @Test
    fun testIncrementalPartitionSamplingQuery() {
        val cursorField = Field("event_date", LocalDateFieldType)
        val idField = Field("row_id", StringFieldType)

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
                select = SelectColumns(cursorField, idField),
                from =
                    FromSample(
                        name = "fact_events",
                        namespace = "analytics",
                        sampleRateInvPow2 = 16,
                        sampleSize = 1024,
                        where = whereClause
                    ),
                where = whereClause,
                orderBy = OrderBy(idField)
            )

        val query = queryGenerator.generate(querySpec)
        assertEquals(
            """SELECT "event_date", "row_id" FROM (SELECT * FROM (SELECT * FROM "analytics"."fact_events" SAMPLE (0.0015258789062500) WHERE ("event_date" > ?) AND ("event_date" <= ?) ORDER BY RANDOM()) LIMIT 1024) WHERE ("event_date" > ?) AND ("event_date" <= ?) ORDER BY "row_id"""",
            query.sql,
        )
        assertEquals(4, query.bindings.size)
    }

    @Test
    fun testSamplingWithNoSampleRate() {
        val whereClause = Where(Greater(Field("id", IntFieldType), Jsons.numberNode(100)))

        val querySpec =
            SelectQuerySpec(
                select = SelectColumns(Field("id", IntFieldType)),
                from =
                    FromSample(
                        name = "test_table",
                        namespace = "test_schema",
                        sampleRateInvPow2 = 0,
                        sampleSize = 1024,
                        where = whereClause
                    )
            )

        val query = queryGenerator.generate(querySpec)
        assertEquals(
            """SELECT "id" FROM (SELECT * FROM (SELECT * FROM "test_schema"."test_table" WHERE "id" > ? ORDER BY RANDOM()) LIMIT 1024)""",
            query.sql,
        )
    }

    @Test
    fun testSamplingQueryWithNullNamespace() {
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

        val query = queryGenerator.generate(querySpec)
        assertEquals(
            """SELECT "id" FROM (SELECT * FROM (SELECT * FROM "users" SAMPLE (6.2500) WHERE "status" = ? ORDER BY RANDOM()) LIMIT 256)""",
            query.sql,
        )
    }

    @Test
    fun testRegularQueryWithoutSampling() {
        val querySpec =
            SelectQuerySpec(
                select = SelectColumns(Field("id", IntFieldType), Field("name", StringFieldType)),
                from = From(name = "users", namespace = "public"),
                where = Where(Greater(Field("id", IntFieldType), Jsons.numberNode(100))),
                orderBy = OrderBy(Field("id", IntFieldType)),
                limit = Limit(10)
            )

        val query = queryGenerator.generate(querySpec)
        assertEquals(
            """SELECT "id", "name" FROM "public"."users" WHERE "id" > ? ORDER BY "id" LIMIT ?""",
            query.sql,
        )
        assertEquals(2, query.bindings.size)
    }

    @Test
    fun testEmptyBoundsHandling() {
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

        val query = queryGenerator.generate(querySpec)
        assertEquals(
            """SELECT "id", "name" FROM (SELECT * FROM (SELECT * FROM "test"."users" SAMPLE (0.0015258789062500)  ORDER BY RANDOM()) LIMIT 1024) ORDER BY "id"""",
            query.sql,
        )
        assertEquals(
            listOf(Field("id", IntFieldType), Field("name", StringFieldType)),
            query.columns,
        )
    }
}
