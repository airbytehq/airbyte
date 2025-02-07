/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import com.google.common.collect.Range
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.MockDestinationCatalogFactory
import io.micronaut.context.annotation.Value
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
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

    @Value("\${airbyte.destination.core.record-batch-size-override}")
    private var recordBatchSizeOverride: Long? = null

    @Test
    fun testFlushByByteSize(flushStrategy: DefaultFlushStrategy, config: DestinationConfiguration) =
        runTest {
            Assertions.assertFalse(
                flushStrategy.shouldFlush(
                    stream1.descriptor,
                    Range.all(),
                    (recordBatchSizeOverride ?: config.recordBatchSizeBytes) - 1L
                )
            )
            Assertions.assertTrue(
                flushStrategy.shouldFlush(
                    stream1.descriptor,
                    Range.all(),
                    config.recordBatchSizeBytes
                )
            )
            Assertions.assertTrue(
                flushStrategy.shouldFlush(
                    stream1.descriptor,
                    Range.all(),
                    config.recordBatchSizeBytes * 1000L
                )
            )
        }
}
