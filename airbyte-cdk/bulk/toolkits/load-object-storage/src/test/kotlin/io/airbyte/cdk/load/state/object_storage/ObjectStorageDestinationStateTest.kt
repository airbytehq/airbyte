/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state.object_storage

import io.airbyte.cdk.load.MockObjectStorageClient
import io.airbyte.cdk.load.MockPathFactory
import io.airbyte.cdk.load.command.MockDestinationCatalogFactory
import io.airbyte.cdk.load.file.NoopProcessor
import io.airbyte.cdk.load.state.DestinationStateManager
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Property
import io.micronaut.context.annotation.Requires
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Singleton
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test

class ObjectStorageDestinationStateTest {
    @Singleton
    @Requires(env = ["ObjectStorageDestinationStateTest"])
    data class Dependencies(
        val stateManager: DestinationStateManager<ObjectStorageDestinationState>,
        val mockClient: MockObjectStorageClient,
        val pathFactory: MockPathFactory
    )

    companion object {
        val stream1 = MockDestinationCatalogFactory.stream1
        const val PERSISTED =
            """{"generations_by_state":{"FINALIZED":{"0":{"key1":0,"key2":1},"1":{"key3":0,"key4":1}}}}"""
    }

    @Singleton
    @Primary
    @Requires(property = "object-storage-destination-state-test.use-staging", value = "true")
    class MockPathFactoryWithStaging : MockPathFactory() {
        override var doSupportStaging = true
    }

    @Singleton
    @Primary
    @Requires(property = "object-storage-destination-state-test.use-staging", value = "false")
    class MockPathFactoryWithoutStaging : MockPathFactory() {
        override var doSupportStaging = false
    }

    @Nested
    @MicronautTest(
        rebuildContext = true,
        environments =
            [
                "ObjectStorageDestinationStateTest",
                "MockObjectStorageClient",
                "MockDestinationCatalog",
            ],
    )
    @Property(name = "object-storage-destination-state-test.use-staging", value = "true")
    inner class ObjectStorageDestinationStateTestStaging {
        @Test
        fun testBasicLifecycle(d: Dependencies) = runTest {
            // TODO: Test fallback to generation id
            val state = d.stateManager.getState(stream1)
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

            d.stateManager.persistState(stream1)
            val obj = d.mockClient.list("").toList().first()
            val data = d.mockClient.get(obj.key) { it.readBytes() }
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

            val fetchedState = d.stateManager.getState(stream1)
            Assertions.assertEquals(
                0,
                fetchedState.generations.flatMap { it.objects }.toList().size,
                "state should still contain 0 objects (managed state is in cache)"
            )
        }

        @Test
        fun testLoadingExistingState(d: Dependencies) = runTest {
            val key =
                d.pathFactory
                    .getStagingDirectory(stream1)
                    .resolve(ObjectStorageStagingPersister.STATE_FILENAME)
                    .toString()
            d.mockClient.put(key, PERSISTED.toByteArray())
            val state = d.stateManager.getState(stream1)
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

    @Nested
    @MicronautTest(
        environments =
            [
                "ObjectStorageDestinationStateTest",
                "MockObjectStorageClient",
                "MockDestinationCatalog",
            ],
    )
    @Property(name = "object-storage-destination-state-test.use-staging", value = "false")
    inner class ObjectStorageDestinationStateTestWithoutStaging {
        @Test
        fun testRecoveringFromMetadata(d: Dependencies) = runTest {
            val genIdKey = ObjectStorageDestinationState.METADATA_GENERATION_ID_KEY
            val prefix = d.pathFactory.prefix
            val generations =
                listOf(
                    Triple(0, "$prefix/key1-0", 0L),
                    Triple(0, "$prefix/key2-1", 1L),
                    Triple(1, "$prefix/key3-0", 0L),
                    Triple(1, "$prefix/key4-1", 1L)
                )
            generations.forEach { (genId, key, _) ->
                d.mockClient.streamingUpload(
                    key,
                    mapOf(genIdKey to genId.toString()),
                    NoopProcessor
                ) { it.write(0) }
            }
            val state = d.stateManager.getState(stream1)
            Assertions.assertEquals(
                generations
                    .groupBy { it.first }
                    .map { (generationId, triples) ->
                        ObjectStorageDestinationState.Generation(
                            false,
                            generationId.toLong(),
                            triples
                                .map { (_, key, partNumber) ->
                                    ObjectStorageDestinationState.ObjectAndPart(key, partNumber)
                                }
                                .sortedByDescending {
                                    // Brittle hack to get the order to line up
                                    it.key.contains("key2") || it.key.contains("key3")
                                }
                                .toMutableList()
                        )
                    },
                state.generations.toList(),
                "state should be recovered from metadata"
            )
        }
    }
}
