/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.util.Jsons
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class BuildWhereClauseTest {
    private val a = EmittedField("a", IntFieldType)
    private val b = EmittedField("b", IntFieldType)
    private val one = Jsons.numberNode(1)
    private val five = Jsons.numberNode(5)
    private val ten = Jsons.numberNode(10)

    // Split partitions only bound the first checkpoint column. The first partition must include
    // its lower bound even when the bound is a strict prefix of the checkpoint columns; otherwise
    // every row sharing the minimum first-column value is skipped for composite keys.
    @Test
    fun testPrefixLowerBoundOnCompositeKeyIsInclusiveWhenRequested() {
        val actual =
            buildWhereClause(
                checkpointColumns = listOf(a, b),
                lowerBound = listOf(one),
                upperBound = listOf(ten),
                isLowerBoundIncluded = true,
            )
        val expected =
            Where(
                And(
                    listOf(
                        Or(listOf(And(listOf(GreaterOrEqual(a, one))))),
                        Or(listOf(And(listOf(LesserOrEqual(a, ten))))),
                    )
                )
            )
        assertEquals(expected, actual)
    }

    @Test
    fun testPrefixLowerBoundOnCompositeKeyIsExclusiveWhenNotRequested() {
        val actual =
            buildWhereClause(
                checkpointColumns = listOf(a, b),
                lowerBound = listOf(one),
                upperBound = listOf(ten),
                isLowerBoundIncluded = false,
            )
        val expected =
            Where(
                And(
                    listOf(
                        Or(listOf(And(listOf(Greater(a, one))))),
                        Or(listOf(And(listOf(LesserOrEqual(a, ten))))),
                    )
                )
            )
        assertEquals(expected, actual)
    }

    @Test
    fun testSingleColumnKeyLowerBoundIsInclusiveWhenRequested() {
        val actual =
            buildWhereClause(
                checkpointColumns = listOf(a),
                lowerBound = listOf(one),
                upperBound = null,
                isLowerBoundIncluded = true,
            )
        val expected = Where(Or(listOf(And(listOf(GreaterOrEqual(a, one))))))
        assertEquals(expected, actual)
    }

    // When the bound covers every checkpoint column (resuming from a checkpoint), the inclusive
    // comparison applies to the last column only.
    @Test
    fun testFullCompositeLowerBoundIsInclusiveOnLastColumnOnly() {
        val actual =
            buildWhereClause(
                checkpointColumns = listOf(a, b),
                lowerBound = listOf(one, five),
                upperBound = null,
                isLowerBoundIncluded = true,
            )
        val expected =
            Where(
                Or(
                    listOf(
                        And(listOf(Greater(a, one))),
                        And(listOf(Equal(a, one), GreaterOrEqual(b, five))),
                    )
                )
            )
        assertEquals(expected, actual)
    }

    @Test
    fun testFullCompositeLowerBoundIsExclusiveWhenNotRequested() {
        val actual =
            buildWhereClause(
                checkpointColumns = listOf(a, b),
                lowerBound = listOf(one, five),
                upperBound = null,
                isLowerBoundIncluded = false,
            )
        val expected =
            Where(
                Or(
                    listOf(
                        And(listOf(Greater(a, one))),
                        And(listOf(Equal(a, one), Greater(b, five))),
                    )
                )
            )
        assertEquals(expected, actual)
    }

    @Test
    fun testNoBoundsYieldsNoWhere() {
        val actual =
            buildWhereClause(
                checkpointColumns = listOf(a, b),
                lowerBound = null,
                upperBound = null,
                isLowerBoundIncluded = true,
            )
        assertEquals(NoWhere, actual)
    }
}
