/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.sql

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class StarrocksSqlGeneratorTest {

    private val gen = StarrocksSqlGenerator()

    private val columns =
        listOf(
            StarrocksColumn("id", "BIGINT", nullable = true), // key, declared nullable on purpose
            StarrocksColumn("name", "STRING", nullable = true),
            StarrocksColumn("_airbyte_raw_id", "VARCHAR(64)", nullable = false),
            StarrocksColumn("_airbyte_generation_id", "BIGINT", nullable = false),
        )

    @Test
    fun `primary key table puts key columns first, NOT NULL, with PRIMARY KEY + DISTRIBUTED BY HASH`() {
        val ddl =
            gen.createTable(
                "db",
                "orders",
                columns,
                keyColumns = listOf("id"),
                model = KeyModel.PRIMARY
            )

        // key column first and forced NOT NULL even though it was declared nullable
        val body = ddl.substringAfter("(").substringBefore("PRIMARY KEY")
        assertTrue(
            body.indexOf("`id`") < body.indexOf("`name`"),
            "key column must be declared first"
        )
        assertTrue(body.contains("`id` BIGINT NOT NULL"), "key column must be NOT NULL")
        assertTrue(ddl.contains("PRIMARY KEY (`id`)"))
        assertTrue(ddl.contains("DISTRIBUTED BY HASH (`id`)"))
        assertTrue(ddl.startsWith("CREATE TABLE IF NOT EXISTS `db`.`orders`"))
    }

    @Test
    fun `composite primary key preserves key order in both clauses`() {
        val cols = columns + StarrocksColumn("region", "STRING", nullable = true)
        val ddl =
            gen.createTable(
                "db",
                "t",
                cols,
                keyColumns = listOf("id", "region"),
                model = KeyModel.PRIMARY
            )
        assertTrue(ddl.contains("PRIMARY KEY (`id`, `region`)"))
        assertTrue(ddl.contains("DISTRIBUTED BY HASH (`id`, `region`)"))
        assertTrue(ddl.contains("`region` STRING NOT NULL"))
    }

    @Test
    fun `append table uses DUPLICATE KEY on the raw id`() {
        val ddl =
            gen.createTable(
                "db",
                "events",
                columns,
                keyColumns = listOf("_airbyte_raw_id"),
                model = KeyModel.DUPLICATE,
            )
        assertTrue(ddl.contains("DUPLICATE KEY (`_airbyte_raw_id`)"))
        assertTrue(ddl.contains("DISTRIBUTED BY HASH (`_airbyte_raw_id`)"))
        // Must NOT be a PRIMARY KEY table — that would let StarRocks dedup append rows by key.
        assertFalse(
            ddl.contains("PRIMARY KEY"),
            "append table must not use PRIMARY KEY (would dedup)"
        )
    }

    @Test
    fun `replication_num appended as PROPERTIES after DISTRIBUTED BY when set`() {
        val ddl =
            gen.createTable(
                "db",
                "orders",
                columns,
                keyColumns = listOf("id"),
                model = KeyModel.PRIMARY,
                replicationNum = 1,
            )
        assertTrue(
            ddl.contains("DISTRIBUTED BY HASH (`id`)\nPROPERTIES (\"replication_num\" = \"1\")"),
            "replication_num must be appended as a PROPERTIES clause after DISTRIBUTED BY",
        )
    }

    @Test
    fun `no PROPERTIES clause when replication_num is unset`() {
        val ddl =
            gen.createTable("db", "t", columns, keyColumns = listOf("id"), model = KeyModel.PRIMARY)
        assertFalse(
            ddl.contains("PROPERTIES"),
            "unset replication_num must not emit a PROPERTIES clause"
        )
        assertFalse(ddl.contains("replication_num"))
    }

    @Test
    fun `rejects key column not present in columns`() {
        assertThrows<IllegalArgumentException> {
            gen.createTable(
                "db",
                "t",
                columns,
                keyColumns = listOf("missing"),
                model = KeyModel.PRIMARY
            )
        }
    }

    @Test
    fun `database and drop helpers`() {
        assertEquals("CREATE DATABASE IF NOT EXISTS `airbyte`", gen.createDatabase("airbyte"))
        assertEquals("DROP TABLE IF EXISTS `db`.`t`", gen.dropTable("db", "t"))
    }

    @Test
    fun `quoteIdent doubles internal backticks so names cannot break out of the identifier`() {
        assertEquals("`a`", quoteIdent("a"))
        assertEquals("`a``b`", quoteIdent("a`b"))
        // a name crafted to break out + inject is neutralized into a single quoted identifier
        assertEquals("`x`` ; DROP TABLE t; --`", quoteIdent("x` ; DROP TABLE t; --"))
    }

    @Test
    fun `DDL escapes identifiers containing backticks`() {
        val cols =
            listOf(
                StarrocksColumn("ev`il", "BIGINT", nullable = false),
                StarrocksColumn("name", "STRING", nullable = true),
            )
        val ddl =
            gen.createTable(
                "d`b",
                "t`l",
                cols,
                keyColumns = listOf("ev`il"),
                model = KeyModel.PRIMARY
            )
        assertTrue(ddl.contains("`d``b`.`t``l`"), "db/table names must be backtick-escaped")
        assertTrue(ddl.contains("`ev``il` BIGINT NOT NULL"), "column name must be backtick-escaped")
        assertEquals("DROP TABLE IF EXISTS `d``b`.`t``l`", gen.dropTable("d`b", "t`l"))
        assertEquals("ALTER TABLE `db`.`a``b` SWAP WITH `c``d`", gen.swapTable("db", "a`b", "c`d"))
    }

    @Test
    fun `swap target is qualified but the SWAP WITH operand is unqualified`() {
        // Regression: a 2nd overwrite sync emitted `SWAP WITH \`db\`.\`tmp\``, which StarRocks
        // rejects
        // with "Unexpected input '.'". The operand must be an unqualified, same-database table
        // name.
        val sql = gen.swapTable("e2e_fro", "nation", "nation_airbyte_tmp")
        assertEquals("ALTER TABLE `e2e_fro`.`nation` SWAP WITH `nation_airbyte_tmp`", sql)
        assertFalse(
            sql.substringAfter("SWAP WITH").contains("."),
            "SWAP WITH operand must not be database-qualified",
        )
    }
}
