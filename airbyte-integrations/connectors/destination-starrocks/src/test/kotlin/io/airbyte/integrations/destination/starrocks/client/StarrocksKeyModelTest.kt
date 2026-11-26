/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.client

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.Overwrite
import io.airbyte.cdk.load.component.ColumnChangeset
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.ColumnTypeChange
import io.airbyte.integrations.destination.starrocks.schema.StarrocksSqlTypes
import io.airbyte.integrations.destination.starrocks.sql.KeyModel
import io.airbyte.integrations.destination.starrocks.sql.StarrocksColumn
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

/**
 * Guards the append-vs-dedup table model (the concern that an append sync into a PRIMARY KEY table
 * would let StarRocks collapse duplicate-key rows): append/overwrite MUST map to DUPLICATE KEY (no
 * dedup), only dedupe maps to PRIMARY KEY (load-time upsert/delete).
 */
class StarrocksKeyModelTest {

    @Test
    fun `append and overwrite use DUPLICATE KEY so StarRocks does not dedup`() {
        assertEquals(KeyModel.DUPLICATE, keyModelFor(Append))
        assertEquals(KeyModel.DUPLICATE, keyModelFor(Overwrite))
    }

    @Test
    fun `dedupe uses PRIMARY KEY for load-time upsert and delete`() {
        assertEquals(
            KeyModel.PRIMARY,
            keyModelFor(Dedupe(primaryKey = listOf(listOf("id")), cursor = emptyList())),
        )
    }

    @Test
    fun `canonicalStarrocksType normalizes information_schema types to the mapper literals`() {
        // Regression: a 2nd sync compared discovered `bigint` to canonical `BIGINT` and tried to
        // ALTER the PRIMARY KEY columns (which StarRocks rejects). Normalization makes them equal.
        assertEquals(StarrocksSqlTypes.BIGINT, canonicalStarrocksType("bigint"))
        assertEquals(StarrocksSqlTypes.STRING, canonicalStarrocksType("varchar"))
        assertEquals(StarrocksSqlTypes.STRING, canonicalStarrocksType("varchar(1048576)"))
        assertEquals(StarrocksSqlTypes.DECIMAL, canonicalStarrocksType("decimal"))
        assertEquals(StarrocksSqlTypes.DECIMAL, canonicalStarrocksType("decimal(38,9)"))
        assertEquals(StarrocksSqlTypes.DATETIME, canonicalStarrocksType("datetime"))
        assertEquals(StarrocksSqlTypes.DATE, canonicalStarrocksType("date"))
        assertEquals(StarrocksSqlTypes.BOOLEAN, canonicalStarrocksType("boolean"))
        assertEquals(StarrocksSqlTypes.JSON, canonicalStarrocksType("json"))
    }

    // --- rebuildColumns / rebuildInsertSql: schema-evolution rebuild (#70) ---

    @Test
    fun `rebuildColumns keeps a non-key column nullable when it cannot be tightened to NOT NULL`() {
        // #77: a non-key column that is nullable in the real table but desired NOT NULL stays
        // nullable in
        // the rebuilt table (existing rows may hold NULLs); key columns stay NOT NULL.
        val columns =
            listOf(
                StarrocksColumn("id", StarrocksSqlTypes.BIGINT, nullable = false), // key
                StarrocksColumn(
                    "code",
                    StarrocksSqlTypes.BIGINT,
                    nullable = false
                ), // desired NOT NULL
                StarrocksColumn("name", StarrocksSqlTypes.STRING, nullable = true), // unchanged
            )
        val changeset =
            ColumnChangeset(
                columnsToAdd = emptyMap(),
                columnsToDrop = emptyMap(),
                columnsToChange =
                    mapOf(
                        "id" to
                            ColumnTypeChange(
                                ColumnType(StarrocksSqlTypes.STRING, false),
                                ColumnType(StarrocksSqlTypes.BIGINT, false),
                            ),
                        "code" to
                            ColumnTypeChange(
                                ColumnType(StarrocksSqlTypes.STRING, true),
                                ColumnType(StarrocksSqlTypes.BIGINT, false),
                            ),
                    ),
                columnsToRetain = emptyMap(),
            )
        val out = rebuildColumns(columns, setOf("id"), changeset).associateBy { it.name }
        assertEquals(false, out.getValue("id").nullable) // key stays NOT NULL
        assertEquals(true, out.getValue("code").nullable) // #77: kept nullable
        assertEquals(true, out.getValue("name").nullable) // untouched
    }

    @Test
    fun `rebuildInsertSql casts changed columns, NULLs added columns, and copies the rest`() {
        val columns =
            listOf(
                StarrocksColumn(
                    "_airbyte_raw_id",
                    StarrocksSqlTypes.STRING,
                    nullable = false
                ), // meta
                StarrocksColumn("id", StarrocksSqlTypes.BIGINT, nullable = false), // retained
                StarrocksColumn(
                    "amount",
                    StarrocksSqlTypes.DECIMAL,
                    nullable = true
                ), // changed -> CAST
                StarrocksColumn("note", StarrocksSqlTypes.STRING, nullable = true), // added -> NULL
            )
        val changeset =
            ColumnChangeset(
                columnsToAdd = mapOf("note" to ColumnType(StarrocksSqlTypes.STRING, true)),
                columnsToDrop = emptyMap(),
                columnsToChange =
                    mapOf(
                        "amount" to
                            ColumnTypeChange(
                                ColumnType(StarrocksSqlTypes.BIGINT, true),
                                ColumnType(StarrocksSqlTypes.DECIMAL, true),
                            ),
                    ),
                columnsToRetain = mapOf("id" to ColumnType(StarrocksSqlTypes.BIGINT, false)),
            )
        assertEquals(
            "INSERT INTO `db`.`t_tmp` (`_airbyte_raw_id`, `id`, `amount`, `note`) " +
                "SELECT `_airbyte_raw_id`, `id`, CAST(`amount` AS DECIMAL(38, 9)), NULL FROM `db`.`t`",
            rebuildInsertSql("`db`.`t_tmp`", "`db`.`t`", columns, changeset),
        )
    }
}
