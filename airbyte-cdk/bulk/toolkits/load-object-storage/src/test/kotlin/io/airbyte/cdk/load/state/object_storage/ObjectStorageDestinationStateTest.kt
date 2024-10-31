/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state.object_storage

import io.airbyte.cdk.load.MockObjectStorageClient
import io.airbyte.cdk.load.MockPathFactory
import io.airbyte.cdk.load.command.MockDestinationCatalogFactory
import io.airbyte.cdk.load.state.DestinationStateManager
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(
    rebuildContext = true,
    environments =
        [
            "ObjectStorageDestinationStateTest",
            "MockDestinationCatalog",
            "MockObjectStorageClient",
            "MockPathFactory"
        ]
)
class ObjectStorageDestinationStateTest {
    @Inject lateinit var stateManager: DestinationStateManager<ObjectStorageDestinationState>
    @Inject lateinit var mockClient: MockObjectStorageClient
    @Inject lateinit var pathFactory: MockPathFactory

    companion object {
        val stream1 = MockDestinationCatalogFactory.stream1
        const val PERSISTED =
            """{"generations_by_state":{"FINALIZED":{"0":{"key1":0,"key2":1},"1":{"key3":0,"key4":1}}}}"""
    }

    @Test
    fun testBasicLifecycle() = runTest {
        // TODO: Test fallback to generation id
        val state = stateManager.getState(stream1)
        Assertions.assertEquals(
            emptyList<ObjectStorageDestinationState.Generation>(),
            state.generations.toList(),
            "state should initially be empty"
        )
        state.addObject(0, "key1", 0)
        state.addObject(0, "key2", 1)
        state.addObject(1, "key3", 0)
        state.addObject(1, "key4", 1)
        Assertions.assertEquals(
            4,
            state.generations.flatMap { it.objects }.toList().size,
            "state should contain 4 objects"
        )

        stateManager.persistState(stream1)
        val obj = mockClient.list("").toList().first()
        val data = mockClient.get(obj.key) { it.readBytes() }
        Assertions.assertEquals(
            PERSISTED,
            data.toString(Charsets.UTF_8),
            "state should be persisted"
        )

        state.removeObject(0, "key1")
        state.removeObject(0, "key2")
        state.removeObject(1, "key3")
        state.removeObject(1, "key4")
        Assertions.assertEquals(
            emptyList<ObjectStorageDestinationState.ObjectAndPart>(),
            state.generations.flatMap { it.objects }.toList(),
            "objects should be removed"
        )

        val fetchedState = stateManager.getState(stream1)
        Assertions.assertEquals(
            0,
            fetchedState.generations.flatMap { it.objects }.toList().size,
            "state should still contain 0 objects (managed state is in cache)"
        )
    }

    @Test
    fun testLoadingExistingState() = runTest {
        val key =
            pathFactory
                .getStagingDirectory(stream1)
                .resolve(ObjectStorageStagingPersister.STATE_FILENAME)
                .toString()
        mockClient.put(key, PERSISTED.toByteArray())
        val state = stateManager.getState(stream1)
        Assertions.assertEquals(
            listOf(
                ObjectStorageDestinationState.Generation(
                    false,
                    0,
                    listOf(
                        ObjectStorageDestinationState.ObjectAndPart("key1", 0),
                        ObjectStorageDestinationState.ObjectAndPart("key2", 1)
                    )
                ),
                ObjectStorageDestinationState.Generation(
                    false,
                    1,
                    listOf(
                        ObjectStorageDestinationState.ObjectAndPart("key3", 0),
                        ObjectStorageDestinationState.ObjectAndPart("key4", 1)
                    )
                )
            ),
            state.generations.toList(),
            "state should be loaded from storage"
        )
    }
}
