/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import io.airbyte.cdk.data.LocalDateCodec
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.LocalDateFieldType
import io.airbyte.cdk.jdbc.NullFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.read.*
import io.airbyte.cdk.util.Jsons
import java.time.LocalDate
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

/**
 * Tests date bound filtering for full-refresh syncs via the `full_refresh_temporal_column` config.
 *
 * Key behaviours verified:
 * - Temporal column found in SELECT → WHERE clause injected on that column
 * - Temporal column not in SELECT → no filtering (skip gracefully)
 * - NullFieldType during LIMIT 0 discovery → skip (guarded by LosslessJdbcFieldType check)
 * - PK MAX query (full-refresh splitting) → NOT cached, no date bounds on PK
 * - After PK MAX, read query → date bounds on temporal column, NOT on PK
 * - Mixed catalog (incremental + full-refresh same table) → no cache interference
 * - FromSample in full-refresh → bounds injected in both inner sample and outer WHERE
 */
class SnowflakeFullRefreshDateBoundsTest : SnowflakeOperationsBaseTest() {

    @Test
    fun testTemporalColumnInSelectAppliesDateBounds() {
        val eventDateField = Field("event_date", LocalDateFieldType)
        val gen =
            SnowflakeSourceOperations(
                configWith(startDate = "2024-01-01", endDate = "2024-12-31", fullRefreshTemporalColumn = "event_date")
            )

        val query =
            gen.generate(
                SelectQuerySpec(
                    select = SelectColumns(eventDateField, Field("id", IntFieldType)),
                    from = From("events", "public"),
                    where = NoWhere,
                    // No ORDER BY → full-refresh
                )
            )

        assertEquals(
            """SELECT "event_date", "id" FROM "public"."events" WHERE ("event_date" >= ?) AND ("event_date" <= ?)""",
            query.sql,
        )
        assertEquals(2, query.bindings.size)
    }

    // cas 14 & 15: only startDate / only endDate

    @Test
    fun testOnlyStartDateAppliedInFullRefreshMode() {
        val dateField = Field("event_date", LocalDateFieldType)
        val gen =
            SnowflakeSourceOperations(
                configWith(startDate = "2024-01-01", fullRefreshTemporalColumn = "event_date")
            )

        val query =
            gen.generate(
                SelectQuerySpec(
                    select = SelectColumns(dateField, Field("id", IntFieldType)),
                    from = From("events", "public"),
                    where = NoWhere,
                )
            )

        assertEquals(
            """SELECT "event_date", "id" FROM "public"."events" WHERE "event_date" >= ?""",
            query.sql,
        )
        assertEquals(1, query.bindings.size)
    }

    @Test
    fun testOnlyEndDateAppliedInFullRefreshMode() {
        val dateField = Field("event_date", LocalDateFieldType)
        val gen =
            SnowflakeSourceOperations(
                configWith(endDate = "2024-12-31", fullRefreshTemporalColumn = "event_date")
            )

        val query =
            gen.generate(
                SelectQuerySpec(
                    select = SelectColumns(dateField, Field("id", IntFieldType)),
                    from = From("events", "public"),
                    where = NoWhere,
                )
            )

        assertEquals(
            """SELECT "event_date", "id" FROM "public"."events" WHERE "event_date" <= ?""",
            query.sql,
        )
        assertEquals(1, query.bindings.size)
    }

    @Test
    fun testTemporalColumnNotInSelectSkipsDateBounds() {
        val gen =
            SnowflakeSourceOperations(
                configWith(startDate = "2024-01-01", fullRefreshTemporalColumn = "missing_col")
            )

        val query =
            gen.generate(
                SelectQuerySpec(
                    select = SelectColumns(Field("id", IntFieldType), Field("name", StringFieldType)),
                    from = From("users", "public"),
                    where = NoWhere,
                )
            )

        assertEquals("""SELECT "id", "name" FROM "public"."users"""", query.sql)
        assertEquals(0, query.bindings.size)
    }

    // cas 2: SELECT MAX on cursor = temporal col

    /**
     * SELECT MAX on the temporal column itself (cursor == temporal col, the realistic config):
     * isCursorMax = true → the cursor is cached AND date bounds are applied to the MAX query.
     * A subsequent snapshot read must also be filtered via the cache.
     */
    @Test
    fun testTemporalColumnMaxQueryCachesAndAppliesBounds() {
        val dateField = Field("DATE_COMMANDE", LocalDateFieldType)
        val gen =
            SnowflakeSourceOperations(
                configWith(
                    startDate = "2024-01-01",
                    endDate = "2024-12-31",
                    fullRefreshTemporalColumn = "DATE_COMMANDE",
                )
            )

        val maxQuery =
            gen.generate(
                SelectQuerySpec(
                    select = SelectColumnMaxValue(dateField),
                    from = From("V1_COMMANDES", "OUT_ACTIONABLE"),
                )
            )

        assertEquals(
            """SELECT MAX("DATE_COMMANDE") FROM "OUT_ACTIONABLE"."V1_COMMANDES" WHERE ("DATE_COMMANDE" >= ?) AND ("DATE_COMMANDE" <= ?)""",
            maxQuery.sql,
        )
        assertEquals(2, maxQuery.bindings.size)

        // Cursor is now cached → a snapshot read (no ORDER BY) must also be filtered
        val snapshotQuery =
            gen.generate(
                SelectQuerySpec(
                    select = SelectColumns(dateField, Field("id", IntFieldType)),
                    from = From("V1_COMMANDES", "OUT_ACTIONABLE"),
                )
            )
        assert(snapshotQuery.sql.contains(""""DATE_COMMANDE" >= ?""")) { "startDate via cache" }
        assert(snapshotQuery.sql.contains(""""DATE_COMMANDE" <= ?""")) { "endDate via cache" }
    }

    // cas 12: NullFieldType guard (LIMIT 0 discovery queries)

    /**
     * During schema discovery the CDK issues LIMIT 0 queries. At that point column types are
     * NullFieldType — not yet resolved from JDBC metadata. The temporal column lookup must skip
     * these columns (NullFieldType is not a LosslessJdbcFieldType) to avoid a ClassCastException.
     */
    @Test
    fun testNullFieldTypeInSelectSkipsDateBoundsForFullRefresh() {
        val nullTypedDateCol = Field("event_date", NullFieldType)
        val gen =
            SnowflakeSourceOperations(
                configWith(
                    startDate = "2024-01-01",
                    endDate = "2024-12-31",
                    fullRefreshTemporalColumn = "event_date",
                )
            )

        val query =
            gen.generate(
                SelectQuerySpec(
                    select = SelectColumns(nullTypedDateCol, Field("id", NullFieldType)),
                    from = From("events", "public"),
                    where = NoWhere,
                    limit = Limit(0),
                )
            )

        // NullFieldType guard → no WHERE injected, no ClassCastException
        assertEquals("""SELECT "event_date", "id" FROM "public"."events" LIMIT 0""", query.sql)
        assertEquals(0, query.bindings.size)
    }

    // cas 23 & 24: FromSample full-refresh with PK ORDER BY

    /**
     * Cas 23: FromSample, full-refresh, ORDER BY PK, cache empty (PK MAX was not cached).
     * Step 3 (temporal column lookup) must fire and inject bounds in both inner sample and outer WHERE.
     */
    @Test
    fun testFullRefreshSamplingWithPkOrderAndEmptyCacheAppliesTemporalColumn() {
        val dateField = Field("DATE_COMMANDE", LocalDateFieldType)
        val pkField1 = Field("NUM_COMMANDE", StringFieldType)
        val pkField2 = Field("NUM_LIGNE_COMMANDE", StringFieldType)
        val gen =
            SnowflakeSourceOperations(
                configWith(
                    startDate = "2024-01-01",
                    endDate = "2024-12-31",
                    fullRefreshTemporalColumn = "DATE_COMMANDE",
                )
            )

        // PK MAX ran but was NOT cached (PK ≠ temporal col)
        gen.generate(
            SelectQuerySpec(
                select = SelectColumnMaxValue(pkField1),
                from = From("V1_COMMANDES", "OUT_ACTIONABLE"),
            )
        )

        val query =
            gen.generate(
                SelectQuerySpec(
                    select = SelectColumns(dateField, pkField1, pkField2),
                    from =
                        FromSample(
                            name = "V1_COMMANDES",
                            namespace = "OUT_ACTIONABLE",
                            sampleRateInvPow2 = 8,
                            sampleSize = 1024,
                            where = NoWhere,
                        ),
                    where = NoWhere,
                    orderBy = OrderBy(pkField1, pkField2),
                )
            )

        assertEquals(2, query.sql.split(""""DATE_COMMANDE" >= ?""").size - 1, "startDate in inner and outer")
        assertEquals(2, query.sql.split(""""DATE_COMMANDE" <= ?""").size - 1, "endDate in inner and outer")
        assert(!query.sql.contains(""""NUM_COMMANDE" >= ?""")) { "No date bounds on PK" }
        assertEquals(4, query.bindings.size)
    }

    /**
     * Cas 24: FromSample, ORDER BY PK, cache populated with cursor (= temporal col).
     * Step 2 (cache) fires before step 3, but produces the same result: bounds on temporal col.
     */
    @Test
    fun testFullRefreshSamplingWithPkOrderAndCachedCursorAppliesTemporalColumn() {
        val dateField = Field("DATE_COMMANDE", LocalDateFieldType)
        val pkField1 = Field("NUM_COMMANDE", StringFieldType)
        val pkField2 = Field("NUM_LIGNE_COMMANDE", StringFieldType)
        val gen =
            SnowflakeSourceOperations(
                configWith(
                    startDate = "2024-01-01",
                    endDate = "2024-12-31",
                    fullRefreshTemporalColumn = "DATE_COMMANDE",
                )
            )

        // Cursor MAX populates the cache with DATE_COMMANDE
        gen.generate(
            SelectQuerySpec(
                select = SelectColumnMaxValue(dateField),
                from = From("V1_COMMANDES", "OUT_ACTIONABLE"),
            )
        )

        val query =
            gen.generate(
                SelectQuerySpec(
                    select = SelectColumns(dateField, pkField1, pkField2),
                    from =
                        FromSample(
                            name = "V1_COMMANDES",
                            namespace = "OUT_ACTIONABLE",
                            sampleRateInvPow2 = 8,
                            sampleSize = 1024,
                            where = NoWhere,
                        ),
                    where = NoWhere,
                    orderBy = OrderBy(pkField1, pkField2),
                )
            )

        // Same expected output as cas 23 — cache vs step 3, same result
        assertEquals(2, query.sql.split(""""DATE_COMMANDE" >= ?""").size - 1, "startDate in inner and outer")
        assertEquals(2, query.sql.split(""""DATE_COMMANDE" <= ?""").size - 1, "endDate in inner and outer")
        assert(!query.sql.contains(""""NUM_COMMANDE" >= ?""")) { "No date bounds on PK" }
        assertEquals(4, query.bindings.size)
    }

    /**
     * When fullRefreshTemporalColumn is configured, a SELECT MAX on a PK column (used by the CDK
     * to determine partition boundaries) must NOT be cached and must NOT inject date bounds.
     */
    @Test
    fun testPkMaxQuerySkipsDateBoundsAndDoesNotPolluteCursor() {
        val pkField = Field("NUM_COMMANDE", StringFieldType)
        val gen =
            SnowflakeSourceOperations(
                configWith(startDate = "2024-01-01", endDate = "2024-12-31", fullRefreshTemporalColumn = "DATE_COMMANDE")
            )

        val query =
            gen.generate(
                SelectQuerySpec(
                    select = SelectColumnMaxValue(pkField),
                    from = From("V1_COMMANDES", "OUT_ACTIONABLE"),
                )
            )

        // NUM_COMMANDE != DATE_COMMANDE → PK MAX, no WHERE injected
        assertEquals("""SELECT MAX("NUM_COMMANDE") FROM "OUT_ACTIONABLE"."V1_COMMANDES"""", query.sql)
        assertEquals(0, query.bindings.size)
    }

    /**
     * After a PK MAX (not cached), a full-refresh read ordered by PK must apply date bounds using
     * the temporal column found in the SELECT list — not the PK.
     */
    @Test
    fun testFullRefreshReadAfterPkMaxUsesTemporalColumn() {
        val dateField = Field("DATE_COMMANDE", LocalDateFieldType)
        val pkField1 = Field("NUM_COMMANDE", StringFieldType)
        val pkField2 = Field("NUM_LIGNE_COMMANDE", StringFieldType)
        val gen =
            SnowflakeSourceOperations(
                configWith(startDate = "2024-01-01", endDate = "2024-12-31", fullRefreshTemporalColumn = "DATE_COMMANDE")
            )

        // PK MAX — must NOT cache NUM_COMMANDE
        gen.generate(
            SelectQuerySpec(
                select = SelectColumnMaxValue(pkField1),
                from = From("V1_COMMANDES", "OUT_ACTIONABLE"),
            )
        )

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
                    select = SelectColumns(dateField, pkField1, pkField2),
                    from = From("V1_COMMANDES", "OUT_ACTIONABLE"),
                    where = pkBounds,
                    orderBy = OrderBy(pkField1, pkField2),
                    limit = Limit(1000),
                )
            )

        assert(query.sql.contains(""""DATE_COMMANDE" >= ?""")) { "startDate must be on DATE_COMMANDE" }
        assert(query.sql.contains(""""DATE_COMMANDE" <= ?""")) { "endDate must be on DATE_COMMANDE" }
        assert(!query.sql.contains(""""NUM_COMMANDE" >= ?""")) { "Date bounds must NOT be on PK" }
        assert(query.sql.contains(""""NUM_COMMANDE" > ?""")) { "PK lower bound must still be present" }
        assert(query.sql.contains("""ORDER BY "NUM_COMMANDE", "NUM_LIGNE_COMMANDE"""")) { "ORDER BY must be on PK" }
    }

    /**
     * Mixed catalog: incremental and full-refresh streams share the same SnowflakeSourceOperations
     * instance. The incremental MAX caches the cursor correctly. The full-refresh PK MAX must NOT
     * overwrite that cache. Both subsequent read queries must filter on DATE_COMMANDE.
     */
    @Test
    fun testMixedIncrementalAndFullRefreshDoNotInterfereWithCache() {
        val dateField = Field("DATE_COMMANDE", LocalDateFieldType)
        val pkField1 = Field("NUM_COMMANDE", StringFieldType)
        val pkField2 = Field("NUM_LIGNE_COMMANDE", StringFieldType)
        val gen =
            SnowflakeSourceOperations(
                configWith(startDate = "2024-01-01", endDate = "2024-12-31", fullRefreshTemporalColumn = "DATE_COMMANDE")
            )

        // Incremental MAX on cursor → caches DATE_COMMANDE
        gen.generate(
            SelectQuerySpec(
                select = SelectColumnMaxValue(dateField),
                from = From("V1_COMMANDES", "OUT_ACTIONABLE"),
            )
        )

        // Full-refresh PK MAX → must NOT overwrite the cache with NUM_COMMANDE
        gen.generate(
            SelectQuerySpec(
                select = SelectColumnMaxValue(pkField1),
                from = From("V1_COMMANDES", "OUT_ACTIONABLE"),
            )
        )

        // Incremental read (ORDER BY PK): cache must still have DATE_COMMANDE
        val incrementalQuery =
            gen.generate(
                SelectQuerySpec(
                    select = SelectColumns(dateField, pkField1, pkField2),
                    from = From("V1_COMMANDES", "OUT_ACTIONABLE"),
                    where =
                        Where(
                            And(
                                Greater(dateField, LocalDateCodec.encode(LocalDate.parse("2024-06-01"))),
                                LesserOrEqual(dateField, LocalDateCodec.encode(LocalDate.parse("2024-09-01"))),
                            )
                        ),
                    orderBy = OrderBy(pkField1, pkField2),
                    limit = Limit(1000),
                )
            )
        assert(incrementalQuery.sql.contains(""""DATE_COMMANDE" >= ?""")) { "Incremental: startDate on cursor" }
        assert(!incrementalQuery.sql.contains(""""NUM_COMMANDE" >= ?""")) { "Incremental: date bound NOT on PK" }

        // Full-refresh read (ORDER BY PK, no cursor WHERE): temporal column must be used
        val fullRefreshQuery =
            gen.generate(
                SelectQuerySpec(
                    select = SelectColumns(dateField, pkField1, pkField2),
                    from = From("V1_COMMANDES", "OUT_ACTIONABLE"),
                    where = NoWhere,
                    orderBy = OrderBy(pkField1, pkField2),
                )
            )
        assert(fullRefreshQuery.sql.contains(""""DATE_COMMANDE" >= ?""")) { "Full-refresh: startDate on temporal col" }
        assert(!fullRefreshQuery.sql.contains(""""NUM_COMMANDE" >= ?""")) { "Full-refresh: date bound NOT on PK" }
    }

    /**
     * Full-refresh with a sampling query (FromSample): date bounds must be injected into both the
     * inner sampling subquery and the outer WHERE clause.
     */
    @Test
    fun testSamplingQueryAppliesDateBoundsInnerAndOuter() {
        val dateField = Field("DATE_COMMANDE", LocalDateFieldType)
        val pkField = Field("NUM_COMMANDE", StringFieldType)
        val gen =
            SnowflakeSourceOperations(
                configWith(startDate = "2024-01-01", endDate = "2024-12-31", fullRefreshTemporalColumn = "DATE_COMMANDE")
            )

        val query =
            gen.generate(
                SelectQuerySpec(
                    select = SelectColumns(dateField, pkField),
                    from =
                        FromSample(
                            name = "V1_COMMANDES",
                            namespace = "OUT_ACTIONABLE",
                            sampleRateInvPow2 = 8,
                            sampleSize = 1024,
                            where = NoWhere,
                        ),
                    where = NoWhere,
                    // No ORDER BY → full-refresh
                )
            )

        assertEquals(2, query.sql.split(""""DATE_COMMANDE" >= ?""").size - 1, "startDate in inner and outer WHERE")
        assertEquals(2, query.sql.split(""""DATE_COMMANDE" <= ?""").size - 1, "endDate in inner and outer WHERE")
        assertEquals(4, query.bindings.size)
    }
}
