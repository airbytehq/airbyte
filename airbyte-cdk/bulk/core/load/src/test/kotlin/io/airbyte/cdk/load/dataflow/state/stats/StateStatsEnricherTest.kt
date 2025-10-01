/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state.stats

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.dataflow.state.PartitionKey
import io.airbyte.cdk.load.dataflow.state.StateKey
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.GlobalCheckpoint
import io.airbyte.cdk.load.message.GlobalSnapshotCheckpoint
import io.airbyte.cdk.load.message.StreamCheckpoint
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import io.mockk.mockk
import io.mockk.verify
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
class StateStatsEnricherTest {

    @MockK private lateinit var statsStore: CommittedStatsStore

    @MockK private lateinit var namespaceMapper: NamespaceMapper

    private lateinit var stateStatsEnricher: StateStatsEnricher

    @BeforeEach
    fun setUp() {
        stateStatsEnricher = StateStatsEnricher(statsStore, namespaceMapper)
    }

    @Test
    fun `#enrich with StreamCheckpoint`() {
        val unmappedNamespace = "namespace"
        val unmappedName = "name"
        val mappedDescriptor = DestinationStream.Descriptor(unmappedNamespace, unmappedName)
        val checkpoint =
            CheckpointMessage.Checkpoint(
                unmappedNamespace = unmappedNamespace,
                unmappedName = unmappedName,
                state = null
            )
        val streamCheckpoint =
            StreamCheckpoint(
                checkpoint = checkpoint,
                sourceStats = CheckpointMessage.Stats(recordCount = 100),
                serializedSizeBytes = 1024
            )
        val stateKey = StateKey(id = 1L, partitionKeys = listOf(PartitionKey("partition1")))
        val commitStatsResult =
            CommitStatsResult(
                committedStats = EmissionStats(count = 50, bytes = 500),
                cumulativeStats = EmissionStats(count = 150, bytes = 1500)
            )

        every { namespaceMapper.map(unmappedNamespace, unmappedName) } returns mappedDescriptor
        every { statsStore.commitStats(mappedDescriptor, stateKey) } returns commitStatsResult

        val result = stateStatsEnricher.enrich(streamCheckpoint, stateKey)

        assertEquals(streamCheckpoint, result)
        assertEquals(150L, streamCheckpoint.totalRecords)
        assertEquals(1500L, streamCheckpoint.totalBytes)
        assertEquals(100L, streamCheckpoint.sourceStats?.recordCount)

        verify { namespaceMapper.map(unmappedNamespace, unmappedName) }
        verify { statsStore.commitStats(mappedDescriptor, stateKey) }
    }

    @Test
    fun `#enrich with GlobalCheckpoint`() {
        val checkpoint1 =
            CheckpointMessage.Checkpoint(
                unmappedNamespace = "namespace1",
                unmappedName = "name1",
                state = null
            )
        val checkpoint2 =
            CheckpointMessage.Checkpoint(
                unmappedNamespace = "namespace2",
                unmappedName = "name2",
                state = null
            )
        val globalCheckpoint =
            GlobalCheckpoint(
                state = null,
                sourceStats = CheckpointMessage.Stats(recordCount = 200),
                checkpoints = listOf(checkpoint1, checkpoint2),
                additionalProperties = emptyMap(),
                serializedSizeBytes = 2048
            )
        val stateKey =
            StateKey(
                id = 2L,
                partitionKeys = listOf(PartitionKey("partition1"), PartitionKey("partition2"))
            )

        val mappedDescriptor1 = DestinationStream.Descriptor("namespace1", "name1")
        val mappedDescriptor2 = DestinationStream.Descriptor("namespace2", "name2")

        val commitStatsResult1 =
            CommitStatsResult(
                committedStats = EmissionStats(count = 30, bytes = 300),
                cumulativeStats = EmissionStats(count = 100, bytes = 1000)
            )
        val commitStatsResult2 =
            CommitStatsResult(
                committedStats = EmissionStats(count = 70, bytes = 700),
                cumulativeStats = EmissionStats(count = 200, bytes = 2000)
            )

        every { namespaceMapper.map("namespace1", "name1") } returns mappedDescriptor1
        every { namespaceMapper.map("namespace2", "name2") } returns mappedDescriptor2
        every { statsStore.commitStats(mappedDescriptor1, stateKey) } returns commitStatsResult1
        every { statsStore.commitStats(mappedDescriptor2, stateKey) } returns commitStatsResult2

        val result = stateStatsEnricher.enrich(globalCheckpoint, stateKey)

        assertEquals(globalCheckpoint, result)
        assertEquals(300L, globalCheckpoint.totalRecords)
        assertEquals(3000L, globalCheckpoint.totalBytes)

        verify { namespaceMapper.map("namespace1", "name1") }
        verify { namespaceMapper.map("namespace2", "name2") }
        verify { statsStore.commitStats(mappedDescriptor1, stateKey) }
        verify { statsStore.commitStats(mappedDescriptor2, stateKey) }
    }

    @Test
    fun `#enrich with GlobalSnapshotCheckpoint`() {
        val checkpoint =
            CheckpointMessage.Checkpoint(
                unmappedNamespace = "namespace",
                unmappedName = "name",
                state = null
            )
        val globalSnapshotCheckpoint =
            GlobalSnapshotCheckpoint(
                state = null,
                sourceStats = CheckpointMessage.Stats(recordCount = 300),
                checkpoints = listOf(checkpoint),
                additionalProperties = emptyMap(),
                serializedSizeBytes = 3072,
                streamCheckpoints = emptyMap()
            )
        val stateKey = StateKey(id = 3L, partitionKeys = listOf(PartitionKey("partition3")))

        val mappedDescriptor = DestinationStream.Descriptor("namespace", "name")
        val commitStatsResult =
            CommitStatsResult(
                committedStats = EmissionStats(count = 150, bytes = 1500),
                cumulativeStats = EmissionStats(count = 450, bytes = 4500)
            )

        every { namespaceMapper.map("namespace", "name") } returns mappedDescriptor
        every { statsStore.commitStats(mappedDescriptor, stateKey) } returns commitStatsResult

        val result = stateStatsEnricher.enrich(globalSnapshotCheckpoint, stateKey)

        assertEquals(globalSnapshotCheckpoint, result)
        assertEquals(450L, globalSnapshotCheckpoint.totalRecords)
        assertEquals(4500L, globalSnapshotCheckpoint.totalBytes)

        verify { namespaceMapper.map("namespace", "name") }
        verify { statsStore.commitStats(mappedDescriptor, stateKey) }
    }

    @Test
    fun `#enrichTopLevelDestinationStats`() {
        val checkpoint = mockk<CheckpointMessage>(relaxed = true)
        val sourceStats = CheckpointMessage.Stats(recordCount = 100)
        every { checkpoint.sourceStats } returns sourceStats

        val result = stateStatsEnricher.enrichTopLevelDestinationStats(checkpoint, 50L)

        assertEquals(checkpoint, result)
        verify { checkpoint.updateStats(destinationStats = sourceStats) }
    }

    @Test
    fun `#enrichTopLevelStats`() {
        val checkpoint = mockk<CheckpointMessage>(relaxed = true)
        val stats = EmissionStats(count = 100, bytes = 1000)

        val result = stateStatsEnricher.enrichTopLevelStats(checkpoint, stats)

        assertEquals(checkpoint, result)
        verify { checkpoint.updateStats(totalRecords = 100, totalBytes = 1000) }
    }

    @Test
    fun `#enrichStreamState directly`() {
        val unmappedNamespace = "test-namespace"
        val unmappedName = "test-stream"
        val mappedDescriptor = DestinationStream.Descriptor(unmappedNamespace, unmappedName)
        val checkpoint =
            CheckpointMessage.Checkpoint(
                unmappedNamespace = unmappedNamespace,
                unmappedName = unmappedName,
                state = null
            )
        val streamCheckpoint = mockk<StreamCheckpoint>(relaxed = true)
        every { streamCheckpoint.checkpoint } returns checkpoint
        every { streamCheckpoint.sourceStats } returns CheckpointMessage.Stats(recordCount = 75)

        val stateKey = StateKey(id = 4L, partitionKeys = listOf(PartitionKey("partition4")))
        val commitStatsResult =
            CommitStatsResult(
                committedStats = EmissionStats(count = 25, bytes = 250),
                cumulativeStats = EmissionStats(count = 75, bytes = 750)
            )

        every { namespaceMapper.map(unmappedNamespace, unmappedName) } returns mappedDescriptor
        every { statsStore.commitStats(mappedDescriptor, stateKey) } returns commitStatsResult

        val result = stateStatsEnricher.enrichStreamState(streamCheckpoint, stateKey)

        assertEquals(streamCheckpoint, result)
        verify {
            streamCheckpoint.updateStats(
                destinationStats = any(),
                totalRecords = 75,
                totalBytes = 750
            )
        }
        verify { namespaceMapper.map(unmappedNamespace, unmappedName) }
        verify { statsStore.commitStats(mappedDescriptor, stateKey) }
    }

    @Test
    fun `#enrichGlobalState directly with multiple checkpoints`() {
        val checkpoint1 =
            mockk<CheckpointMessage.Checkpoint>(relaxed = true) {
                every { unmappedNamespace } returns null
                every { unmappedName } returns "stream1"
            }

        val checkpoint2 =
            mockk<CheckpointMessage.Checkpoint>(relaxed = true) {
                every { unmappedNamespace } returns "ns2"
                every { unmappedName } returns "stream2"
            }

        val stats = CheckpointMessage.Stats(recordCount = 500)
        val globalCheckpoint =
            mockk<CheckpointMessage>(relaxed = true) {
                every { checkpoints } returns listOf(checkpoint1, checkpoint2)
                every { sourceStats } returns stats
            }

        val stateKey =
            StateKey(id = 5L, partitionKeys = listOf(PartitionKey("p1"), PartitionKey("p2")))

        val mappedDescriptor1 = DestinationStream.Descriptor(null, "stream1")
        val mappedDescriptor2 = DestinationStream.Descriptor("ns2", "stream2")

        val commitStatsResult1 =
            CommitStatsResult(
                committedStats = EmissionStats(count = 100, bytes = 1000),
                cumulativeStats = EmissionStats(count = 300, bytes = 3000)
            )
        val commitStatsResult2 =
            CommitStatsResult(
                committedStats = EmissionStats(count = 200, bytes = 2000),
                cumulativeStats = EmissionStats(count = 600, bytes = 6000)
            )

        every { namespaceMapper.map(null, "stream1") } returns mappedDescriptor1
        every { namespaceMapper.map("ns2", "stream2") } returns mappedDescriptor2
        every { statsStore.commitStats(mappedDescriptor1, stateKey) } returns commitStatsResult1
        every { statsStore.commitStats(mappedDescriptor2, stateKey) } returns commitStatsResult2

        val result = stateStatsEnricher.enrichGlobalState(globalCheckpoint, stateKey)

        assertEquals(globalCheckpoint, result)
        verify { globalCheckpoint.updateStats(totalRecords = 900, totalBytes = 9000) }
        verify { globalCheckpoint.updateStats(destinationStats = stats) }
        verify { checkpoint1.updateStats(300, 3000) }
        verify { checkpoint2.updateStats(600, 6000) }
        verify { namespaceMapper.map(null, "stream1") }
        verify { namespaceMapper.map("ns2", "stream2") }
        verify { statsStore.commitStats(mappedDescriptor1, stateKey) }
        verify { statsStore.commitStats(mappedDescriptor2, stateKey) }
    }

    @Test
    fun `#enrichGlobalState with empty checkpoints list`() {
        val globalCheckpoint = mockk<CheckpointMessage>(relaxed = true)
        every { globalCheckpoint.checkpoints } returns emptyList()
        every { globalCheckpoint.sourceStats } returns CheckpointMessage.Stats(recordCount = 0)

        val stateKey = StateKey(id = 6L, partitionKeys = emptyList())

        val result = stateStatsEnricher.enrichGlobalState(globalCheckpoint, stateKey)

        assertEquals(globalCheckpoint, result)
        verify {
            globalCheckpoint.updateStats(destinationStats = any(), totalRecords = 0, totalBytes = 0)
        }
    }
}
