/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.data.IntCodec
import io.airbyte.cdk.data.LocalDateCodec
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.TestFixtures.assertFailures
import io.airbyte.cdk.read.TestFixtures.bootstrap
import io.airbyte.cdk.read.TestFixtures.factory
import io.airbyte.cdk.read.TestFixtures.id
import io.airbyte.cdk.read.TestFixtures.msg
import io.airbyte.cdk.read.TestFixtures.opaqueStateValue
import io.airbyte.cdk.read.TestFixtures.sharedState
import io.airbyte.cdk.read.TestFixtures.stream
import io.airbyte.cdk.read.TestFixtures.ts
import java.time.LocalDate
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class JdbcPartitionsCreatorTest {

    private fun idDateString(id: Int, dateStr: String, string: String): NativeRecordPayload =
        mutableMapOf(
            "id" to FieldValueEncoder(id, IntCodec),
            "ts" to FieldValueEncoder(LocalDate.parse(dateStr), LocalDateCodec),
            "msg" to FieldValueEncoder(string, TextCodec),
        )

    @Test
    fun testConcurrentSnapshotWithCursor() {
        val stream = stream()

        val sharedState =
            sharedState(
                constants =
                    DefaultJdbcConstants(
                        withSampling = true,
                        maxSampleSize = 4,
                        // absurdly low value to create many partitions
                        expectedThroughputBytesPerSecond = 1L,
                    ),
                mockedQueries =
                    arrayOf(
                        TestFixtures.MockedQuery(
                            expectedQuerySpec =
                                SelectQuerySpec(
                                    SelectColumnMaxValue(ts),
                                    From(stream().name, stream().namespace),
                                ),
                            expectedParameters = SelectQuerier.Parameters(fetchSize = null),
                            mutableMapOf(
                                "max" to FieldValueEncoder(cursorUpperBound, LocalDateCodec)
                            )
                        ),
                        TestFixtures.MockedQuery(
                            expectedQuerySpec =
                                SelectQuerySpec(
                                    SelectColumns(id, ts, msg),
                                    FromSample(
                                        stream().name,
                                        stream().namespace,
                                        sampleRateInvPow2 = 16,
                                        sampleSize = 4,
                                        where = NoWhere
                                    ),
                                    NoWhere,
                                    OrderBy(id)
                                ),
                            expectedParameters = SelectQuerier.Parameters(fetchSize = null),
                            idDateString(10000, "2024-08-01", "foo"),
                        ),
                        TestFixtures.MockedQuery(
                            expectedQuerySpec =
                                SelectQuerySpec(
                                    SelectColumns(id, ts, msg),
                                    FromSample(
                                        stream().name,
                                        stream().namespace,
                                        sampleRateInvPow2 = 8,
                                        sampleSize = 4,
                                        where = NoWhere
                                    ),
                                    NoWhere,
                                    OrderBy(id)
                                ),
                            expectedParameters = SelectQuerier.Parameters(fetchSize = null),
                            idDateString(10000, "2024-08-01", "foo"),
                            idDateString(20000, "2024-08-02", "bar"),
                            idDateString(30000, "2024-08-03", "baz"),
                            idDateString(40000, "2024-08-04", "quux"),
                        )
                    ),
            )
        val expectedPartitions = 5 // adjust this as needed based on inputs
        val expectedFetchSize = 681 // adjust this as needed based on inputs
        val factory = sharedState.factory()
        val initialPartition =
            factory.create(stream.bootstrap(opaqueStateValue = null)).asPartition()
        factory.assertFailures()
        val readers = JdbcConcurrentPartitionsCreator(initialPartition, factory).runInTest()
        val partitions: List<DefaultJdbcSplittableSnapshotWithCursorPartition> =
            concurrentPartitions(stream, readers)
        val streamState: DefaultJdbcStreamState = partitions.first().streamState
        Assertions.assertEquals(
            LocalDateCodec.encode(cursorUpperBound),
            streamState.cursorUpperBound
        )
        Assertions.assertEquals(expectedFetchSize, streamState.fetchSize)
        Assertions.assertEquals(expectedPartitions, partitions.size)
        Assertions.assertIterableEquals(listOf(id), partitions.first().checkpointColumns)
        Assertions.assertNull(partitions.first().lowerBound)
        for (i in 1..(expectedPartitions - 1)) {
            Assertions.assertIterableEquals(partitions[i - 1].upperBound, partitions[i].lowerBound)
            Assertions.assertIterableEquals(listOf(id), partitions[i].checkpointColumns)
        }
        Assertions.assertNull(partitions.last().upperBound)
    }

    @Test
    fun testConcurrentSnapshot() {
        val stream = stream(withCursor = false)
        val sharedState =
            sharedState(
                constants =
                    DefaultJdbcConstants(
                        withSampling = true,
                        maxSampleSize = 4,
                        // absurdly low value to create many partitions
                        expectedThroughputBytesPerSecond = 1L,
                    ),
                mockedQueries =
                    arrayOf(
                        TestFixtures.MockedQuery(
                            expectedQuerySpec =
                                SelectQuerySpec(
                                    SelectColumns(id, ts, msg),
                                    FromSample(
                                        stream().name,
                                        stream().namespace,
                                        sampleRateInvPow2 = 16,
                                        sampleSize = 4,
                                        where = Where(Greater(id, IntCodec.encode(22)))
                                    ),
                                    NoWhere,
                                    OrderBy(id)
                                ),
                            expectedParameters = SelectQuerier.Parameters(fetchSize = null),
                            idDateString(10000, "2024-08-01", "foo"),
                        ),
                        TestFixtures.MockedQuery(
                            expectedQuerySpec =
                                SelectQuerySpec(
                                    SelectColumns(id, ts, msg),
                                    FromSample(
                                        stream().name,
                                        stream().namespace,
                                        sampleRateInvPow2 = 8,
                                        sampleSize = 4,
                                        where = Where(Greater(id, IntCodec.encode(22)))
                                    ),
                                    NoWhere,
                                    OrderBy(id)
                                ),
                            expectedParameters = SelectQuerier.Parameters(fetchSize = null),
                            idDateString(10000, "2024-08-01", "foo"),
                            idDateString(20000, "2024-08-02", "bar"),
                            idDateString(30000, "2024-08-03", "baz"),
                            idDateString(40000, "2024-08-04", "quux"),
                        )
                    ),
            )
        val expectedPartitions = 5 // adjust this as needed based on inputs
        val expectedFetchSize = 681 // adjust this as needed based on inputs
        val factory = sharedState.factory()
        val initialPartition =
            factory.create(stream.bootstrap(opaqueStateValue(pk = 22))).asPartition()
        factory.assertFailures()
        val readers = JdbcConcurrentPartitionsCreator(initialPartition, factory).runInTest()
        val partitions: List<DefaultJdbcSplittableSnapshotPartition> =
            concurrentPartitions(stream, readers)
        val streamState: DefaultJdbcStreamState = partitions.first().streamState
        Assertions.assertNull(streamState.cursorUpperBound)
        Assertions.assertEquals(expectedFetchSize, streamState.fetchSize)
        Assertions.assertEquals(expectedPartitions, partitions.size)
        Assertions.assertIterableEquals(listOf(id), partitions.first().checkpointColumns)
        Assertions.assertIterableEquals(listOf(IntCodec.encode(22)), partitions.first().lowerBound)
        for (i in 1..(expectedPartitions - 1)) {
            Assertions.assertIterableEquals(partitions[i - 1].upperBound, partitions[i].lowerBound)
            Assertions.assertIterableEquals(listOf(id), partitions[i].checkpointColumns)
        }
        Assertions.assertNull(partitions.last().upperBound)
    }

    @Test
    fun testConcurrentSnapshotWithoutSampling() {
        val stream = stream(withCursor = false)
        val sharedState = sharedState()
        val factory = sharedState.factory()
        val initialPartition =
            factory.create(stream.bootstrap(opaqueStateValue(pk = 22))).asPartition()
        factory.assertFailures()
        val readers = JdbcConcurrentPartitionsCreator(initialPartition, factory).runInTest()
        val partitions: List<DefaultJdbcSplittableSnapshotPartition> =
            concurrentPartitions(stream, readers)
        // No sampling means no splitting.
        Assertions.assertEquals(1, partitions.size)
        Assertions.assertIterableEquals(
            stream.configuredPrimaryKey,
            partitions.first().checkpointColumns,
        )
        Assertions.assertEquals(listOf(IntCodec.encode(22)), partitions.first().lowerBound)
        Assertions.assertNull(partitions.first().upperBound)
    }

    @Test
    fun testColdStartSequentialSnapshot() {
        val stream = stream(withCursor = false)
        val sharedState = sharedState()
        val factory = sharedState.factory()
        val initialPartition =
            factory.create(stream.bootstrap(opaqueStateValue(pk = 22))).asPartition()
        factory.assertFailures()
        val readers = JdbcSequentialPartitionsCreator(initialPartition, factory).runInTest()
        val readerPartition: DefaultJdbcSplittableSnapshotPartition =
            sequentialPartition(stream, readers)
        Assertions.assertNull(readerPartition.streamState.cursorUpperBound)
        Assertions.assertNull(readerPartition.streamState.fetchSize)
        Assertions.assertIterableEquals(
            stream.configuredPrimaryKey,
            readerPartition.checkpointColumns,
        )
        Assertions.assertEquals(listOf(IntCodec.encode(22)), readerPartition.lowerBound)
        Assertions.assertNull(readerPartition.upperBound)
    }

    @Test
    fun testColdStartSequentialSnapshotWithSampling() {
        val stream = stream(withCursor = false)
        val sharedState =
            sharedState(
                constants =
                    DefaultJdbcConstants(
                        withSampling = true,
                        maxSampleSize = 4,
                    ),
                mockedQueries =
                    arrayOf(
                        TestFixtures.MockedQuery(
                            expectedQuerySpec =
                                SelectQuerySpec(
                                    SelectColumns(id, ts, msg),
                                    FromSample(
                                        stream().name,
                                        stream().namespace,
                                        sampleRateInvPow2 = 16,
                                        sampleSize = 4,
                                        where = Where(Greater(id, IntCodec.encode(22)))
                                    ),
                                    NoWhere,
                                    OrderBy(id)
                                ),
                            expectedParameters = SelectQuerier.Parameters(fetchSize = null),
                            idDateString(10000, "2024-08-01", "foo"),
                        ),
                        TestFixtures.MockedQuery(
                            expectedQuerySpec =
                                SelectQuerySpec(
                                    SelectColumns(id, ts, msg),
                                    FromSample(
                                        stream().name,
                                        stream().namespace,
                                        sampleRateInvPow2 = 8,
                                        sampleSize = 4,
                                        where = Where(Greater(id, IntCodec.encode(22)))
                                    ),
                                    NoWhere,
                                    OrderBy(id)
                                ),
                            expectedParameters = SelectQuerier.Parameters(fetchSize = null),
                            idDateString(10000, "2024-08-01", "foo"),
                            idDateString(20000, "2024-08-02", "bar"),
                            idDateString(30000, "2024-08-03", "baz"),
                            idDateString(40000, "2024-08-04", "quux"),
                        )
                    ),
            )
        val expectedFetchSize = 681 // adjust this as needed based on inputs
        val factory = sharedState.factory()
        val initialPartition =
            factory.create(stream.bootstrap(opaqueStateValue(pk = 22))).asPartition()
        factory.assertFailures()
        val readers = JdbcSequentialPartitionsCreator(initialPartition, factory).runInTest()
        val readerPartition: DefaultJdbcSplittableSnapshotPartition =
            sequentialPartition(stream, readers)
        Assertions.assertNull(readerPartition.streamState.cursorUpperBound)
        Assertions.assertEquals(expectedFetchSize, readerPartition.streamState.fetchSize)
        Assertions.assertIterableEquals(listOf(id), readerPartition.checkpointColumns)
        Assertions.assertEquals(listOf(IntCodec.encode(22)), readerPartition.lowerBound)
        Assertions.assertNull(readerPartition.upperBound)
    }

    @Test
    fun testColdStartCursorIncrementalSequential() {
        val stream = stream()
        val sharedState =
            sharedState(
                mockedQueries =
                    arrayOf(
                        TestFixtures.MockedQuery(
                            expectedQuerySpec =
                                SelectQuerySpec(
                                    SelectColumnMaxValue(ts),
                                    From(stream().name, stream().namespace),
                                ),
                            expectedParameters = SelectQuerier.Parameters(fetchSize = null),
                            mutableMapOf(
                                "max" to FieldValueEncoder(cursorUpperBound, LocalDateCodec)
                            )
                        ),
                    )
            )
        val factory = sharedState.factory()
        val initialPartition =
            factory
                .create(stream.bootstrap(opaqueStateValue(cursor = cursorCheckpoint)))
                .asPartition()
        factory.assertFailures()
        val readers = JdbcSequentialPartitionsCreator(initialPartition, factory).runInTest()
        val readerPartition: DefaultUnsplittableJdbcCursorIncrementalPartition =
            unsplittableSequentialPartition(stream, readers)
        Assertions.assertEquals(
            LocalDateCodec.encode(cursorUpperBound),
            readerPartition.streamState.cursorUpperBound,
        )
        Assertions.assertNull(readerPartition.streamState.fetchSize)
        Assertions.assertEquals(ts, readerPartition.cursor)
        Assertions.assertEquals(
            LocalDateCodec.encode(cursorCheckpoint),
            readerPartition.cursorLowerBound,
        )
        Assertions.assertEquals(
            LocalDateCodec.encode(cursorUpperBound),
            readerPartition.cursorUpperBound,
        )
    }

    @Test
    fun testWarmStartCursorIncrementalSequentialWithSampling() {
        val stream = stream()
        val sharedState =
            sharedState(
                constants = DefaultJdbcConstants(withSampling = true),
                // The JdbcSequentialPartitionsCreator is not expected to query anything.
                mockedQueries = arrayOf()
            )
        val factory = sharedState.factory()
        val bootstrap = stream.bootstrap(opaqueStateValue(cursor = cursorCheckpoint))
        run {
            // This warm start is particularly warm; the stream state has some transient state.
            val streamState: DefaultJdbcStreamState = factory.streamState(bootstrap)
            streamState.fetchSize = 1234
            streamState.cursorUpperBound = LocalDateCodec.encode(cursorUpperBound)
        }
        val initialPartition = factory.create(bootstrap).asPartition()
        factory.assertFailures()
        val readers = JdbcSequentialPartitionsCreator(initialPartition, factory).runInTest()
        val readerPartition: DefaultUnsplittableJdbcCursorIncrementalPartition =
            unsplittableSequentialPartition(stream, readers)
        Assertions.assertEquals(ts, readerPartition.cursor)
        Assertions.assertEquals(
            LocalDateCodec.encode(cursorCheckpoint),
            readerPartition.cursorLowerBound,
        )
        Assertions.assertEquals(
            LocalDateCodec.encode(cursorUpperBound),
            readerPartition.cursorUpperBound,
        )
    }

    val cursorCheckpoint = LocalDate.parse("2024-08-02")
    val cursorUpperBound = LocalDate.parse("2024-08-05")

    inline fun <reified T : DefaultJdbcPartition> concurrentPartitions(
        stream: Stream,
        readers: List<PartitionReader>
    ): List<T> {
        Assertions.assertTrue(readers.isNotEmpty())
        val typedReaders = readers.filterIsInstance<JdbcNonResumablePartitionReader<*>>()
        Assertions.assertIterableEquals(readers, typedReaders)
        for (reader in typedReaders) {
            Assertions.assertTrue(reader.partition is T)
            Assertions.assertEquals(stream, reader.stream)
        }
        return typedReaders.map { it.partition as T }
    }

    inline fun <reified T : DefaultJdbcPartition> sequentialPartition(
        stream: Stream,
        readers: List<PartitionReader>
    ): T {
        Assertions.assertTrue(readers.firstOrNull() is JdbcResumablePartitionReader<*>)
        Assertions.assertNull(readers.getOrNull(1))
        val reader = readers.first() as JdbcResumablePartitionReader<*>
        Assertions.assertTrue(reader.partition is T)
        val partition = reader.partition as T
        Assertions.assertEquals(stream, reader.stream)
        return partition
    }

    inline fun <reified T : DefaultJdbcPartition> unsplittableSequentialPartition(
        stream: Stream,
        readers: List<PartitionReader>
    ): T {
        Assertions.assertTrue(readers.firstOrNull() is JdbcNonResumablePartitionReader<*>)
        Assertions.assertNull(readers.getOrNull(1))
        val reader = readers.first() as JdbcNonResumablePartitionReader<*>
        Assertions.assertTrue(reader.partition is T)
        val partition = reader.partition as T
        Assertions.assertEquals(stream, reader.stream)
        return partition
    }

    fun DefaultJdbcPartition?.asPartition(): DefaultJdbcPartition {
        Assertions.assertTrue(this is DefaultJdbcPartition)
        return this as DefaultJdbcPartition
    }

    fun JdbcPartitionsCreator<DefaultJdbcSharedState, DefaultJdbcStreamState, DefaultJdbcPartition>
        .runInTest(): List<PartitionReader> {
        val sharedState: DefaultJdbcSharedState = sharedState
        // Acquire resources
        Assertions.assertEquals(
            sharedState.configuration.maxConcurrency,
            sharedState.concurrencyResource.available,
        )
        Assertions.assertEquals(
            PartitionsCreator.TryAcquireResourcesStatus.READY_TO_RUN,
            tryAcquireResources()
        )
        Assertions.assertEquals(
            sharedState.configuration.maxConcurrency - 1,
            sharedState.concurrencyResource.available,
        )
        // Run
        val partitionReaders: List<PartitionReader> = runBlocking { run() }
        // Release resources
        Assertions.assertEquals(
            sharedState.configuration.maxConcurrency - 1,
            sharedState.concurrencyResource.available,
        )
        releaseResources()
        Assertions.assertEquals(
            sharedState.configuration.maxConcurrency,
            sharedState.concurrencyResource.available,
        )
        // Return result
        return partitionReaders
    }

    /**
     * Regression test for infinite loop when an empty table has prior cursor state.
     *
     * Scenario: A table was previously synced (cursor state exists) but has since been truncated.
     * SELECT MAX(cursor) returns NULL (.isNull), but the prior state causes the partition factory
     * to keep creating new partitions each round.
     *
     * Validates that when MAX(cursor) returns NULL, we cache nullNode in
     * streamState.cursorUpperBound so the stream completes instead of looping.
     */
    @Test
    fun testEmptyTableWithPriorCursorState() {
        val stream = stream()
        val sharedState =
            sharedState(
                mockedQueries =
                    arrayOf(
                        // MAX(cursor) returns NULL — empty table
                        TestFixtures.MockedQuery(
                            expectedQuerySpec =
                                SelectQuerySpec(
                                    SelectColumnMaxValue(ts),
                                    From(stream().name, stream().namespace),
                                ),
                            expectedParameters = SelectQuerier.Parameters(fetchSize = null),
                            // single row with null value, simulating MAX() on empty table
                            // when fieldValue is null, encode() returns NullCodec.encode(null)
                            // which is a NullNode
                            mutableMapOf("max" to FieldValueEncoder(null, LocalDateCodec))
                        ),
                    )
            )
        val factory = sharedState.factory()
        // provide PRIOR cursor state (simulating a truncated table)
        val initialPartition =
            factory
                .create(stream.bootstrap(opaqueStateValue(cursor = cursorCheckpoint)))
                .asPartition()
        factory.assertFailures()

        val readers = JdbcConcurrentPartitionsCreator(initialPartition, factory).runInTest()

        // Should get a single CheckpointOnlyPartitionReader, identify that the table is empty and
        // marked
        // it as done.
        Assertions.assertEquals(1, readers.size)
        // CheckpointOnlyPartitionReader signals an empty table that needs no further reading
        Assertions.assertTrue(
            readers.first() is JdbcPartitionsCreator<*, *, *>.CheckpointOnlyPartitionReader
        )

        // cursorUpperBound should be cached as nullNode
        Assertions.assertTrue(initialPartition.streamState.cursorUpperBound?.isNull == true)

        // The complete state should be nullNode, so next round factory returns null (done)
        val checkpoint = readers.first().checkpoint()
        Assertions.assertTrue(checkpoint.opaqueStateValue.isNull)
    }

    /**
     * Extension of testEmptyTableWithPriorCursorState to verify we don't enter a loop.
     *
     * Regression test to verify that an empty table with prior cursor state does not cause an
     * infinite loop. Simulates two rounds of the partition creation cycle: Round 1: detects the
     * empty table and emits a nullNode state Round 2: receives that state and returns null (stream
     * complete).
     *
     * If the fix is reverted, Round 2 would create another partition instead of completing, and the
     * test would fail.
     */
    @Test
    fun testEmptyTableWithPriorCursorStateDoesNotLoop() {
        val stream = stream()
        val sharedState =
            sharedState(
                mockedQueries =
                    arrayOf(
                        // Round 1: MAX(cursor) returns NULL
                        TestFixtures.MockedQuery(
                            expectedQuerySpec =
                                SelectQuerySpec(
                                    SelectColumnMaxValue(ts),
                                    From(stream().name, stream().namespace),
                                ),
                            expectedParameters = SelectQuerier.Parameters(fetchSize = null),
                            mutableMapOf("max" to FieldValueEncoder(null, LocalDateCodec))
                        ),
                        // No second MAX query should happen — if it does, the test fails
                        // because there are no more mocked queries
                        )
            )
        val factory = sharedState.factory()

        // Round 1: prior cursor state, table is empty
        val partition1 =
            factory
                .create(stream.bootstrap(opaqueStateValue(cursor = cursorCheckpoint)))
                .asPartition()
        val readers = JdbcConcurrentPartitionsCreator(partition1, factory).runInTest()
        // Validating that there is only one reader
        Assertions.assertEquals(1, readers.size)

        // Get the state that CheckpointOnlyPartitionReader would emit
        val checkpointState = readers.first().checkpoint().opaqueStateValue

        // Round 2: feed that state back into the factory
        val partition2 = factory.create(stream.bootstrap(checkpointState))

        // Should be null — stream is DONE
        Assertions.assertNull(partition2)
    }
}
