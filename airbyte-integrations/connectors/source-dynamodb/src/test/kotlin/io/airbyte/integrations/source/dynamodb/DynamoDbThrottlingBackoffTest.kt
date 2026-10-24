/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodb

import java.time.Duration
import kotlin.random.Random
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import software.amazon.awssdk.services.dynamodb.model.ProvisionedThroughputExceededException
import software.amazon.awssdk.services.dynamodb.model.ResourceNotFoundException
import software.amazon.awssdk.services.dynamodb.model.ThrottlingException

/**
 * The fake clock advances by [tick] on every backoff sleep, whatever the jittered duration, so that
 * the throttling budget is deterministic; the requested durations are recorded in [sleeps].
 */
class DynamoDbThrottlingBackoffTest {

    private val tick: Duration = Duration.ofSeconds(10)
    private var now: Long = 0L
    private val sleeps: MutableList<Duration> = mutableListOf()
    private var cancelAfterSleeps: Int = Int.MAX_VALUE

    private fun backoff(maxThrottledDuration: Duration = Duration.ofMinutes(30)) =
        DynamoDbThrottlingBackoff(
            initialBackoff = Duration.ofSeconds(1),
            maxBackoff = Duration.ofSeconds(60),
            maxThrottledDuration = maxThrottledDuration,
            nanoTime = { now },
            sleep = { d: Duration ->
                sleeps.add(d)
                now += tick.toNanos()
                if (sleeps.size >= cancelAfterSleeps) throw CancellationException("checkpoint")
            },
            random = Random(42),
        )

    private fun onDemandThrottling(): ThrottlingException =
        DynamoDbExceptionClassifierTest.throttling(
            ThrottlingException.builder(),
            "ThrottlingException",
            "Throughput exceeds the maximum OnDemandThroughput configured on table or index " +
                "(Service: DynamoDb, Status Code: 400, Request ID: ABC) (SDK Attempt Count: 9)",
        )

    private fun provisionedThrottling(): ProvisionedThroughputExceededException =
        DynamoDbExceptionClassifierTest.throttling(
            ProvisionedThroughputExceededException.builder(),
            "ProvisionedThroughputExceededException",
            "The level of configured provisioned throughput for the table was exceeded.",
        )

    @Test
    fun testThrottledRequestIsRetriedUntilItSucceeds() = runBlocking {
        val failures = ArrayDeque(listOf(onDemandThrottling(), provisionedThrottling()))
        var requests = 0
        val result: String =
            backoff().call("t/0/3", "table 't' segment 0/3") {
                requests++
                failures.removeFirstOrNull()?.let { throw it }
                "page"
            }
        Assertions.assertEquals("page", result)
        Assertions.assertEquals(3, requests)
        Assertions.assertEquals(2, sleeps.size)
        sleeps.forEachIndexed { attempt: Int, d: Duration ->
            val cap: Long = 1_000L shl attempt
            Assertions.assertTrue(d.toMillis() in cap / 2..cap, "attempt $attempt slept $d")
        }
    }

    @Test
    fun testBackoffIsCappedAndPositive() {
        val b = backoff()
        for (attempt in 0..100) {
            val d: Duration = b.backoff(attempt)
            Assertions.assertTrue(d <= Duration.ofSeconds(60), "attempt $attempt: $d")
            Assertions.assertTrue(d > Duration.ZERO, "attempt $attempt: $d")
        }
    }

    @Test
    fun testOtherErrorsAreNotRetried() {
        val b = backoff()
        var requests = 0
        assertThrows<ResourceNotFoundException> {
            runBlocking {
                b.call("t/0/1", "table 't'") {
                    requests++
                    throw ResourceNotFoundException.builder().message("no such table").build()
                }
            }
        }
        Assertions.assertEquals(1, requests)
        Assertions.assertTrue(sleeps.isEmpty())
    }

    @Test
    fun testPersistentThrottlingIsRethrownOnceTheBudgetIsSpent() {
        val b = backoff(maxThrottledDuration = Duration.ofMinutes(5))
        var requests = 0
        val thrown: ThrottlingException =
            assertThrows<ThrottlingException> {
                runBlocking {
                    b.call("t/0/1", "table 't'") {
                        requests++
                        throw onDemandThrottling()
                    }
                }
            }
        Assertions.assertTrue(thrown.message!!.contains("OnDemandThroughput"))
        Assertions.assertEquals(Duration.ofMinutes(5).toNanos(), now)
        Assertions.assertEquals(31, requests)
    }

    @Test
    fun testThrottlingBudgetSurvivesACancelledReader() {
        val b = backoff(maxThrottledDuration = Duration.ofSeconds(100))
        // The CDK cancels the first round's reader at its checkpoint deadline while it waits.
        cancelAfterSleeps = 6
        assertThrows<CancellationException> {
            runBlocking { b.call("t/0/1", "table 't'") { throw onDemandThrottling() } }
        }
        Assertions.assertEquals(Duration.ofSeconds(60).toNanos(), now)
        cancelAfterSleeps = Int.MAX_VALUE
        // The next round's reader of the same segment only gets the rest of the budget.
        assertThrows<ThrottlingException> {
            runBlocking { b.call("t/0/1", "table 't'") { throw onDemandThrottling() } }
        }
        Assertions.assertEquals(Duration.ofSeconds(100).toNanos(), now)
    }

    @Test
    fun testThrottlingBudgetIsPerKey() = runBlocking {
        val b = backoff(maxThrottledDuration = Duration.ofSeconds(45))
        var calls = 0
        b.call("t/0/2", "table 't' segment 0/2") {
            if (++calls < 4) throw onDemandThrottling()
            "segment 0"
        }
        calls = 0
        val result: String =
            b.call("t/1/2", "table 't' segment 1/2") {
                if (++calls < 4) throw onDemandThrottling()
                "segment 1"
            }
        Assertions.assertEquals("segment 1", result)
    }

    @Test
    fun testSuccessResetsTheThrottlingBudget() = runBlocking {
        val b = backoff(maxThrottledDuration = Duration.ofSeconds(45))
        // Each page is throttled for 40 s, less than the budget; the two together exceed it.
        for (page in 1..2) {
            var calls = 0
            val result: String =
                b.call("t/0/1", "table 't'") {
                    if (++calls < 5) throw onDemandThrottling()
                    "page $page"
                }
            Assertions.assertEquals("page $page", result)
        }
        Assertions.assertEquals(Duration.ofSeconds(80).toNanos(), now)
    }
}
