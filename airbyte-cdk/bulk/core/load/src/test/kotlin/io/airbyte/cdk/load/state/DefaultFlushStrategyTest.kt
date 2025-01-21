/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import com.google.common.collect.Range
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.MockDestinationCatalogFactory
import io.airbyte.cdk.load.command.MockDestinationCatalogFactory.Companion.stream2
import io.airbyte.cdk.load.message.ChannelMessageQueue
import io.airbyte.cdk.load.task.internal.ForceFlushEvent
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Singleton
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(
    environments =
        [
            "FlushStrategyTest",
            "MockDestinationConfiguration",
        ]
)
class DefaultFlushStrategyTest {
    val stream1 = MockDestinationCatalogFactory.stream1

    @Singleton
    @Primary
    @Requires(env = ["FlushStrategyTest"])
    class MockForceFlushEventQueue : ChannelMessageQueue<ForceFlushEvent>()

    @Test
    fun testFlushByByteSize(flushStrategy: DefaultFlushStrategy, config: DestinationConfiguration) =
        runTest {
            Assertions.assertFalse(
                flushStrategy.shouldFlush(stream1, Range.all(), config.recordBatchSizeBytes - 1L)
            )
            Assertions.assertTrue(
                flushStrategy.shouldFlush(stream1, Range.all(), config.recordBatchSizeBytes)
            )
            Assertions.assertTrue(
                flushStrategy.shouldFlush(stream1, Range.all(), config.recordBatchSizeBytes * 1000L)
            )
        }

    @Test
    fun testFlushByIndex(
        flushStrategy: DefaultFlushStrategy,
        config: DestinationConfiguration,
        forceFlushEventProducer: MockForceFlushEventQueue
    ) = runTest {
        // Ensure the size trigger is not a factor
        val insufficientSize = config.recordBatchSizeBytes - 1L

        Assertions.assertFalse(
            flushStrategy.shouldFlush(stream1, Range.all(), insufficientSize),
            "Should not flush even with whole range if no event"
        )

        forceFlushEventProducer.publish(ForceFlushEvent(mapOf(stream1.descriptor to 42L)))
        Assertions.assertFalse(
            flushStrategy.shouldFlush(stream1, Range.closed(0, 41), insufficientSize),
            "Should not flush if index is not in range"
        )
        Assertions.assertTrue(
            flushStrategy.shouldFlush(stream1, Range.closed(0, 42), insufficientSize),
            "Should flush if index is in range"
        )

        Assertions.assertFalse(
            flushStrategy.shouldFlush(stream2, Range.closed(0, 42), insufficientSize),
            "Should not flush other streams"
        )
        forceFlushEventProducer.publish(ForceFlushEvent(mapOf(stream2.descriptor to 200L)))
        Assertions.assertTrue(
            flushStrategy.shouldFlush(stream2, Range.closed(0, 200), insufficientSize),
            "(Unless they also have flush points)"
        )

        Assertions.assertTrue(
            flushStrategy.shouldFlush(stream1, Range.closed(42, 100), insufficientSize),
            "Should flush even if barely in range"
        )
        Assertions.assertFalse(
            flushStrategy.shouldFlush(stream1, Range.closed(43, 100), insufficientSize),
            "Should not flush if index has been passed"
        )

        forceFlushEventProducer.publish(ForceFlushEvent(mapOf(stream1.descriptor to 100L)))
        Assertions.assertFalse(
            flushStrategy.shouldFlush(stream1, Range.closed(0, 42), insufficientSize),
            "New events indexes should invalidate old ones"
        )
        Assertions.assertTrue(
            flushStrategy.shouldFlush(stream1, Range.closed(43, 100), insufficientSize),
            "New event indexes should be honored"
        )
    }
}
