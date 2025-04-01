/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline

import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.mockk.mockk
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test

class RoundRobinPartitionerTest {
    @Test
    fun `partitioner should round-robin`() {
        val partitioner = RoundRobinInputPartitioner(rotateEveryNRecords = 5)
        val record = mockk<DestinationRecordRaw>()
        val numParts = 3
        var lastPartition: Int? = null
        var recordCount = 0
        repeat(1000) {
            val partition = partitioner.getPartition(record, numParts)
            lastPartition?.let { last ->
                recordCount++
                if (recordCount == 5) {
                    recordCount = 0
                    assertEquals((last + 1) % numParts, partition)
                } else {
                    assertEquals(last, partition)
                }
            }
            lastPartition = partition
        }
    }
}
