/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.data.IntCodec
import io.airbyte.cdk.data.LocalDateCodec
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.output.InvalidCursor
import io.airbyte.cdk.output.InvalidPrimaryKey
import io.airbyte.cdk.output.ResetStream
import io.airbyte.cdk.read.TestFixtures.assertFailures
import io.airbyte.cdk.read.TestFixtures.assertJsonEquals
import io.airbyte.cdk.read.TestFixtures.assertQueryEquals
import io.airbyte.cdk.read.TestFixtures.factory
import io.airbyte.cdk.read.TestFixtures.id
import io.airbyte.cdk.read.TestFixtures.msg
import io.airbyte.cdk.read.TestFixtures.opaqueStateValue
import io.airbyte.cdk.read.TestFixtures.record
import io.airbyte.cdk.read.TestFixtures.sharedState
import io.airbyte.cdk.read.TestFixtures.stream
import io.airbyte.cdk.read.TestFixtures.ts
import java.time.LocalDate
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class DefaultJdbcPartitionFactoryTest {

    val cursorValue = LocalDate.parse("2024-08-19")

    @Test
    fun testColdStartUnsplittableSnapshot() {
        val stream = stream(withPK = false, withCursor = false)
        val factory = sharedState().factory()
        val result = factory.create(stream, opaqueStateValue = null)
        factory.assertFailures()
        Assertions.assertTrue(result is DefaultJdbcUnsplittableSnapshotPartition)
        val partition = result as DefaultJdbcUnsplittableSnapshotPartition
        // Check partition properties
        sanityCheck(stream, factory, partition)
        // Check query generation
        partition.nonResumableQuery.assertQueryEquals(
            SelectQuerySpec(SelectColumns(id, ts, msg), From(stream.name, stream.namespace))
        )
        partition
            .samplingQuery(sampleRateInvPow2 = 8)
            .assertQueryEquals(
                SelectQuerySpec(
                    SelectColumns(id, ts, msg),
                    FromSample(
                        stream.name,
                        stream.namespace,
                        sampleRateInvPow2 = 8,
                        DefaultJdbcConstants.TABLE_SAMPLE_SIZE,
                    ),
                )
            )
        // Check state generation
        partition.completeState.assertJsonEquals(opaqueStateValue())
    }

    @Test
    fun testColdStartUnsplittableSnapshotWithCursor() {
        val stream = stream(withPK = false)
        val factory = sharedState().factory()
        val result = factory.create(stream, null)
        factory.assertFailures()
        Assertions.assertTrue(result is DefaultJdbcUnsplittableSnapshotWithCursorPartition)
        val partition = result as DefaultJdbcUnsplittableSnapshotWithCursorPartition
        partition.streamState.cursorUpperBound = LocalDateCodec.encode(cursorValue)
        // Check partition properties
        sanityCheck(stream, factory, partition)
        Assertions.assertEquals(ts, partition.cursor)
        // Check query generation
        partition.cursorUpperBoundQuery.assertQueryEquals(
            SelectQuerySpec(SelectColumnMaxValue(ts), From(stream.name, stream.namespace))
        )
        partition.nonResumableQuery.assertQueryEquals(
            SelectQuerySpec(SelectColumns(id, ts, msg), From(stream.name, stream.namespace))
        )
        partition
            .samplingQuery(sampleRateInvPow2 = 8)
            .assertQueryEquals(
                SelectQuerySpec(
                    SelectColumns(id, ts, msg),
                    FromSample(
                        stream.name,
                        stream.namespace,
                        sampleRateInvPow2 = 8,
                        DefaultJdbcConstants.TABLE_SAMPLE_SIZE,
                    ),
                )
            )
        // Check state generation
        partition.completeState.assertJsonEquals(opaqueStateValue(cursor = cursorValue))
    }

    @Test
    fun testColdStartSplittableSnapshot() {
        val stream = stream(withCursor = false)
        val factory = sharedState().factory()
        val result = factory.create(stream, opaqueStateValue = null)
        factory.assertFailures()
        Assertions.assertTrue(result is DefaultJdbcSplittableSnapshotPartition)
        val partition = result as DefaultJdbcSplittableSnapshotPartition
        // Check partition properties
        sanityCheck(stream, factory, partition)
        Assertions.assertEquals(listOf(id), partition.checkpointColumns)
        Assertions.assertNull(partition.lowerBound)
        Assertions.assertNull(partition.upperBound)
        // Check query generation
        partition.nonResumableQuery.assertQueryEquals(
            SelectQuerySpec(SelectColumns(id, ts, msg), From(stream.name, stream.namespace))
        )
        partition
            .resumableQuery(limit = 10L)
            .assertQueryEquals(
                SelectQuerySpec(
                    SelectColumns(id, ts, msg),
                    From(stream.name, stream.namespace),
                    NoWhere,
                    OrderBy(id),
                    Limit(10L)
                )
            )
        partition
            .samplingQuery(sampleRateInvPow2 = 8)
            .assertQueryEquals(
                SelectQuerySpec(
                    SelectColumns(id, ts, msg),
                    FromSample(
                        stream.name,
                        stream.namespace,
                        sampleRateInvPow2 = 8,
                        DefaultJdbcConstants.TABLE_SAMPLE_SIZE,
                    ),
                    NoWhere,
                    OrderBy(id),
                )
            )
        // Check state generation
        partition.completeState.assertJsonEquals(opaqueStateValue())
        partition.incompleteState(record(pk = 22)).assertJsonEquals(opaqueStateValue(pk = 22))
        // Check split output
        val rawSplits: List<DefaultJdbcPartition> =
            factory.split(partition, listOf(opaqueStateValue(pk = 22), opaqueStateValue(pk = 44)))
        val splits: List<DefaultJdbcSplittableSnapshotPartition> =
            rawSplits.filterIsInstance<DefaultJdbcSplittableSnapshotPartition>()
        Assertions.assertIterableEquals(rawSplits, splits)
        splits.forEach {
            sanityCheck(stream, factory, it)
            Assertions.assertIterableEquals(listOf(id), it.checkpointColumns)
        }
        Assertions.assertEquals(3, splits.size)
        Assertions.assertNull(splits[0].lowerBound)
        Assertions.assertIterableEquals(listOf(IntCodec.encode(22)), splits[0].upperBound)
        Assertions.assertIterableEquals(listOf(IntCodec.encode(22)), splits[1].lowerBound)
        Assertions.assertIterableEquals(listOf(IntCodec.encode(44)), splits[1].upperBound)
        Assertions.assertIterableEquals(listOf(IntCodec.encode(44)), splits[2].lowerBound)
        Assertions.assertNull(splits[2].upperBound)
    }

    @Test
    fun testColdStartSplittableSnapshotWithCursor() {
        val stream = stream()
        val factory = sharedState().factory()
        val result = factory.create(stream, null)
        factory.assertFailures()
        Assertions.assertTrue(result is DefaultJdbcSplittableSnapshotWithCursorPartition)
        val partition = result as DefaultJdbcSplittableSnapshotWithCursorPartition
        partition.streamState.cursorUpperBound = LocalDateCodec.encode(cursorValue)
        // Check partition properties
        sanityCheck(stream, factory, partition)
        Assertions.assertEquals(listOf(id), partition.checkpointColumns)
        Assertions.assertEquals(ts, partition.cursor)
        Assertions.assertNull(partition.lowerBound)
        Assertions.assertNull(partition.upperBound)
        // Check query generation
        partition.cursorUpperBoundQuery.assertQueryEquals(
            SelectQuerySpec(SelectColumnMaxValue(ts), From(stream.name, stream.namespace))
        )
        partition.nonResumableQuery.assertQueryEquals(
            SelectQuerySpec(SelectColumns(id, ts, msg), From(stream.name, stream.namespace))
        )
        partition
            .resumableQuery(limit = 10L)
            .assertQueryEquals(
                SelectQuerySpec(
                    SelectColumns(id, ts, msg),
                    From(stream.name, stream.namespace),
                    NoWhere,
                    OrderBy(id),
                    Limit(10L)
                )
            )
        partition
            .samplingQuery(sampleRateInvPow2 = 8)
            .assertQueryEquals(
                SelectQuerySpec(
                    SelectColumns(id, ts, msg),
                    FromSample(
                        stream.name,
                        stream.namespace,
                        sampleRateInvPow2 = 8,
                        DefaultJdbcConstants.TABLE_SAMPLE_SIZE,
                    ),
                    NoWhere,
                    OrderBy(id)
                )
            )
        // Check state generation
        partition.completeState.assertJsonEquals(opaqueStateValue(cursor = cursorValue))
        partition
            .incompleteState(record(pk = 22))
            .assertJsonEquals(opaqueStateValue(pk = 22, cursor = cursorValue))
        // Check split output
        val rawSplits: List<DefaultJdbcPartition> =
            factory.split(partition, listOf(opaqueStateValue(pk = 22), opaqueStateValue(pk = 44)))
        val splits: List<DefaultJdbcSplittableSnapshotWithCursorPartition> =
            rawSplits.filterIsInstance<DefaultJdbcSplittableSnapshotWithCursorPartition>()
        Assertions.assertIterableEquals(rawSplits, splits)
        splits.forEach {
            sanityCheck(stream, factory, it)
            Assertions.assertIterableEquals(listOf(id), it.checkpointColumns)
            Assertions.assertEquals(ts, it.cursor)
            Assertions.assertEquals(LocalDateCodec.encode(cursorValue), it.cursorUpperBound)
        }
        Assertions.assertEquals(3, splits.size)
        Assertions.assertNull(splits[0].lowerBound)
        Assertions.assertIterableEquals(listOf(IntCodec.encode(22)), splits[0].upperBound)
        Assertions.assertIterableEquals(listOf(IntCodec.encode(22)), splits[1].lowerBound)
        Assertions.assertIterableEquals(listOf(IntCodec.encode(44)), splits[1].upperBound)
        Assertions.assertIterableEquals(listOf(IntCodec.encode(44)), splits[2].lowerBound)
        Assertions.assertNull(splits[2].upperBound)
    }

    @Test
    fun testInvalidPrimaryKey() {
        val stream = stream(withPK = false, withCursor = false)
        val factory = sharedState().factory()
        val result = factory.create(stream, opaqueStateValue(pk = 22))
        factory.assertFailures(
            InvalidPrimaryKey(stream.id, listOf(id.id)),
            ResetStream(stream.id),
        )
        Assertions.assertTrue(result is DefaultJdbcUnsplittableSnapshotPartition)
        val partition = result as DefaultJdbcUnsplittableSnapshotPartition
        // Check partition properties
        sanityCheck(stream, factory, partition)
    }

    @Test
    fun testInvalidCursor() {
        val stream = stream(withCursor = false)
        val factory = sharedState().factory()
        val result = factory.create(stream, opaqueStateValue(cursor = cursorValue))
        factory.assertFailures(
            InvalidCursor(stream.id, ts.id),
            ResetStream(stream.id),
        )
        Assertions.assertTrue(result is DefaultJdbcSplittableSnapshotPartition)
        val partition = result as DefaultJdbcSplittableSnapshotPartition
        // Check partition properties
        sanityCheck(stream, factory, partition)
        Assertions.assertEquals(listOf(id), partition.checkpointColumns)
        Assertions.assertNull(partition.lowerBound)
        Assertions.assertNull(partition.upperBound)
    }

    @Test
    fun testWarmStartSnapshot() {
        val stream = stream(withCursor = false)
        val factory = sharedState().factory()
        val result = factory.create(stream, opaqueStateValue(pk = 22))
        factory.assertFailures()
        Assertions.assertTrue(result is DefaultJdbcSplittableSnapshotPartition)
        val partition = result as DefaultJdbcSplittableSnapshotPartition
        // Check partition properties
        sanityCheck(stream, factory, partition)
        Assertions.assertEquals(listOf(id), partition.checkpointColumns)
        Assertions.assertIterableEquals(listOf(IntCodec.encode(22)), partition.lowerBound)
        Assertions.assertNull(partition.upperBound)
        // Check query generation
        partition.nonResumableQuery.assertQueryEquals(
            SelectQuerySpec(
                SelectColumns(id, ts, msg),
                From(stream.name, stream.namespace),
                Where(Greater(id, IntCodec.encode(22)))
            )
        )
        partition
            .resumableQuery(limit = 10L)
            .assertQueryEquals(
                SelectQuerySpec(
                    SelectColumns(id, ts, msg),
                    From(stream.name, stream.namespace),
                    Where(Greater(id, IntCodec.encode(22))),
                    OrderBy(id),
                    Limit(10L)
                )
            )
        partition
            .samplingQuery(sampleRateInvPow2 = 8)
            .assertQueryEquals(
                SelectQuerySpec(
                    SelectColumns(id, ts, msg),
                    FromSample(
                        stream.name,
                        stream.namespace,
                        sampleRateInvPow2 = 8,
                        DefaultJdbcConstants.TABLE_SAMPLE_SIZE,
                    ),
                    Where(Greater(id, IntCodec.encode(22))),
                    OrderBy(id),
                )
            )
        // Check state generation
        partition.completeState.assertJsonEquals(opaqueStateValue())
        partition.incompleteState(record(pk = 10)).assertJsonEquals(opaqueStateValue(pk = 10))
        // Check full refresh termination criteria
        val finalResult = factory.create(stream, opaqueStateValue())
        factory.assertFailures()
        Assertions.assertNull(finalResult)
    }

    @Test
    fun testWarmStartSnapshotWithCursor() {
        val stream = stream()
        val factory = sharedState().factory()
        val result = factory.create(stream, opaqueStateValue(pk = 22, cursor = cursorValue))
        factory.assertFailures()
        Assertions.assertTrue(result is DefaultJdbcSplittableSnapshotWithCursorPartition)
        val partition = result as DefaultJdbcSplittableSnapshotWithCursorPartition
        // Check partition properties
        sanityCheck(stream, factory, partition)
        Assertions.assertEquals(listOf(id), partition.checkpointColumns)
        Assertions.assertEquals(ts, partition.cursor)
        Assertions.assertIterableEquals(listOf(IntCodec.encode(22)), partition.lowerBound)
        Assertions.assertNull(partition.upperBound)
        // Check query generation
        partition.nonResumableQuery.assertQueryEquals(
            SelectQuerySpec(
                SelectColumns(id, ts, msg),
                From(stream.name, stream.namespace),
                Where(Greater(id, IntCodec.encode(22))),
            )
        )
        partition
            .resumableQuery(limit = 10L)
            .assertQueryEquals(
                SelectQuerySpec(
                    SelectColumns(id, ts, msg),
                    From(stream.name, stream.namespace),
                    Where(Greater(id, IntCodec.encode(22))),
                    OrderBy(id),
                    Limit(10L)
                )
            )
        partition
            .samplingQuery(sampleRateInvPow2 = 8)
            .assertQueryEquals(
                SelectQuerySpec(
                    SelectColumns(id, ts, msg),
                    FromSample(
                        stream.name,
                        stream.namespace,
                        sampleRateInvPow2 = 8,
                        DefaultJdbcConstants.TABLE_SAMPLE_SIZE,
                    ),
                    Where(Greater(id, IntCodec.encode(22))),
                    OrderBy(id)
                )
            )
        // Check state generation
        partition.completeState.assertJsonEquals(opaqueStateValue(cursor = cursorValue))
        partition
            .incompleteState(record(pk = 44))
            .assertJsonEquals(opaqueStateValue(pk = 44, cursor = cursorValue))
        // Check snapshot termination criteria and transition to cursor-based incremental
        val finalResult = factory.create(stream, opaqueStateValue(cursor = cursorValue))
        factory.assertFailures()
        Assertions.assertTrue(finalResult is DefaultJdbcCursorIncrementalPartition)
        val finalPartition = finalResult as DefaultJdbcCursorIncrementalPartition
        sanityCheck(stream, factory, finalPartition)
        Assertions.assertEquals(ts, finalPartition.cursor)
        Assertions.assertEquals(LocalDateCodec.encode(cursorValue), finalPartition.cursorLowerBound)
    }

    @Test
    fun testCursorIncremental() {
        val stream = stream(withPK = false)
        val factory = sharedState().factory()
        val result = factory.create(stream, opaqueStateValue(cursor = cursorValue))
        factory.assertFailures()
        Assertions.assertTrue(result is DefaultJdbcCursorIncrementalPartition)
        val partition = result as DefaultJdbcCursorIncrementalPartition
        val cursorUpperBound = cursorValue.plusMonths(1)
        partition.streamState.cursorUpperBound = LocalDateCodec.encode(cursorUpperBound)
        // Check partition properties
        sanityCheck(stream, factory, partition)
        Assertions.assertEquals(ts, partition.cursor)
        Assertions.assertIterableEquals(listOf(ts), partition.checkpointColumns)
        Assertions.assertEquals(LocalDateCodec.encode(cursorValue), partition.cursorLowerBound)
        Assertions.assertIterableEquals(listOf(partition.cursorLowerBound), partition.lowerBound)
        Assertions.assertEquals(LocalDateCodec.encode(cursorUpperBound), partition.cursorUpperBound)
        Assertions.assertIterableEquals(listOf(partition.cursorUpperBound), partition.upperBound)
        Assertions.assertTrue(partition.isLowerBoundIncluded)
        // Check query generation
        partition.cursorUpperBoundQuery.assertQueryEquals(
            SelectQuerySpec(SelectColumnMaxValue(ts), From(stream.name, stream.namespace))
        )
        partition.nonResumableQuery.assertQueryEquals(
            SelectQuerySpec(
                SelectColumns(id, ts, msg),
                From(stream.name, stream.namespace),
                Where(
                    And(
                        GreaterOrEqual(ts, LocalDateCodec.encode(cursorValue)),
                        LesserOrEqual(ts, LocalDateCodec.encode(cursorUpperBound))
                    ),
                ),
            )
        )
        partition
            .resumableQuery(limit = 10L)
            .assertQueryEquals(
                SelectQuerySpec(
                    SelectColumns(id, ts, msg),
                    From(stream.name, stream.namespace),
                    Where(
                        And(
                            GreaterOrEqual(ts, LocalDateCodec.encode(cursorValue)),
                            LesserOrEqual(ts, LocalDateCodec.encode(cursorUpperBound))
                        ),
                    ),
                    OrderBy(ts),
                    Limit(10L)
                )
            )
        partition
            .samplingQuery(sampleRateInvPow2 = 8)
            .assertQueryEquals(
                SelectQuerySpec(
                    SelectColumns(id, ts, msg),
                    FromSample(
                        stream.name,
                        stream.namespace,
                        sampleRateInvPow2 = 8,
                        DefaultJdbcConstants.TABLE_SAMPLE_SIZE,
                    ),
                    Where(
                        And(
                            GreaterOrEqual(ts, LocalDateCodec.encode(cursorValue)),
                            LesserOrEqual(ts, LocalDateCodec.encode(cursorUpperBound))
                        ),
                    ),
                    OrderBy(ts)
                )
            )
        // Check state generation
        partition.completeState.assertJsonEquals(opaqueStateValue(cursor = cursorUpperBound))
        partition
            .incompleteState(record(cursor = cursorValue.plusDays(1)))
            .assertJsonEquals(opaqueStateValue(cursor = cursorValue.plusDays(1)))
        // Check that subsequent non-terminal partition includes the lower bound
        val nextResult = factory.create(stream, opaqueStateValue(cursor = cursorValue.plusDays(1)))
        factory.assertFailures()
        Assertions.assertTrue(nextResult is DefaultJdbcCursorIncrementalPartition)
        val nextPartition = nextResult as DefaultJdbcCursorIncrementalPartition
        sanityCheck(stream, factory, nextPartition)
        Assertions.assertTrue(nextPartition.isLowerBoundIncluded)
        // Check termination criteria
        val finalResult = factory.create(stream, opaqueStateValue(cursor = cursorUpperBound))
        factory.assertFailures()
        Assertions.assertNull(finalResult)
        // Check split output
        val boundary1 = cursorValue.plusDays(1)
        val boundary2 = cursorValue.plusDays(2)
        val rawSplits: List<DefaultJdbcPartition> =
            factory.split(
                partition,
                listOf(opaqueStateValue(cursor = boundary1), opaqueStateValue(cursor = boundary2)),
            )
        val splits: List<DefaultJdbcCursorIncrementalPartition> =
            rawSplits.filterIsInstance<DefaultJdbcCursorIncrementalPartition>()
        Assertions.assertIterableEquals(rawSplits, splits)
        splits.forEach {
            sanityCheck(stream, factory, it)
            Assertions.assertEquals(ts, it.cursor)
        }
        Assertions.assertEquals(3, splits.size)
        Assertions.assertEquals(LocalDateCodec.encode(cursorValue), splits[0].cursorLowerBound)
        Assertions.assertTrue(splits[0].isLowerBoundIncluded)
        Assertions.assertEquals(LocalDateCodec.encode(boundary1), splits[0].cursorUpperBound)
        Assertions.assertEquals(LocalDateCodec.encode(boundary1), splits[1].cursorLowerBound)
        Assertions.assertFalse(splits[1].isLowerBoundIncluded)
        Assertions.assertEquals(LocalDateCodec.encode(boundary2), splits[1].cursorUpperBound)
        Assertions.assertEquals(LocalDateCodec.encode(boundary2), splits[2].cursorLowerBound)
        Assertions.assertFalse(splits[2].isLowerBoundIncluded)
        Assertions.assertEquals(LocalDateCodec.encode(cursorUpperBound), splits[2].cursorUpperBound)
    }

    fun sanityCheck(
        stream: Stream,
        factory: DefaultJdbcPartitionFactory,
        partition: DefaultJdbcPartition,
    ) {
        Assertions.assertEquals(stream, partition.stream)
        Assertions.assertEquals(stream, partition.streamState.stream)
        Assertions.assertEquals(factory.sharedState, partition.streamState.sharedState)
    }
}
