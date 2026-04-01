/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.LocalDateFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.read.*
import io.airbyte.cdk.util.Jsons
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

/**
 * Tests the per-table cursor cache used for splittable (PK-ordered) partitions in incremental mode.
 *
 * When a table has a primary key, the CDK orders reads by PK columns, not by the cursor. The
 * SELECT MAX(cursor) query populates the cache so that subsequent read queries — which only carry
 * ORDER BY PK — can still apply date bounds on the correct cursor column.
 */
class SnowflakePkCursorCacheTest : SnowflakeOperationsBaseTest() {

    @Test
    fun testDateBoundsUsesCachedCursorNotPkWhenOrderByIsPk() {
        val cursorField = Field("event_date", LocalDateFieldType)
        val pkField1 = Field("order_id", StringFieldType)
        val pkField2 = Field("line_id", StringFieldType)
        val gen = SnowflakeSourceOperations(configWith(startDate = "2026-01-01", endDate = "2026-02-02"))

        // Step 1: MAX query caches the cursor for this table
        gen.generate(
            SelectQuerySpec(
                select = SelectColumnMaxValue(cursorField),
                from = From("fact_events", "analytics"),
            )
        )

        // Step 2: Splittable read — ORDER BY is PK, not cursor
        val pkBounds =
            Where(
                And(
                    Greater(pkField1, Jsons.textNode("A000")),
                    LesserOrEqual(pkField1, Jsons.textNode("Z999")),
                )
            )
        val query =
            gen.generate(
                SelectQuerySpec(
                    select = SelectColumns(cursorField, pkField1, pkField2),
                    from = From("fact_events", "analytics"),
                    where = pkBounds,
                    orderBy = OrderBy(pkField1, pkField2),
                    limit = Limit(1000),
                )
            )

        assert(query.sql.contains(""""order_id" > ?""")) { "PK lower bound must be present" }
        assert(query.sql.contains(""""order_id" <= ?""")) { "PK upper bound must be present" }
        assert(query.sql.contains(""""event_date" >= ?""")) { "startDate must be on cursor" }
        assert(query.sql.contains(""""event_date" <= ?""")) { "endDate must be on cursor" }
        assert(!query.sql.contains(""""order_id" >= ?""")) { "Date bounds must NOT be on PK" }
        assert(query.sql.contains("""ORDER BY "order_id", "line_id"""")) { "ORDER BY must be on PK" }
    }

    @Test
    fun testDateBoundsUsesCachedCursorForUnsplittableSnapshot() {
        val cursorField = Field("event_date", LocalDateFieldType)
        val gen = SnowflakeSourceOperations(configWith(startDate = "2026-01-01", endDate = "2026-02-02"))

        // MAX query caches the cursor
        gen.generate(
            SelectQuerySpec(
                select = SelectColumnMaxValue(cursorField),
                from = From("fact_events", "analytics"),
            )
        )

        // Unsplittable snapshot — no ORDER BY, no WHERE
        val query =
            gen.generate(
                SelectQuerySpec(
                    select = SelectColumns(cursorField, Field("user_id", IntFieldType)),
                    from = From("fact_events", "analytics"),
                )
            )

        assertEquals(
            """SELECT "event_date", "user_id" FROM "analytics"."fact_events" WHERE ("event_date" >= ?) AND ("event_date" <= ?)""",
            query.sql,
        )
        assertEquals(2, query.bindings.size)
    }

    /**
     * Cas 8: ORDER BY PK, cache empty, no fullRefreshTemporalColumn, dates set.
     * The ORDER BY fallback (step 4) fires and picks the first PK column as cursor.
     * This documents the edge-case behavior — in normal operation SELECT MAX always
     * runs first and populates the cache before any PK-ordered read.
     */
    @Test
    fun testOrderByPkWithEmptyCacheAndNoDatesAppliesBoundsOnPkColumn() {
        val pkField = Field("id", StringFieldType)
        val dataField = Field("name", StringFieldType)
        val gen = SnowflakeSourceOperations(configWith(startDate = "2024-01-01", endDate = "2024-12-31"))

        // No SELECT MAX → cache is empty
        val query =
            gen.generate(
                SelectQuerySpec(
                    select = SelectColumns(pkField, dataField),
                    from = From("users", "public"),
                    where = NoWhere,
                    orderBy = OrderBy(pkField),
                    limit = Limit(100),
                )
            )

        // Fallback behavior: ORDER BY first column (PK) is used as cursor
        assertEquals(
            """SELECT "id", "name" FROM "public"."users" WHERE ("id" >= ?) AND ("id" <= ?) ORDER BY "id" LIMIT ?""",
            query.sql,
        )
        assertEquals(3, query.bindings.size)
    }

    @Test
    fun testNoDatesNoFilteringWithPk() {
        val cursorField = Field("event_date", LocalDateFieldType)
        val pkField = Field("order_id", StringFieldType)
        val gen = SnowflakeSourceOperations(configWith()) // no dates

        gen.generate(
            SelectQuerySpec(
                select = SelectColumnMaxValue(cursorField),
                from = From("fact_events", "analytics"),
            )
        )

        val query =
            gen.generate(
                SelectQuerySpec(
                    select = SelectColumns(cursorField, pkField),
                    from = From("fact_events", "analytics"),
                    orderBy = OrderBy(pkField),
                    limit = Limit(100),
                )
            )

        assertEquals(
            """SELECT "event_date", "order_id" FROM "analytics"."fact_events" ORDER BY "order_id" LIMIT ?""",
            query.sql,
        )
    }

    @Test
    fun testSamplingQueryWithPkOrderByUsesCachedCursorForDateBounds() {
        val cursorField = Field("event_date", LocalDateFieldType)
        val pkField1 = Field("order_id", StringFieldType)
        val pkField2 = Field("line_id", StringFieldType)
        val gen = SnowflakeSourceOperations(configWith(startDate = "2026-01-01", endDate = "2026-02-02"))

        gen.generate(
            SelectQuerySpec(
                select = SelectColumnMaxValue(cursorField),
                from = From("fact_events", "analytics"),
            )
        )

        val pkPartitionWhere = Where(LesserOrEqual(pkField1, Jsons.textNode("Z999")))
        val query =
            gen.generate(
                SelectQuerySpec(
                    select = SelectColumns(cursorField, pkField1, pkField2),
                    from =
                        FromSample(
                            name = "fact_events",
                            namespace = "analytics",
                            sampleRateInvPow2 = 16,
                            sampleSize = 1024,
                            where = pkPartitionWhere,
                        ),
                    where = NoWhere,
                    orderBy = OrderBy(pkField1, pkField2),
                )
            )

        assert(query.sql.contains(""""order_id" <= ?""")) { "PK upper bound must be in sample" }
        assert(query.sql.contains(""""event_date" >= ?""")) { "startDate must be on cursor in sample" }
        assert(query.sql.contains(""""event_date" <= ?""")) { "endDate must be on cursor in sample" }
        assert(!query.sql.contains(""""order_id" >= ?""")) { "Date bounds must NOT be on PK" }
    }
}
