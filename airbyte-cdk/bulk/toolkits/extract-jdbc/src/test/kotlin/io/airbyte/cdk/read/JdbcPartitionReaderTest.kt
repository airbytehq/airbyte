/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.data.LocalDateCodec
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.read.TestFixtures.assertFailures
import io.airbyte.cdk.read.TestFixtures.factory
import io.airbyte.cdk.read.TestFixtures.id
import io.airbyte.cdk.read.TestFixtures.msg
import io.airbyte.cdk.read.TestFixtures.opaqueStateValue
import io.airbyte.cdk.read.TestFixtures.sharedState
import io.airbyte.cdk.read.TestFixtures.stream
import io.airbyte.cdk.read.TestFixtures.ts
import java.time.LocalDate
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withTimeoutOrNull
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class JdbcPartitionReaderTest {

    val cursorLowerBound = LocalDate.parse("2024-08-01")
    val cursorCheckpoint = LocalDate.parse("2024-08-02")
    val cursorUpperBound = LocalDate.parse("2024-08-05")

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
                            """{"id":1,"ts":"2024-08-01","msg":"hello"}""",
                            """{"id":2,"ts":"2024-08-02","msg":"how"}""",
                            """{"id":3,"ts":"2024-08-03","msg":"are"}""",
                            """{"id":4,"ts":"2024-08-04","msg":"you"}""",
                            """{"id":5,"ts":"2024-08-05","msg":"today"}""",
                        )
                    )
            )
        val factory = sharedState.factory()
        val result = factory.create(stream, opaqueStateValue(cursor = cursorLowerBound))
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
            factory.sharedState.semaphore.availablePermits,
        )
        Assertions.assertEquals(
            PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN,
            reader.tryAcquireResources()
        )
        Assertions.assertEquals(
            sharedState.configuration.maxConcurrency - 1,
            factory.sharedState.semaphore.availablePermits,
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
            (sharedState.outputConsumer as BufferingOutputConsumer)
                .records()
                .map { it.data["msg"].asText() }
                .joinToString(separator = " ")
        )
        // Release resources
        Assertions.assertEquals(
            sharedState.configuration.maxConcurrency - 1,
            factory.sharedState.semaphore.availablePermits,
        )
        reader.releaseResources()
        Assertions.assertEquals(
            sharedState.configuration.maxConcurrency,
            factory.sharedState.semaphore.availablePermits,
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
                            """{"id":1,"ts":"2024-08-01","msg":"hello"}""",
                            """{"id":2,"ts":"2024-08-02","msg":"how"}""",
                            """{"id":3,"ts":"2024-08-03","msg":"are"}""",
                            """{"id":4,"ts":"2024-08-04","msg":"you"}""",
                        )
                    )
            )
        val factory = sharedState.factory()
        val result = factory.create(stream, opaqueStateValue(cursor = cursorLowerBound))
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
            factory.sharedState.semaphore.availablePermits,
        )
        Assertions.assertEquals(
            PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN,
            reader.tryAcquireResources()
        )
        Assertions.assertEquals(
            sharedState.configuration.maxConcurrency - 1,
            factory.sharedState.semaphore.availablePermits,
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
            (sharedState.outputConsumer as BufferingOutputConsumer)
                .records()
                .map { it.data["msg"].asText() }
                .joinToString(separator = " ")
        )
        // Release resources
        Assertions.assertEquals(
            sharedState.configuration.maxConcurrency - 1,
            factory.sharedState.semaphore.availablePermits,
        )
        reader.releaseResources()
        Assertions.assertEquals(
            sharedState.configuration.maxConcurrency,
            factory.sharedState.semaphore.availablePermits,
        )
    }
}
