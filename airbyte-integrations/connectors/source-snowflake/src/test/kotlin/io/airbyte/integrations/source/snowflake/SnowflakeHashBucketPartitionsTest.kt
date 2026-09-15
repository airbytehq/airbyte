/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.LocalDateFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.read.And
import io.airbyte.cdk.read.From
import io.airbyte.cdk.read.GreaterOrEqual
import io.airbyte.cdk.read.LesserOrEqual
import io.airbyte.cdk.read.Sample
import io.airbyte.cdk.read.SelectColumns
import io.airbyte.cdk.read.SelectQuery
import io.airbyte.cdk.read.SelectQuerySpec
import io.airbyte.cdk.read.Where
import io.airbyte.cdk.read.optimize
import io.airbyte.cdk.util.Jsons
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class SnowflakeHashBucketPartitionsTest {

    private val generator = SnowflakeSourceOperations()
    private val vxid = EmittedField("VXID", StringFieldType)
    private val permutiveId = EmittedField("PERMUTIVE_ID", StringFieldType)
    private val createdAt = EmittedField("CREATED_AT", LocalDateFieldType)
    private val from = From("T", "S")

    private fun render(spec: SelectQuerySpec): SelectQuery = generator.generate(spec.optimize())

    @Test
    fun `adds a WHERE clause when the spec has none`() {
        val spec = SelectQuerySpec(SelectColumns(listOf(vxid, permutiveId)), from)
        val q = render(spec.withHashBucket(spec.projectedColumns, bucketIndex = 3, bucketCount = 8))
        assertEquals(
            """SELECT "VXID", "PERMUTIVE_ID" FROM "S"."T" WHERE MOD(ABS(HASH("VXID", "PERMUTIVE_ID")), 8) = ?""",
            q.sql,
        )
        assertEquals(listOf(SelectQuery.Binding(Jsons.numberNode(3), IntFieldType)), q.bindings)
    }

    @Test
    fun `extends an existing WHERE clause and keeps its bindings first`() {
        val lower = Jsons.textNode("2026-06-29")
        val upper = Jsons.textNode("2026-07-06")
        val spec =
            SelectQuerySpec(
                SelectColumns(listOf(vxid, permutiveId, createdAt)),
                from,
                Where(And(GreaterOrEqual(createdAt, lower), LesserOrEqual(createdAt, upper))),
            )
        val q = render(spec.withHashBucket(spec.projectedColumns, bucketIndex = 0, bucketCount = 2))
        assertEquals(
            """SELECT "VXID", "PERMUTIVE_ID", "CREATED_AT" FROM "S"."T" WHERE ("CREATED_AT" >= ?) AND ("CREATED_AT" <= ?) AND (MOD(ABS(HASH("VXID", "PERMUTIVE_ID", "CREATED_AT")), 2) = ?)""",
            q.sql,
        )
        assertEquals(
            listOf(
                SelectQuery.Binding(lower, LocalDateFieldType),
                SelectQuery.Binding(upper, LocalDateFieldType),
                SelectQuery.Binding(Jsons.numberNode(0), IntFieldType),
            ),
            q.bindings,
        )
    }

    @Test
    fun `identifiers are quoted by the generator, so odd names cannot break the predicate`() {
        val odd = EmittedField("my WHERE column", StringFieldType)
        val spec = SelectQuerySpec(SelectColumns(listOf(odd)), From("MY WHERE TABLE", "S"))
        val q = render(spec.withHashBucket(spec.projectedColumns, bucketIndex = 1, bucketCount = 2))
        assertEquals(
            """SELECT "my WHERE column" FROM "S"."MY WHERE TABLE" WHERE MOD(ABS(HASH("my WHERE column")), 2) = ?""",
            q.sql,
        )
    }

    @Test
    fun `hashes only the primary key when the stream has one`() {
        val projected = listOf(vxid, permutiveId, createdAt)
        assertEquals(listOf(vxid), hashColumnsFor(listOf(vxid), createdAt, projected))
        assertEquals(
            listOf(vxid, permutiveId),
            hashColumnsFor(listOf(vxid, permutiveId), createdAt, projected),
        )
        val spec = SelectQuerySpec(SelectColumns(projected), from)
        val q = render(spec.withHashBucket(listOf(vxid), bucketIndex = 0, bucketCount = 4))
        assertEquals(
            """SELECT "VXID", "PERMUTIVE_ID", "CREATED_AT" FROM "S"."T" WHERE MOD(ABS(HASH("VXID")), 4) = ?""",
            q.sql,
        )
    }

    @Test
    fun `without a primary key, hashes the projected columns except the cursor`() {
        val projected = listOf(vxid, permutiveId, createdAt)
        assertEquals(listOf(vxid, permutiveId), hashColumnsFor(null, createdAt, projected))
        assertEquals(listOf(vxid, permutiveId), hashColumnsFor(emptyList(), createdAt, projected))
        // No cursor: everything is hashed.
        assertEquals(projected, hashColumnsFor(null, null, projected))
        // The cursor is the only column: it has to be hashed.
        assertEquals(listOf(createdAt), hashColumnsFor(null, createdAt, listOf(createdAt)))
    }

    @Test
    fun `row count query keeps the partition's WHERE clause and bindings`() {
        val lower = Jsons.textNode("2026-06-29")
        val spec =
            SelectQuerySpec(
                SelectColumns(listOf(vxid, createdAt)),
                from,
                Where(GreaterOrEqual(createdAt, lower)),
            )
        val q = render(spec.asRowCount())
        assertEquals("""SELECT COUNT(*) FROM "S"."T" WHERE "CREATED_AT" >= ?""", q.sql)
        assertEquals(listOf(SelectQuery.Binding(lower, LocalDateFieldType)), q.bindings)
        assertEquals(listOf(SnowflakeRowCountColumn), q.columns)
    }

    @Test
    fun `sizes from the row count when the sample hit its row limit, otherwise from the sample`() {
        val rows = List(1024) { 100L } // 1024 sampled rows of 100 bytes
        val large = Sample(rows, Sample.Kind.LARGE, 65_536L)
        val fromWeight = 1024L * 100 * 65_536 // what the CDK alone would estimate: ~6.4 GiB
        assertEquals(fromWeight, estimateByteSize(large, rowCount = null))
        assertEquals(300_000_000L * 100, estimateByteSize(large, rowCount = 300_000_000L))
        assertTrue(
            hashBucketCount(estimateByteSize(large, 300_000_000L)) > hashBucketCount(fromWeight)
        )
        // A count never shrinks the estimate below what the sample already implies.
        assertEquals(fromWeight, estimateByteSize(large, rowCount = 10L))
        // A sample that did not hit its limit is trusted as-is; the count is ignored.
        val medium = Sample(rows, Sample.Kind.MEDIUM, 256L)
        assertEquals(1024L * 100 * 256, estimateByteSize(medium, rowCount = 300_000_000L))
    }

    @Test
    fun `rejects a projection with no columns to hash`() {
        assertThrows(IllegalArgumentException::class.java) {
            SnowflakeHashBucketColumn(emptyList(), 2)
        }
    }

    @Test
    fun `hashBucketCount sizes buckets to the safe query size with a floor of two and a cap`() {
        val safe = SnowflakeHashBucketPartitionsCreator.SAFE_QUERY_BYTES
        val cap = SnowflakeHashBucketPartitionsCreator.MAX_BUCKET_COUNT
        assertEquals(2, hashBucketCount(1L))
        assertEquals(2, hashBucketCount(safe))
        assertEquals(2, hashBucketCount(safe + 1))
        assertEquals(3, hashBucketCount(2 * safe + 1))
        assertEquals(18, hashBucketCount(8768L shl 20))
        assertEquals(cap, hashBucketCount(Long.MAX_VALUE / 4))
    }
}
