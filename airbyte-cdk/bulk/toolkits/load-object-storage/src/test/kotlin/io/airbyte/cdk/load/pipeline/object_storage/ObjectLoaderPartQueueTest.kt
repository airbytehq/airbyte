/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline.object_storage

import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartQueueFactory
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.mockk
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class ObjectLoaderPartQueueTest {
    @MockK(relaxed = true) lateinit var objectLoader: ObjectLoader

    @Test
    fun `part queue factory respects memory available`() {
        val beanFactory = ObjectLoaderPartQueueFactory(objectLoader)
        val globalMemoryManager = mockk<ReservationManager>(relaxed = true)
        every { globalMemoryManager.totalCapacityBytes } returns 1000
        coEvery { globalMemoryManager.reserveOrThrow(any(), objectLoader) } returns mockk()
        every { objectLoader.maxMemoryRatioReservedForParts } returns 0.5
        beanFactory.objectLoaderMemoryReservation(globalMemoryManager)
        coVerify { globalMemoryManager.reserveOrThrow(500, objectLoader) }
    }

    @Test
    fun `part queue clamps part size if too many workers`() {
        val beanFactory = ObjectLoaderPartQueueFactory(objectLoader)
        every { objectLoader.numPartWorkers } returns 5
        every { objectLoader.numUploadWorkers } returns 3
        every { objectLoader.partSizeBytes } returns 100
        val memoryReservation = mockk<Reserved<ObjectLoader>>(relaxed = true)
        every { memoryReservation.bytesReserved } returns 800
        val clampedSize = beanFactory.objectLoaderClampedPartSizeBytes(memoryReservation)
        Assertions.assertEquals(800 / 9, clampedSize)
    }

    @Test
    fun `part queue does not clamp part size if not too many workers`() {
        val beanFactory = ObjectLoaderPartQueueFactory(objectLoader)
        every { objectLoader.numPartWorkers } returns 5
        every { objectLoader.numUploadWorkers } returns 1
        every { objectLoader.partSizeBytes } returns 100
        val memoryReservation = mockk<Reserved<ObjectLoader>>(relaxed = true)
        every { memoryReservation.bytesReserved } returns 800
        val clampedSize = beanFactory.objectLoaderClampedPartSizeBytes(memoryReservation)
        Assertions.assertEquals(100, clampedSize)
    }

    @Test
    fun `queue capacity is derived from clamped size and available memory`() {
        val beanFactory = ObjectLoaderPartQueueFactory(objectLoader)
        every { objectLoader.numPartWorkers } returns 3
        every { objectLoader.numUploadWorkers } returns 1
        val clampedPartSize = 150L
        val memoryReservation = mockk<Reserved<ObjectLoader>>(relaxed = true)
        every { memoryReservation.bytesReserved } returns 910
        val capacity = beanFactory.objectLoaderPartQueueCapacity(clampedPartSize, memoryReservation)
        // Expected capacity is total number of parts minus number of workers
        Assertions.assertEquals(2, capacity)
    }
}
