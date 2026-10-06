/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigquery

import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.jdbc.LongFieldType
import io.airbyte.cdk.read.Greater
import io.airbyte.cdk.read.NoWhere
import io.airbyte.cdk.read.Where
import io.airbyte.cdk.util.Jsons
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class BigQueryConcurrentPartitionsCreatorTest {

    private val operations = BigQuerySourceOperations(dataProjectId = "my-project")
    private val id = EmittedField("id", LongFieldType)

    @Test
    fun testApproxQuantilesQueryForANativeKey() {
        val query =
            operations.approxQuantilesQuery(
                "orders",
                "sales",
                id,
                numQuantiles = 4,
                where = NoWhere
            )
        Assertions.assertEquals(
            "SELECT `id` FROM UNNEST((SELECT APPROX_QUANTILES(`id`, 4) " +
                "FROM `my-project`.`sales`.`orders`)) AS `id`",
            query.sql,
        )
        Assertions.assertTrue(query.bindings.isEmpty())
    }

    @Test
    fun testApproxQuantilesQueryCastsATextTemporalKey() {
        val day = EmittedField("day", BigQueryDateFieldType)
        val query =
            operations.approxQuantilesQuery(
                "orders",
                "sales",
                day,
                numQuantiles = 8,
                where = NoWhere
            )
        // The key is CAST to STRING for reading (as on the normal read path), while
        // APPROX_QUANTILES
        // still runs on the native DATE column.
        Assertions.assertEquals(
            "SELECT CAST(`day` AS STRING) AS `day` FROM UNNEST((SELECT APPROX_QUANTILES(`day`, 8) " +
                "FROM `my-project`.`sales`.`orders`)) AS `day`",
            query.sql,
        )
    }

    @Test
    fun testApproxQuantilesQueryKeepsThePartitionBounds() {
        val query =
            operations.approxQuantilesQuery(
                "orders",
                "sales",
                id,
                numQuantiles = 4,
                where = Where(Greater(id, Jsons.numberNode(100))),
            )
        Assertions.assertEquals(
            "SELECT `id` FROM UNNEST((SELECT APPROX_QUANTILES(`id`, 4) " +
                "FROM `my-project`.`sales`.`orders` WHERE `id` > ?)) AS `id`",
            query.sql,
        )
        Assertions.assertEquals(1, query.bindings.size)
    }

    @Test
    fun testPartitionCountFromBytes() {
        val target = 32L shl 30
        Assertions.assertEquals(
            1,
            fallbackPartitionCount(16L shl 30, 1_000, target, 50_000_000, 1_000),
        )
        Assertions.assertEquals(
            4,
            fallbackPartitionCount(100L shl 30, 1_000, target, 50_000_000, 1_000),
        )
    }

    @Test
    fun testPartitionCountFallsBackToRowsWhenBytesAreUnknown() {
        Assertions.assertEquals(
            6,
            fallbackPartitionCount(null, 6, 32L shl 30, targetRows = 1, maxPartitions = 1_000),
        )
        // Bytes win when both are present.
        Assertions.assertEquals(
            1,
            fallbackPartitionCount(
                1L,
                1_000_000_000,
                32L shl 30,
                targetRows = 1,
                maxPartitions = 1_000
            ),
        )
    }

    @Test
    fun testPartitionCountIsClampedAndDefaultsToOne() {
        Assertions.assertEquals(
            1,
            fallbackPartitionCount(null, null, 32L shl 30, 50_000_000, 1_000),
        )
        Assertions.assertEquals(
            10,
            fallbackPartitionCount(100L shl 30, null, 1L shl 30, 50_000_000, maxPartitions = 10),
        )
    }

    @Test
    fun testInteriorBoundariesDropTheExtremesAndBuildPrimaryKeyState() {
        // APPROX_QUANTILES(id, 4) over 1..100 -> [1, 25, 50, 75, 100]; interior = 25, 50, 75.
        val quantiles = listOf(1, 25, 50, 75, 100).map { Jsons.numberNode(it) }
        val boundaries = interiorBoundaries(quantiles, id)
        Assertions.assertEquals(
            listOf(
                """{"primary_key":{"id":25},"cursors":{}}""",
                """{"primary_key":{"id":50},"cursors":{}}""",
                """{"primary_key":{"id":75},"cursors":{}}""",
            ),
            boundaries.map { Jsons.writeValueAsString(it) },
        )
    }

    @Test
    fun testInteriorBoundariesDedupeSkewedQuantilesAndDropNulls() {
        val quantiles =
            listOf(
                Jsons.numberNode(1),
                Jsons.numberNode(5),
                Jsons.numberNode(5),
                Jsons.nullNode(),
                Jsons.numberNode(9),
                Jsons.numberNode(100),
            )
        val boundaries = interiorBoundaries(quantiles, id)
        Assertions.assertEquals(
            listOf(
                """{"primary_key":{"id":5},"cursors":{}}""",
                """{"primary_key":{"id":9},"cursors":{}}""",
            ),
            boundaries.map { Jsons.writeValueAsString(it) },
        )
    }

    @Test
    fun testInteriorBoundariesEmptyWhenTooFewQuantiles() {
        Assertions.assertTrue(interiorBoundaries(listOf(Jsons.numberNode(1)), id).isEmpty())
        Assertions.assertTrue(
            interiorBoundaries(listOf(Jsons.numberNode(1), Jsons.numberNode(2)), id).isEmpty(),
        )
    }
}
