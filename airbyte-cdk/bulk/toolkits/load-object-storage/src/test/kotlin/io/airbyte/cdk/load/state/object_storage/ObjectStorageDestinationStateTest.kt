/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state.object_storage

import io.airbyte.cdk.load.MockObjectStorageClient
import io.airbyte.cdk.load.MockPathFactory
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.MockDestinationCatalogFactory
import io.airbyte.cdk.load.file.NoopProcessor
import io.airbyte.cdk.load.state.DestinationStateManager
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Property
import io.micronaut.context.annotation.Requires
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Singleton
import java.nio.file.Paths
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
            """{"generations_by_state":{"FINALIZED":{"0":{"key1":0,"key2":1},"1":{"key3":0,"key4":1}}},"count_by_key":{}}"""
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
            val state = d.stateManager.getState(stream1)
            Assertions.assertEquals(
                emptyList<ObjectStorageDestinationState.Generation>(),
                state.getGenerations().toList(),
                "state should initially be empty"
            )
            state.addObject(0, "key1", 0)
            state.addObject(0, "key2", 1)
            state.addObject(1, "key3", 0)
            state.addObject(1, "key4", 1)
            Assertions.assertEquals(
                4,
                state.getGenerations().flatMap { it.objects }.toList().size,
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
                state.getGenerations().flatMap { it.objects }.toList(),
                "objects should be removed"
            )

            val fetchedState = d.stateManager.getState(stream1)
            Assertions.assertEquals(
                0,
                fetchedState.getGenerations().flatMap { it.objects }.toList().size,
                "state should still contain 0 objects (managed state is in cache)"
            )
        }

        @Test
        fun testLoadingExistingState(d: Dependencies) = runTest {
            val key =
                Paths.get(
                        d.pathFactory.getStagingDirectory(stream1),
                        ObjectStorageStagingPersister.STATE_FILENAME
                    )
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
                state.getGenerations().toList(),
                "state should be loaded from storage"
            )

            Assertions.assertEquals(2L, state.getNextPartNumber())
        }

        @Test
        fun testFallbackToMetadataState(d: Dependencies) = runTest {
            val generations =
                ObjectStorageDestinationStateTestWithoutStaging().loadMetadata(d, stream1)
            val state = d.stateManager.getState(stream1)
            ObjectStorageDestinationStateTestWithoutStaging().validateMetadata(state, generations)
            Assertions.assertEquals(2L, state.getNextPartNumber())
        }

        @Test
        fun testGetObjectsToMoveAndDelete(d: Dependencies) = runTest {
            val state = d.stateManager.getState(stream1)
            state.addObject(generationId = 0L, "old-finalized", partNumber = 0L, isStaging = false)
            state.addObject(generationId = 1L, "new-finalized", partNumber = 1L, isStaging = false)
            state.addObject(
                generationId = 0L,
                "leftover-old-staging",
                partNumber = 2L,
                isStaging = true
            )
            state.addObject(generationId = 1L, "new-staging", partNumber = 3L, isStaging = true)
            val toFinalize =
                state
                    .getStagedObjectsToFinalize(minimumGenerationId = 1L)
                    .map { it.first to it.second }
                    .toSet()

            Assertions.assertEquals(
                setOf(1L to ObjectStorageDestinationState.ObjectAndPart("new-staging", 3L)),
                toFinalize,
                "only new-staging should be finalized"
            )

            val toDelete =
                state
                    .getObjectsToDelete(minimumGenerationId = 1L)
                    .map { it.first to it.second }
                    .toSet()
            Assertions.assertEquals(
                setOf(
                    0L to ObjectStorageDestinationState.ObjectAndPart("old-finalized", 0L),
                    0L to ObjectStorageDestinationState.ObjectAndPart("leftover-old-staging", 2L)
                ),
                toDelete,
                "all old objects should be deleted"
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
        suspend fun loadMetadata(
            d: Dependencies,
            stream: DestinationStream
        ): List<Triple<Int, String, Long>> {
            val genIdKey = ObjectStorageDestinationState.METADATA_GENERATION_ID_KEY
            val prefix =
                "${d.pathFactory.finalPrefix}/${stream.descriptor.namespace}/${stream.descriptor.name}"
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
            return generations
        }

        fun validateMetadata(
            state: ObjectStorageDestinationState,
            generations: List<Triple<Int, String, Long>>
        ) = runTest {
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
                                    it.key.contains("key2") || it.key.contains("key4")
                                }
                                .toMutableList()
                        )
                    },
                state.getGenerations().toList().sortedBy { it.generationId },
                "state should be recovered from metadata"
            )
        }

        @Test
        fun testRecoveringFromMetadata(d: Dependencies) = runTest {
            val generations = loadMetadata(d, stream1)
            val state = d.stateManager.getState(stream1)
            validateMetadata(state, generations)
            Assertions.assertEquals(2L, state.getNextPartNumber())
        }
    }
}
