/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.components

import java.time.Duration
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class ComponentRunnerTest {

    /**
     * Test implementation of [ConsumerComponent]. Thread-safe, as per contract. Records are
     * characters, which are accumulated into a string.
     */
    class TestConsumerComponent(val maxRecords: Int) : ConsumerComponent<Char> {

        private val sb = StringBuilder()

        override fun shouldCheckpoint(): Boolean = synchronized(sb) { sb.length >= maxRecords }

        override fun flush(): Sequence<Char> = synchronized(sb) { sb.toString() }.asSequence()

        override fun accept(c: Char) {
            synchronized(sb) { sb.append(c) }
        }
    }

    /**
     * Test implementation of [ProducerComponent]. Thread-safe, as per contract. Emits the
     * characters in [DATASET] in an infinite loop, until a latch reaches zero.
     *
     * In one less-realistic variant where [isCloseSynchronized] is true, [close] is synchronized
     * with [notifyStop] and the producer stops immediately. This makes for more predictable output.
     * Otherwise, the loop exits only once the [ComponentRunner] comes around to calling [close].
     */
    class TestProducerComponent(
        initialState: Int,
        val upperBound: Int,
        val isCloseSynchronized: Boolean,
        val notifyStop: () -> Unit,
        val consumer: ConsumerComponent<Char>,
    ) : ProducerComponent<Int> {

        private val state = AtomicInteger(initialState)
        private val latch = CountDownLatch(1)

        override fun finalState(): Int = state.get()

        override fun run() {
            while (latch.count > 0) {
                consumer.accept(DATASET[state.getAndIncrement().mod(DATASET.length)])
                if (consumer.shouldCheckpoint() || state.get() >= upperBound) {
                    notifyStop()
                    if (isCloseSynchronized) {
                        // Wait until the notification registers.
                        // This helps to make the test as deterministic as possible.
                        latch.await(maxTime.toMillis(), TimeUnit.MILLISECONDS)
                    }
                }
            }
        }

        override fun close() {
            latch.countDown()
        }
    }

    companion object {
        const val DATASET = "The Quick Brown Fox Jumped Over The Lazy Dog. "
        val log: Logger = LoggerFactory.getLogger(ComponentRunnerTest::class.java)
        // Adjust this upwards if the test starts to flake.
        val maxTime: Duration = Duration.ofMillis(100)
    }

    fun doTestCase(
        maxRecords: Int = 1_000,
        initialState: Int = 0,
        upperBound: Int = DATASET.length
    ) {
        log.info(
            "running test case with maxRecords = {}, initialState = {}, upperBound = {}",
            maxRecords,
            initialState,
            upperBound
        )
        val expectedWithoutSeparator: String =
            DATASET.repeat(1 + upperBound / DATASET.length).take(upperBound).drop(initialState)
        val expected: String =
            expectedWithoutSeparator
                .flatMapIndexed { idx, c ->
                    if (0 == (idx + 1).mod(maxRecords)) listOf(c, '|') else listOf(c)
                }
                .dropLastWhile { it == '|' }
                .joinToString(separator = "")
        log.info("expected value is '{}'", expected)
        val cb = ConsumerComponent.Builder { TestConsumerComponent(maxRecords) }
        for (isCloseSynchronized in listOf(true, false)) {
            val producerBuilder =
                ProducerComponent.Builder {
                    input: Int,
                    consumer: ConsumerComponent<Char>,
                    notifyStop ->
                    TestProducerComponent(
                        input,
                        upperBound,
                        isCloseSynchronized,
                        notifyStop,
                        consumer
                    )
                }
            val actual =
                ComponentRunner("test", producerBuilder, cb, maxTime, Comparator.naturalOrder())
                    .collectRepeatedly(initialState, upperBound)
                    .map { (records, _) -> records.joinToString(separator = "") { it.toString() } }
                    .joinToString(separator = "|")

            log.info(
                "actual value with isCloseSynchronized = {} is '{}'",
                isCloseSynchronized,
                actual
            )
            if (isCloseSynchronized) {
                Assertions.assertEquals(
                    expected,
                    actual,
                    "when producer close() is synchronized, '$actual' should equal '$expected' "
                )
            } else {
                // In this case, when notifyStop fires, the producer doesn't immediately stop
                // producing.
                // Instead. the ComponentRunner shuts the producer thread down.
                // These testing conditions are more realistic, but less deterministic, so we relax
                // the assertions.
                if (expected.contains('|')) {
                    val actualWithoutSeparator = actual.replace("|", "")
                    Assertions.assertTrue(
                        actualWithoutSeparator.startsWith(expectedWithoutSeparator),
                        "when producer close() is not synchronized, $actual should start with $expected, minus the '|' characters"
                    )
                    val actualCheckpointedChunks: List<String> =
                        actual.split('|').dropLast(1).toList()
                    if (actualCheckpointedChunks.isNotEmpty()) {
                        val shortestCheckpointedLength: Int =
                            actualCheckpointedChunks.map { it.length }.minOrNull()!!
                        Assertions.assertTrue(
                            maxRecords < shortestCheckpointedLength,
                            "expected at least $maxRecords characters before each '|' in $actual"
                        )
                    }
                } else {
                    Assertions.assertTrue(
                        actual.startsWith(expected),
                        "when producer close() is not synchronized, $actual should start with $expected"
                    )
                }
            }
        }
    }

    @Test
    fun testNoCheckpointing() {
        doTestCase(initialState = 10)
    }

    @Test
    fun testCheckpointing() {
        doTestCase(maxRecords = 3, initialState = 10)
    }

    @Test
    fun testCheckpointingWithUpperBound() {
        doTestCase(maxRecords = 3, initialState = 10, upperBound = 20)
    }
}
