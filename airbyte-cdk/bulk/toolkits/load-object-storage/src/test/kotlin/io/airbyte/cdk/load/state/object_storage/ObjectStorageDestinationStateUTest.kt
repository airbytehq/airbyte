/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state.object_storage

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.object_storage.PathMatcher
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.mockk.coEvery
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.mockk
import java.util.concurrent.ConcurrentLinkedQueue
import kotlinx.coroutines.flow.asFlow
import kotlinx.coroutines.flow.filter
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class ObjectStorageDestinationStateUTest {
    data class MockObj(override val key: String, override val storageConfig: Unit = Unit) :
        RemoteObject<Unit>

    @MockK lateinit var stream: DestinationStream
    @MockK lateinit var client: ObjectStorageClient<*>
    @MockK lateinit var pathFactory: ObjectStoragePathFactory

    @BeforeEach
    fun setup() {
        every { stream.descriptor } returns DestinationStream.Descriptor("test", "stream")
        every { pathFactory.getLongestStreamConstantPrefix(any(), any()) } returns ""
    }

    @Test
    fun `test inferring unique key`() = runTest {
        val mockObjects =
            ConcurrentLinkedQueue(
                listOf(
                    MockObj("dog"),
                    MockObj("dog-1"),
                    MockObj("dog-3"),
                    MockObj("cat"),
                    MockObj("turtle-1-100")
                )
            )
        coEvery { client.list(any()) } answers
            {
                val prefix = firstArg<String>()
                mockObjects.asFlow().filter { it.key.startsWith(prefix) }
            }

        every { pathFactory.getPathMatcher(any(), any()) } answers
            {
                val suffix = secondArg<String>()
                PathMatcher(Regex("(dog|cat|turtle-1)$suffix"), mapOf("suffix" to 2))
            }

        val persister = ObjectStorageFallbackPersister(client, pathFactory)
        val state = persister.load(stream)

        assertEquals("dog-4", state.ensureUnique("dog"))
        assertEquals("dog-5", state.ensureUnique("dog"))
        assertEquals("cat-1", state.ensureUnique("cat"))
        assertEquals("turtle-1-101", state.ensureUnique("turtle-1"))
        assertEquals("turtle-1-102", state.ensureUnique("turtle-1"))
        assertEquals("spider", state.ensureUnique("spider"))
    }

    @Test
    fun `test inferring part number`() = runTest {
        val mockObjects =
            ConcurrentLinkedQueue(
                listOf(
                    MockObj("dog/file.0.jsonl"),
                    MockObj("dog/file.1.jsonl"),
                    MockObj("dog/file.2.jsonl"),
                    MockObj("cat/file.1.jsonl"),
                    MockObj("turtle-1/file.100.jsonl")
                )
            )
        coEvery { client.list(any()) } answers
            {
                val prefix = firstArg<String>()
                mockObjects.asFlow().filter { it.key.startsWith(prefix) }
            }

        every { pathFactory.getPathMatcher(any(), any()) } answers
            {
                val suffix = secondArg<String>()
                PathMatcher(
                    Regex("(dog|cat|turtle-1)/file\\.([0-9]+)\\.(jsonl)$suffix"),
                    mapOf("part_number" to 2, "suffix" to 4)
                )
            }

        val persister = ObjectStorageFallbackPersister(client, pathFactory)
        val state = persister.load(stream)

        assertEquals(2L, state.getPartIdCounter("dog/").get())
        assertEquals(1L, state.getPartIdCounter("cat/").get())
        assertEquals(100L, state.getPartIdCounter("turtle-1/").get())
        assertEquals(-1L, state.getPartIdCounter("spider/").get())
    }

    @Test
    fun `test get objects to delete`() = runTest {
        val mockObjects =
            ConcurrentLinkedQueue(
                listOf(
                    MockObj("dog/1"),
                    MockObj("dog/2"),
                    MockObj("dog/3"),
                    MockObj("cat/1"),
                    MockObj("cat/2"),
                    MockObj("cat/3"),
                    MockObj("turtle-1/1"),
                    MockObj("turtle-1/2")
                )
            )
        coEvery { client.list(any()) } answers
            {
                val prefix = firstArg<String>()
                mockObjects.asFlow().filter { it.key.startsWith(prefix) }
            }

        every { pathFactory.getPathMatcher(any(), any()) } answers
            {
                val stream = firstArg<DestinationStream>()
                val suffix = secondArg<String>()
                PathMatcher(
                    Regex("(${stream.descriptor.name})/([0-9]+)$suffix"),
                    mapOf("suffix" to 3)
                )
            }

        coEvery { client.getMetadata(any()) } answers
            {
                val key = firstArg<String>()
                mapOf("ab-generation-id" to key.split("/").last())
            }

        val persister = ObjectStorageFallbackPersister(client, pathFactory)

        val dogStream = mockk<DestinationStream>(relaxed = true)
        every { dogStream.descriptor } returns DestinationStream.Descriptor("test", "dog")
        every { dogStream.minimumGenerationId } returns 0L
        every { dogStream.shouldBeTruncatedAtEndOfSync() } returns true
        val dogState = persister.load(dogStream)
        assertEquals(0, dogState.getObjectsToDelete().size)

        val catStream = mockk<DestinationStream>(relaxed = true)
        every { catStream.descriptor } returns DestinationStream.Descriptor("test", "cat")
        every { catStream.minimumGenerationId } returns 3L
        every { catStream.shouldBeTruncatedAtEndOfSync() } returns true
        val catState = persister.load(catStream)
        assertEquals(
            setOf("cat/1", "cat/2"),
            catState.getObjectsToDelete().map { it.second.key }.toSet()
        )

        val turtleStream = mockk<DestinationStream>(relaxed = true)
        every { turtleStream.descriptor } returns DestinationStream.Descriptor("test", "turtle-1")
        every { turtleStream.minimumGenerationId } returns 3L
        every { turtleStream.shouldBeTruncatedAtEndOfSync() } returns false
        val turtleState = persister.load(turtleStream)
        assertEquals(0, turtleState.getObjectsToDelete().size)
    }
}
