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
    class TestConsumerComponent(val maxRecords: Int) : ConsumerComponent<Char,Char> {

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
        val consumer: ConsumerComponent<Char, *>,
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

    @Test
    fun testNoCheckpointing() {
        doTestCases(DATASET, TestCase())
        doTestCases("Brown Fox Jumped Over The Lazy Dog. ", TestCase(initialState = 10))
    }

    @Test
    fun testCheckpointing() {
        doTestCases(
            "Bro|wn |Fox| Ju|mpe|d O|ver| Th|e L|azy| Do|g. ",
            TestCase(maxRecords = 3, initialState = 10)
        )
    }

    @Test
    fun testCheckpointingWithUpperBound() {
        doTestCases("Brow|n Fo|x ", TestCase(maxRecords = 4, initialState = 10, upperBound = 20))
    }

    fun doTestCases(
        expectedLiteral: String,
        tc: TestCase,
    ) {
        Assertions.assertEquals(expectedLiteral, tc.expected())
        log.info("running {}", tc)
        log.info("expected value is '{}'", tc.expected())
        doTestCase(tc, isCloseSynchronized = false)
        doTestCase(tc, isCloseSynchronized = true)
    }

    data class TestCase(
        val maxRecords: Int = 1_000,
        val initialState: Int = 0,
        val upperBound: Int = DATASET.length
    ) {
        fun expected(): String =
            DATASET.repeat(1 + upperBound / DATASET.length)
                .take(upperBound)
                .drop(initialState)
                .flatMapIndexed { idx, c ->
                    if (0 == (idx + 1).mod(maxRecords)) listOf(c, '|') else listOf(c)
                }
                .dropLastWhile { it == '|' }
                .joinToString(separator = "")
    }

    fun doTestCase(
        tc: TestCase,
        isCloseSynchronized: Boolean,
    ) {
        val expected: String = tc.expected()
        val actual: String = collectRepeatedly(tc, isCloseSynchronized)
        log.info("actual value with isCloseSynchronized = {} is '{}'", isCloseSynchronized, actual)
        if (isCloseSynchronized) {
            Assertions.assertEquals(
                tc.expected(),
                actual,
                "when producer close() is synchronized, '$actual' should equal '$expected'"
            )
        } else {
            // In this case, when notifyStop fires, the producer doesn't immediately stop
            // producing. Instead. the ComponentRunner shuts the producer thread down.
            // These testing conditions are more realistic, but less deterministic, so we relax
            // the assertions.
            Assertions.assertTrue(
                actual.replace("|", "").startsWith(expected.replace("|", "")),
                "when producer close() is not synchronized, " +
                    "'$actual' should start with '$expected', minus the '|' characters"
            )
        }
    }

    fun collectRepeatedly(
        tc: TestCase,
        isCloseSynchronized: Boolean,
    ): String {
        val consumerBuilder = ConsumerComponent.Builder { TestConsumerComponent(tc.maxRecords) }
        val producerBuilder =
            ProducerComponent.Builder { input: Int, consumer: ConsumerComponent<Char,*>, notifyStop ->
                TestProducerComponent(
                    input,
                    tc.upperBound,
                    isCloseSynchronized,
                    notifyStop,
                    consumer
                )
            }
        val runner =
            ComponentRunner(
                name = "test",
                producerBuilder,
                consumerBuilder,
                maxTime,
                Comparator.naturalOrder()
            )
        val output: Sequence<Pair<Sequence<Char>, Int>> =
            runner.collectRepeatedly(tc.initialState, tc.upperBound)
        val collectedChunks: Sequence<String> =
            output.map { (records, _) -> records.joinToString(separator = "") { it.toString() } }
        return collectedChunks.joinToString(separator = "|")
    }
}
