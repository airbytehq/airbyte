package io.airbyte.cdk.load.config

import io.airbyte.cdk.load.write.LoadStrategy
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class SyncBeanFactoryTest {

    @Test
    fun `pipeline input queue is initialized with 1 partition for syncs with files`() {
        val queue = SyncBeanFactory().pipelineInputQueue(
            Fixtures.TestLoadStrategy(3),
            isFileTransfer = true,
        )

        assertEquals(1, queue.partitions)
    }

    @Test
    fun `pipeline input queue is initialized with partitions specified by load strategy`() {
        val queue = SyncBeanFactory().pipelineInputQueue(
            Fixtures.TestLoadStrategy(3),
            isFileTransfer = false,
        )

        assertEquals(3, queue.partitions)
    }

    @Test
    fun `pipeline input queue defaults to 1 partition of unspecified by load strategy`() {
        val queue = SyncBeanFactory().pipelineInputQueue(
            null,
            isFileTransfer = false,
        )

        assertEquals(1, queue.partitions)
    }

    object Fixtures {
        class TestLoadStrategy(partitions: Int): LoadStrategy {
            override val inputPartitions: Int = partitions
        }
    }
}
