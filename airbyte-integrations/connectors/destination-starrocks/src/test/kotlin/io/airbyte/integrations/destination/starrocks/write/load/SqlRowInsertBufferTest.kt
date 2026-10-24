/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.write.load

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.CDC_DELETED_AT_COLUMN
import java.math.BigDecimal
import java.math.BigInteger
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test

class SqlRowInsertBufferTest {

    private val table = TableName("db", "orders")
    private val columns = listOf("_airbyte_raw_id", "id", "name", "amount")

    private fun buf(cdc: Boolean = false, pk: List<String> = emptyList(), soft: Boolean = false) =
        SqlRowInsertBuffer(
            table,
            columns,
            cdc,
            pk,
            "jdbc:mysql://h/?sslMode=DISABLED",
            "u",
            "p",
            soft
        )

    @Test
    fun `insert sql lists quoted columns and placeholders`() {
        assertEquals(
            "INSERT INTO `db`.`orders` (`_airbyte_raw_id`, `id`, `name`, `amount`) VALUES (?, ?, ?, ?)",
            buf().insertSql(),
        )
    }

    @Test
    fun `delete sql targets the primary key columns`() {
        assertEquals(
            "DELETE FROM `db`.`orders` WHERE `id` = ?",
            buf(cdc = true, pk = listOf("id")).deleteSql()
        )
        assertEquals(
            "DELETE FROM `db`.`orders` WHERE `k1` = ? AND `k2` = ?",
            buf(cdc = true, pk = listOf("k1", "k2")).deleteSql(),
        )
    }

    @Test
    fun `sqlString renders values as strings for StarRocks coercion, null as SQL NULL`() {
        val b = buf()
        assertNull(b.sqlString(NullValue))
        // integers/decimals keep full precision (string -> StarRocks casts to BIGINT/DECIMAL)
        assertEquals(
            "9223372036854775807",
            b.sqlString(IntegerValue(BigInteger("9223372036854775807")))
        )
        assertEquals(
            "12345.678901234567890",
            b.sqlString(NumberValue(BigDecimal("12345.678901234567890")))
        )
        assertEquals("hello", b.sqlString(StringValue("hello")))
        assertEquals("1", b.sqlString(BooleanValue(true)))
        assertEquals("0", b.sqlString(BooleanValue(false)))
        // a literal `\N` string is a plain string here (no CSV null-marker collision)
        assertEquals("\\N", b.sqlString(StringValue("\\N")))
    }

    // --- resolveOperations: intra-batch CDC ordering (#76) ---

    private fun upsert(id: Long, name: String): Map<String, AirbyteValue> =
        mapOf("id" to IntegerValue(BigInteger.valueOf(id)), "name" to StringValue(name))

    /**
     * A CDC hard-delete record: deleted-at present and non-null (the value content is irrelevant).
     */
    private fun delete(id: Long): Map<String, AirbyteValue> =
        mapOf(
            "id" to IntegerValue(BigInteger.valueOf(id)),
            CDC_DELETED_AT_COLUMN to StringValue("2026-06-26T00:00:00Z")
        )

    @Test
    fun `resolveOperations collapses delete-then-reinsert of the same key to an upsert`() {
        val b = buf(cdc = true, pk = listOf("id"))
        b.accumulate(delete(5))
        b.accumulate(upsert(5, "revived"))
        val (upserts, deletes) = b.resolveOperations()
        assertEquals(0, deletes.size, "the trailing insert must win, so nothing is deleted")
        assertEquals(1, upserts.size)
        assertEquals("revived", (upserts[0]["name"] as StringValue).value)
    }

    @Test
    fun `resolveOperations collapses insert-then-delete of the same key to a delete`() {
        val b = buf(cdc = true, pk = listOf("id"))
        b.accumulate(upsert(5, "doomed"))
        b.accumulate(delete(5))
        val (upserts, deletes) = b.resolveOperations()
        assertEquals(0, upserts.size, "the trailing delete must win")
        assertEquals(1, deletes.size)
    }

    @Test
    fun `resolveOperations routes independent keys to upsert and delete buckets`() {
        val b = buf(cdc = true, pk = listOf("id"))
        b.accumulate(upsert(1, "a"))
        b.accumulate(delete(2))
        b.accumulate(upsert(3, "c"))
        val (upserts, deletes) = b.resolveOperations()
        assertEquals(2, upserts.size)
        assertEquals(1, deletes.size)
    }

    @Test
    fun `resolveOperations keeps every row for a non-cdc append stream`() {
        val b = buf(cdc = false)
        b.accumulate(upsert(1, "a"))
        b.accumulate(upsert(1, "b")) // same key — must NOT be collapsed on an append stream
        val (upserts, deletes) = b.resolveOperations()
        assertEquals(2, upserts.size)
        assertEquals(0, deletes.size)
    }
}
