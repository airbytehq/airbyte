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
import kotlinx.coroutines.flow.flowOf
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
        every { pathFactory.getPathMatcher(any(), any()) } answers
            {
                val suffix = secondArg<String>()
                PathMatcher(Regex("([a-z]+)$suffix"), mapOf("suffix" to 2))
            }
        every { pathFactory.getLongestStreamConstantPrefix(any(), any()) } returns "prefix/"
    }

    @Test
    fun `test that the fallback persister correctly infers the unique key to ordinal count`() =
        runTest {
            coEvery { client.list(any()) } returns
                flowOf(
                    MockObj("dog"),
                    MockObj("dog-1"),
                    MockObj("dog-3"),
                    MockObj("cat"),
                    MockObj("turtle-100")
                )
            coEvery { client.getMetadata(any()) } returns mapOf("ab-generation-id" to "1")

            val persister = ObjectStorageFallbackPersister(client, pathFactory)
            val state = persister.load(stream)
            assertEquals(state.countByKey["dog"], 3L)
            assertEquals(state.countByKey["cat"], 0L)
            assertEquals(state.countByKey["turtle"], 100L)

            assertEquals(state.ensureUnique("dog"), "dog-4")
            assertEquals(state.ensureUnique("dog"), "dog-5")
            assertEquals(state.ensureUnique("cat"), "cat-1")
            assertEquals(state.ensureUnique("turtle"), "turtle-101")
            assertEquals(state.ensureUnique("turtle"), "turtle-102")
            assertEquals(state.ensureUnique("spider"), "spider")
        }
}
