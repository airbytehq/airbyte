/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.TransientErrorException
import io.airbyte.cdk.data.IntCodec
import io.airbyte.cdk.data.LocalDateCodec
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.output.BufferingOutputConsumer
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
import java.time.Duration
import java.time.LocalDate
import kotlin.time.Duration.Companion.seconds
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withTimeoutOrNull
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class JdbcPartitionReaderTest {

    val cursorLowerBound: LocalDate = LocalDate.parse("2024-08-01")
    val cursorCheckpoint: LocalDate = LocalDate.parse("2024-08-02")
    val cursorUpperBound: LocalDate = LocalDate.parse("2024-08-05")

    private fun idDateString(id: Int, dateStr: String, string: String): NativeRecordPayload =
        mutableMapOf(
            "id" to FieldValueEncoder(id, IntCodec),
            "ts" to FieldValueEncoder(LocalDate.parse(dateStr), LocalDateCodec),
            "msg" to FieldValueEncoder(string, TextCodec),
        )

    @Test
    fun testNonResumable() {
        // Generate partition
        val stream = stream(withPK = false)
        val sharedState =
            sharedState(
                mockedQueries =
                    arrayOf(
                        TestFixtures.MockedQuery(
                            SelectQuerySpec(
                                SelectColumns(id, ts, msg),
                                From(stream.name, stream.namespace),
                                Where(
                                    And(
                                        GreaterOrEqual(ts, LocalDateCodec.encode(cursorLowerBound)),
                                        LesserOrEqual(ts, LocalDateCodec.encode(cursorUpperBound)),
                                    )
                                ),
                            ),
                            SelectQuerier.Parameters(reuseResultObject = true, fetchSize = 2),
                            idDateString(1, "2024-08-01", "hello"),
                            idDateString(2, "2024-08-02", "how"),
                            idDateString(3, "2024-08-03", "are"),
                            idDateString(4, "2024-08-04", "you"),
                            idDateString(5, "2024-08-05", "today"),
                        )
                    ),
                maxSnapshotReadTime = Duration.ofMinutes(1),
            )
        val factory = sharedState.factory()
        val result = factory.create(stream.bootstrap(opaqueStateValue(cursor = cursorLowerBound)))
        factory.assertFailures()
        Assertions.assertTrue(result is DefaultJdbcCursorIncrementalPartition)
        val partition = result as DefaultJdbcCursorIncrementalPartition
        partition.streamState.cursorUpperBound = LocalDateCodec.encode(cursorUpperBound)
        partition.streamState.fetchSize = 2
        // Generate reader
        val reader = JdbcNonResumablePartitionReader(partition)
        // Acquire resources
        Assertions.assertEquals(
            sharedState.configuration.maxConcurrency,
            factory.sharedState.concurrencyResource.available,
        )
        Assertions.assertEquals(
            PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN,
            reader.tryAcquireResources()
        )
        Assertions.assertEquals(
            sharedState.configuration.maxConcurrency - 1,
            factory.sharedState.concurrencyResource.available,
        )
        // Run
        runBlocking { reader.run() }
        // Checkpoint
        Assertions.assertEquals(
            PartitionReadCheckpoint(opaqueStateValue(cursor = cursorUpperBound), 5),
            reader.checkpoint(),
        )
        // Check output
        Assertions.assertEquals(
            "hello how are you today",
            (partition.streamState.streamFeedBootstrap.outputConsumer as BufferingOutputConsumer)
                .records()
                .joinToString(separator = " ") { it.data["msg"].asText() }
        )
        // Release resources
        Assertions.assertEquals(
            sharedState.configuration.maxConcurrency - 1,
            factory.sharedState.concurrencyResource.available,
        )
        reader.releaseResources()
        Assertions.assertEquals(
            sharedState.configuration.maxConcurrency,
            factory.sharedState.concurrencyResource.available,
        )
    }

    @Test
    fun testResumable() {
        // Generate partition
        val stream = stream(withPK = false)
        val sharedState =
            sharedState(
                mockedQueries =
                    arrayOf(
                        TestFixtures.MockedQuery(
                            SelectQuerySpec(
                                SelectColumns(id, ts, msg),
                                From(stream.name, stream.namespace),
                                Where(
                                    And(
                                        GreaterOrEqual(ts, LocalDateCodec.encode(cursorLowerBound)),
                                        LesserOrEqual(ts, LocalDateCodec.encode(cursorUpperBound)),
                                    )
                                ),
                                OrderBy(ts),
                                Limit(4),
                            ),
                            SelectQuerier.Parameters(reuseResultObject = true, fetchSize = 2),
                            idDateString(1, "2024-08-01", "hello"),
                            idDateString(2, "2024-08-02", "how"),
                            idDateString(3, "2024-08-03", "are"),
                            idDateString(4, "2024-08-04", "you"),
                        )
                    ),
                maxSnapshotReadTime = Duration.ofMinutes(1),
            )
        val factory = sharedState.factory()
        val result = factory.create(stream.bootstrap(opaqueStateValue(cursor = cursorLowerBound)))
        factory.assertFailures()
        Assertions.assertTrue(result is DefaultJdbcCursorIncrementalPartition)
        val partition = result as DefaultJdbcCursorIncrementalPartition
        partition.streamState.cursorUpperBound = LocalDateCodec.encode(cursorUpperBound)
        partition.streamState.fetchSize = 2
        partition.streamState.updateLimitState { it.up } // so we don't hit the limit
        // Generate reader
        val reader = JdbcResumablePartitionReader(partition)
        // Acquire resources
        Assertions.assertEquals(
            sharedState.configuration.maxConcurrency,
            factory.sharedState.concurrencyResource.available,
        )
        Assertions.assertEquals(
            PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN,
            reader.tryAcquireResources()
        )
        Assertions.assertEquals(
            sharedState.configuration.maxConcurrency - 1,
            factory.sharedState.concurrencyResource.available,
        )
        // Run and simulate timing out
        runBlocking {
            withTimeoutOrNull(1) {
                try {
                    delay(100)
                } catch (_: CancellationException) {
                    // swallow
                }
                reader.run()
            }
        }
        // Checkpoint
        Assertions.assertEquals(
            PartitionReadCheckpoint(opaqueStateValue(cursor = cursorCheckpoint), 2),
            reader.checkpoint(),
        )
        // Check output
        Assertions.assertEquals(
            "hello how",
            (partition.streamState.streamFeedBootstrap.outputConsumer as BufferingOutputConsumer)
                .records()
                .joinToString(separator = " ") { it.data["msg"].asText() }
        )
        // Release resources
        Assertions.assertEquals(
            sharedState.configuration.maxConcurrency - 1,
            factory.sharedState.concurrencyResource.available,
        )
        reader.releaseResources()
        Assertions.assertEquals(
            sharedState.configuration.maxConcurrency,
            factory.sharedState.concurrencyResource.available,
        )
    }

    @Test
    fun testPartitionMaxReadTime() {
        // Generate partition
        val stream = stream(withPK = false)
        val sharedState =
            sharedState(
                mockedQueries =
                    arrayOf(
                        TestFixtures.MockedQuery(
                            SelectQuerySpec(
                                SelectColumns(id, ts, msg),
                                From(stream.name, stream.namespace),
                                Where(
                                    And(
                                        GreaterOrEqual(ts, LocalDateCodec.encode(cursorLowerBound)),
                                        LesserOrEqual(ts, LocalDateCodec.encode(cursorUpperBound)),
                                    )
                                ),
                                OrderBy(ts),
                                Limit(4),
                            ),
                            SelectQuerier.Parameters(reuseResultObject = true, fetchSize = 2),
                            idDateString(1, "2024-08-01", "hello"),
                            idDateString(2, "2024-08-02", "how"),
                            idDateString(3, "2024-08-03", "are"),
                            idDateString(4, "2024-08-04", "you"),
                        )
                    ),
                maxSnapshotReadTime = Duration.ofSeconds(1),
            )
        val factory = sharedState.factory()
        val result = factory.create(stream.bootstrap(opaqueStateValue(cursor = cursorLowerBound)))
        factory.assertFailures()
        Assertions.assertTrue(result is DefaultJdbcCursorIncrementalPartition)
        val partition = result as DefaultJdbcCursorIncrementalPartition
        partition.streamState.cursorUpperBound = LocalDateCodec.encode(cursorUpperBound)
        partition.streamState.fetchSize = 2
        partition.streamState.updateLimitState { it.up } // so we don't hit the limit
        // Generate reader
        val readerResumable = JdbcResumablePartitionReader(partition)
        // Acquire resources
        Assertions.assertEquals(
            sharedState.configuration.maxConcurrency,
            factory.sharedState.concurrencyResource.available,
        )
        Assertions.assertEquals(
            PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN,
            readerResumable.tryAcquireResources()
        )
        Assertions.assertEquals(
            sharedState.configuration.maxConcurrency - 1,
            factory.sharedState.concurrencyResource.available,
        )

        Assertions.assertThrows(TransientErrorException::class.java) {
            // Run and simulate timing out
            runBlocking {
                sharedState.snapshotReadStartTime
                delay(1.seconds)
                readerResumable.run()
            }
        }
        readerResumable.releaseResources()

        // Generate partition
        val stream2 = stream(withPK = false)
        val sharedState2 =
            sharedState(
                mockedQueries =
                    arrayOf(
                        TestFixtures.MockedQuery(
                            SelectQuerySpec(
                                SelectColumns(id, ts, msg),
                                From(stream.name, stream.namespace),
                                Where(
                                    And(
                                        GreaterOrEqual(ts, LocalDateCodec.encode(cursorLowerBound)),
                                        LesserOrEqual(ts, LocalDateCodec.encode(cursorUpperBound)),
                                    )
                                ),
                            ),
                            SelectQuerier.Parameters(reuseResultObject = true, fetchSize = 2),
                            idDateString(1, "2024-08-01", "hello"),
                            idDateString(2, "2024-08-02", "how"),
                            idDateString(3, "2024-08-03", "are"),
                            idDateString(4, "2024-08-04", "you"),
                            idDateString(5, "2024-08-05", "today"),
                        )
                    ),
                maxSnapshotReadTime = Duration.ofSeconds(1),
            )
        val factory2 = sharedState2.factory()
        val result2 =
            factory2.create(stream2.bootstrap(opaqueStateValue(cursor = cursorLowerBound)))
        factory2.assertFailures()
        Assertions.assertTrue(result2 is DefaultJdbcCursorIncrementalPartition)
        val partition2 = result2 as DefaultJdbcCursorIncrementalPartition
        partition2.streamState.cursorUpperBound = LocalDateCodec.encode(cursorUpperBound)
        partition2.streamState.fetchSize = 2
        // Generate reader

        val readerNonResumable = JdbcNonResumablePartitionReader(partition2)
        Assertions.assertEquals(
            PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN,
            readerNonResumable.tryAcquireResources()
        )

        Assertions.assertThrows(TransientErrorException::class.java) {
            // Run and simulate timing out
            runBlocking {
                sharedState2.snapshotReadStartTime
                delay(1.seconds)
                readerNonResumable.run()
            }
        }
    }
}
