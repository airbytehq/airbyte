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
import java.time.LocalDate
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

/**
 * Tests date bound filtering (start_date / end_date) for incremental syncs: cursor detected via
 * ORDER BY or SELECT MAX, date conditions injected into regular and sampling queries.
 */
class SnowflakeIncrementalDateBoundsTest : SnowflakeOperationsBaseTest() {

    @Test
    fun testStartDateAddsGreaterOrEqualToRegularQuery() {
        val cursorField = Field("updated_at", LocalDateFieldType)
        val gen = SnowflakeSourceOperations(configWith(startDate = "2024-01-01"))

        val query =
            gen.generate(
                SelectQuerySpec(
                    select = SelectColumns(Field("id", IntFieldType), cursorField),
                    from = From("orders", "sales"),
                    where = NoWhere,
                    orderBy = OrderBy(cursorField),
                    limit = Limit(100),
                )
            )

        assertEquals(
            """SELECT "id", "updated_at" FROM "sales"."orders" WHERE "updated_at" >= ? ORDER BY "updated_at" LIMIT ?""",
            query.sql,
        )
        assertEquals(2, query.bindings.size)
    }

    @Test
    fun testEndDateAddsLesserOrEqualToRegularQuery() {
        val cursorField = Field("updated_at", LocalDateFieldType)
        val gen = SnowflakeSourceOperations(configWith(endDate = "2024-12-31"))

        val query =
            gen.generate(
                SelectQuerySpec(
                    select = SelectColumns(Field("id", IntFieldType), cursorField),
                    from = From("orders", "sales"),
                    where = NoWhere,
                    orderBy = OrderBy(cursorField),
                    limit = Limit(100),
                )
            )

        assertEquals(
            """SELECT "id", "updated_at" FROM "sales"."orders" WHERE "updated_at" <= ? ORDER BY "updated_at" LIMIT ?""",
            query.sql,
        )
        assertEquals(2, query.bindings.size)
    }

    @Test
    fun testBothDatesAddedToRegularQueryWithExistingCursorBounds() {
        val cursorField = Field("created_at", LocalDateFieldType)
        val gen =
            SnowflakeSourceOperations(configWith(startDate = "2024-01-01", endDate = "2024-12-31"))

        val existingWhere =
            Where(
                And(
                    Greater(cursorField, LocalDateCodec.encode(LocalDate.parse("2024-06-01"))),
                    LesserOrEqual(
                        cursorField,
                        LocalDateCodec.encode(LocalDate.parse("2024-09-01"))
                    ),
                )
            )

        val query =
            gen.generate(
                SelectQuerySpec(
                    select = SelectColumns(cursorField),
                    from = From("events", "public"),
                    where = existingWhere,
                    orderBy = OrderBy(cursorField),
                    limit = Limit(500),
                )
            )

        // Existing cursor bounds (> ?, <= ?) + startDate (>= ?) + endDate (<= ?) + LIMIT (?)
        assertEquals(5, query.bindings.size)
        assert(query.sql.contains(""""created_at" > ?""")) {
            "Expected existing cursor lower bound"
        }
        assert(query.sql.contains(""""created_at" >= ?""")) { "Expected startDate condition" }
        assertEquals(
            2,
            query.sql.split(""""created_at" <= ?""").size - 1,
            "Expected two <= conditions"
        )
    }

    @Test
    fun testBothDatesAddedToSamplingQuery() {
        val cursorField = Field("event_date", LocalDateFieldType)
        val gen =
            SnowflakeSourceOperations(configWith(startDate = "2024-01-01", endDate = "2024-12-31"))

        val innerWhere =
            Where(
                And(
                    Greater(cursorField, LocalDateCodec.encode(LocalDate.parse("2024-03-01"))),
                    LesserOrEqual(
                        cursorField,
                        LocalDateCodec.encode(LocalDate.parse("2024-06-01"))
                    ),
                )
            )

        val query =
            gen.generate(
                SelectQuerySpec(
                    select = SelectColumns(cursorField, Field("row_id", StringFieldType)),
                    from =
                        FromSample(
                            name = "fact_events",
                            namespace = "analytics",
                            sampleRateInvPow2 = 16,
                            sampleSize = 1024,
                            where = innerWhere,
                        ),
                    where = innerWhere,
                    orderBy = OrderBy(cursorField),
                )
            )

        // 2 inner cursor + 2 inner date + 2 outer cursor + 2 outer date = 8
        assertEquals(8, query.bindings.size)
        assertEquals(
            2,
            query.sql.split(""""event_date" >= ?""").size - 1,
            "startDate in both inner and outer WHERE"
        )
        assertEquals(
            4,
            query.sql.split(""""event_date" <= ?""").size - 1,
            "endDate (<=) in cursor bounds + date bounds, inner and outer"
        )
    }

    // ---- guard: full_refresh_temporal_column must not affect incremental queries ----

    /**
     * Configuring full_refresh_temporal_column must have zero effect on incremental queries. The
     * cursor is always detected via ORDER BY or the SELECT MAX cache — the temporal column lookup
     * (step 3 in applyDateBounds) must never be reached for incremental streams.
     *
     * This test would fail if the branch ordering in applyDateBounds were changed so that the
     * temporal column check ran before ORDER BY or the cache.
     */
    @Test
    fun testFullRefreshTemporalColumnDoesNotAffectIncrementalOrderByCursorQuery() {
        val cursorField = Field("updated_at", LocalDateFieldType)
        val gen =
            SnowflakeSourceOperations(
                configWith(
                    startDate = "2024-01-01",
                    endDate = "2024-12-31",
                    fullRefreshTemporalColumn = "updated_at", // same column (realistic config)
                )
            )

        val withTemporalCol =
            gen.generate(
                SelectQuerySpec(
                    select = SelectColumns(Field("id", IntFieldType), cursorField),
                    from = From("orders", "sales"),
                    where = NoWhere,
                    orderBy = OrderBy(cursorField),
                    limit = Limit(100),
                )
            )

        // Must be identical to the same query without fullRefreshTemporalColumn
        val withoutTemporalCol =
            SnowflakeSourceOperations(configWith(startDate = "2024-01-01", endDate = "2024-12-31"))
                .generate(
                    SelectQuerySpec(
                        select = SelectColumns(Field("id", IntFieldType), cursorField),
                        from = From("orders", "sales"),
                        where = NoWhere,
                        orderBy = OrderBy(cursorField),
                        limit = Limit(100),
                    )
                )

        assertEquals(withoutTemporalCol.sql, withTemporalCol.sql)
        assertEquals(withoutTemporalCol.bindings.size, withTemporalCol.bindings.size)
    }

    /**
     * Same guard for PK-ordered incremental reads (cursor cached via SELECT MAX). The cache (step
     * 2) must take priority over the temporal column check (step 3).
     */
    @Test
    fun testFullRefreshTemporalColumnDoesNotAffectIncrementalPkOrderedRead() {
        val cursorField = Field("updated_at", LocalDateFieldType)
        val pkField = Field("id", StringFieldType)
        val gen =
            SnowflakeSourceOperations(
                configWith(
                    startDate = "2024-01-01",
                    endDate = "2024-12-31",
                    fullRefreshTemporalColumn = "updated_at",
                )
            )

        // Populate the cursor cache
        gen.generate(
            SelectQuerySpec(
                select = SelectColumnMaxValue(cursorField),
                from = From("orders", "sales"),
            )
        )

        val withTemporalCol =
            gen.generate(
                SelectQuerySpec(
                    select = SelectColumns(cursorField, pkField),
                    from = From("orders", "sales"),
                    where = NoWhere,
                    orderBy = OrderBy(pkField),
                    limit = Limit(500),
                )
            )

        val genWithout =
            SnowflakeSourceOperations(configWith(startDate = "2024-01-01", endDate = "2024-12-31"))
        genWithout.generate(
            SelectQuerySpec(
                select = SelectColumnMaxValue(cursorField),
                from = From("orders", "sales"),
            )
        )
        val withoutTemporalCol =
            genWithout.generate(
                SelectQuerySpec(
                    select = SelectColumns(cursorField, pkField),
                    from = From("orders", "sales"),
                    where = NoWhere,
                    orderBy = OrderBy(pkField),
                    limit = Limit(500),
                )
            )

        assertEquals(withoutTemporalCol.sql, withTemporalCol.sql)
        assertEquals(withoutTemporalCol.bindings.size, withTemporalCol.bindings.size)
    }

    @Test
    fun testDateBoundsSkippedForFullRefreshQueryWithoutTemporalColumn() {
        val gen =
            SnowflakeSourceOperations(configWith(startDate = "2024-01-01", endDate = "2024-12-31"))

        val query =
            gen.generate(
                SelectQuerySpec(
                    select =
                        SelectColumns(Field("id", IntFieldType), Field("name", StringFieldType)),
                    from = From("users", "public"),
                    where = NoWhere,
                    // No ORDER BY and no fullRefreshTemporalColumn → skip
                    )
            )

        assertEquals("""SELECT "id", "name" FROM "public"."users"""", query.sql)
        assertEquals(0, query.bindings.size)
    }

    @Test
    fun testDateBoundsAppliedToMaxValueQuery() {
        val cursorField = Field("updated_at", LocalDateFieldType)
        val gen =
            SnowflakeSourceOperations(configWith(startDate = "2024-01-01", endDate = "2024-12-31"))

        val query =
            gen.generate(
                SelectQuerySpec(
                    select = SelectColumnMaxValue(cursorField),
                    from = From("orders", "sales"),
                )
            )

        assertEquals(
            """SELECT MAX("updated_at") FROM "sales"."orders" WHERE ("updated_at" >= ?) AND ("updated_at" <= ?)""",
            query.sql,
        )
        assertEquals(2, query.bindings.size)
    }
}
