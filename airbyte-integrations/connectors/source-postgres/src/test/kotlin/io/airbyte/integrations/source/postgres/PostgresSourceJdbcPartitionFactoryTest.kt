/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.ClockFactory
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.discover.MetaFieldDecorator
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.output.CatalogValidationFailureHandler
import io.airbyte.cdk.output.DataChannelFormat
import io.airbyte.cdk.output.DataChannelMedium
import io.airbyte.cdk.output.ResetStream
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.DefaultJdbcSharedState
import io.airbyte.cdk.read.StateManager
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.postgres.config.CdcIncrementalConfiguration
import io.airbyte.integrations.source.postgres.config.IncrementalConfiguration
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.airbyte.integrations.source.postgres.config.UserDefinedCursorIncrementalConfiguration
import io.airbyte.integrations.source.postgres.config.XminIncrementalConfiguration
import io.airbyte.integrations.source.postgres.ctid.Ctid
import io.airbyte.integrations.source.postgres.operations.PostgresSourceSelectQueryGenerator
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import java.time.OffsetDateTime
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class PostgresSourceJdbcPartitionFactoryTest {

    private lateinit var factory: PostgresSourceJdbcPartitionFactory
    private val testBlockSize = 8192L // Standard PostgreSQL block size

    @BeforeEach
    fun setup() {
        // Create mocked dependencies - we only need the factory instance to call
        // computePartitionBounds
        factory =
            PostgresSourceJdbcPartitionFactory(
                sharedState = mockk<DefaultJdbcSharedState>(),
                selectQueryGenerator = mockk<PostgresSourceSelectQueryGenerator>(),
                config = mockk<PostgresSourceConfiguration>(),
                handler = mockk<CatalogValidationFailureHandler>(),
                connectionFactory = mockk<PostgresSourceJdbcConnectionFactory>()
            )
    }

    @Test
    fun `computePartitionBounds with null lowerBound should start from Ctid ZERO`() {
        // Given: null lower bound, 4 partitions, 1MB relation size
        val lowerBound: JsonNode? = null
        val numPartitions = 4
        val relationSize = 1024L * 1024L // 1 MB

        // When
        val bounds =
            factory.computePartitionBounds(lowerBound, numPartitions, relationSize, testBlockSize)

        // Then
        assertEquals(4, bounds.size)

        // First partition should start from (0,0)
        assertEquals(Ctid.ZERO, bounds[0].first)
        assertEquals(Ctid(32, 1), bounds[0].second)

        // Subsequent partitions
        assertEquals(Ctid(32, 1), bounds[1].first)
        assertEquals(Ctid(64, 1), bounds[1].second)

        assertEquals(Ctid(64, 1), bounds[2].first)
        assertEquals(Ctid(96, 1), bounds[2].second)

        // Last partition's upper bound should be null (open-ended)
        assertEquals(Ctid(96, 1), bounds[3].first)
        assertNull(bounds[3].second)
    }

    @Test
    fun `computePartitionBounds with null JsonNode lowerBound should start from Ctid ZERO`() {
        // Given: JsonNode null lower bound
        val lowerBound: JsonNode = Jsons.nullNode()
        val numPartitions = 2
        val relationSize = 16384L // 2 blocks

        // When
        val bounds =
            factory.computePartitionBounds(lowerBound, numPartitions, relationSize, testBlockSize)

        // Then
        assertEquals(2, bounds.size)
        assertEquals(Ctid.ZERO, bounds[0].first)
        assertEquals(Ctid(1, 1), bounds[0].second)

        assertEquals(Ctid(1, 1), bounds[1].first)
        assertNull(bounds[1].second)
    }

    @Test
    fun `computePartitionBounds with empty string lowerBound should start from Ctid ZERO`() {
        // Given: empty string lower bound
        val lowerBound: JsonNode = Jsons.textNode("")
        val numPartitions = 3
        val relationSize = 24576L // 3 blocks

        // When
        val bounds =
            factory.computePartitionBounds(lowerBound, numPartitions, relationSize, testBlockSize)

        // Then
        assertEquals(3, bounds.size)
        assertEquals(Ctid.ZERO, bounds[0].first)
    }

    @Test
    fun `computePartitionBounds with valid Ctid string lowerBound`() {
        // Given: valid Ctid string lower bound
        val lowerBound: JsonNode = Jsons.textNode("(10,5)")
        val numPartitions = 2
        val relationSize = 163840L // 20 blocks

        // When
        val bounds =
            factory.computePartitionBounds(lowerBound, numPartitions, relationSize, testBlockSize)

        // Then
        assertEquals(2, bounds.size)

        // Should start from page 10
        assertEquals(Ctid(10, 5), bounds[0].first)
        assertEquals(Ctid(15, 1), bounds[0].second)

        assertEquals(Ctid(15, 1), bounds[1].first)
        assertNull(bounds[1].second)
    }

    @Test
    fun `computePartitionBounds should evenly distribute pages across partitions`() {
        // Given: 100 pages, 5 partitions
        val lowerBound: JsonNode? = null
        val numPartitions = 5
        val relationSize = 819200L // 100 blocks (100 * 8192)

        // When
        val bounds =
            factory.computePartitionBounds(lowerBound, numPartitions, relationSize, testBlockSize)

        // Then: each partition should get 20 pages (100 / 5)
        assertEquals(5, bounds.size)

        assertEquals(Ctid.ZERO, bounds[0].first)
        assertEquals(Ctid(20, 1), bounds[0].second)

        assertEquals(Ctid(20, 1), bounds[1].first)
        assertEquals(Ctid(40, 1), bounds[1].second)

        assertEquals(Ctid(40, 1), bounds[2].first)
        assertEquals(Ctid(60, 1), bounds[2].second)

        assertEquals(Ctid(60, 1), bounds[3].first)
        assertEquals(Ctid(80, 1), bounds[3].second)

        assertEquals(Ctid(80, 1), bounds[4].first)
        assertNull(bounds[4].second)
    }

    @Test
    fun `computePartitionBounds with single partition should return one open-ended range`() {
        // Given: single partition
        val lowerBound: JsonNode? = null
        val numPartitions = 1
        val relationSize = 81920L // 10 blocks

        // When
        val bounds =
            factory.computePartitionBounds(lowerBound, numPartitions, relationSize, testBlockSize)

        // Then
        assertEquals(1, bounds.size)
        assertEquals(Ctid.ZERO, bounds[0].first)
        assertNull(bounds[0].second)
    }

    @Test
    fun `computePartitionBounds should handle small relation size with many partitions`() {
        // Given: very small relation (1 block) with 10 partitions
        val lowerBound: JsonNode? = null
        val numPartitions = 10
        val relationSize = 8192L // 1 block

        // When
        val bounds =
            factory.computePartitionBounds(lowerBound, numPartitions, relationSize, testBlockSize)

        // Then: eachStep should be coerced to at least 1
        assertEquals(10, bounds.size)

        // Each partition should advance by 1 page (minimum step)
        assertEquals(Ctid.ZERO, bounds[0].first)
        assertEquals(Ctid(1, 1), bounds[0].second)

        assertEquals(Ctid(1, 1), bounds[1].first)
        assertEquals(Ctid(2, 1), bounds[1].second)

        // Last partition
        assertEquals(Ctid(9, 1), bounds[9].first)
        assertNull(bounds[9].second)
    }

    @Test
    fun `computePartitionBounds with large relation size`() {
        // Given: large relation (1GB), 10 partitions
        val lowerBound: JsonNode? = null
        val numPartitions = 10
        val relationSize = 1024L * 1024L * 1024L // 1 GB

        // When
        val bounds =
            factory.computePartitionBounds(lowerBound, numPartitions, relationSize, testBlockSize)

        // Then
        assertEquals(10, bounds.size)

        // 1GB / 8192 = 131072 pages
        // 131072 / 10 = 13107 pages per partition
        assertEquals(Ctid.ZERO, bounds[0].first)
        assertEquals(Ctid(13107, 1), bounds[0].second)

        assertEquals(Ctid(13107, 1), bounds[1].first)
        assertEquals(Ctid(26214, 1), bounds[1].second)

        assertEquals(Ctid(117963, 1), bounds[9].first)
        assertNull(bounds[9].second)
    }

    @Test
    fun `computePartitionBounds with non-zero lowerBound should calculate ranges from that point`() {
        // Given: starting from page 50, 100 total pages, 2 partitions
        val lowerBound: JsonNode = Jsons.textNode("(50,10)")
        val numPartitions = 2
        val relationSize = 819200L // 100 blocks total

        // When
        val bounds =
            factory.computePartitionBounds(lowerBound, numPartitions, relationSize, testBlockSize)

        // Then: should split the remaining 50 pages (100 - 50) into 2 partitions
        assertEquals(2, bounds.size)

        assertEquals(Ctid(50, 10), bounds[0].first)
        assertEquals(Ctid(75, 1), bounds[0].second) // 50 + (50/2)

        assertEquals(Ctid(75, 1), bounds[1].first)
        assertNull(bounds[1].second)
    }

    @Test
    fun `computePartitionBounds should ensure all partitions are sequential`() {
        // Given: arbitrary setup
        val lowerBound: JsonNode? = null
        val numPartitions = 7
        val relationSize = 573440L // 70 blocks

        // When
        val bounds =
            factory.computePartitionBounds(lowerBound, numPartitions, relationSize, testBlockSize)

        // Then: verify that each partition's upper bound matches the next partition's lower bound
        assertEquals(7, bounds.size)

        for (i in 0 until bounds.size - 1) {
            assertEquals(
                bounds[i].second,
                bounds[i + 1].first,
                "Partition $i upper bound should match partition ${i + 1} lower bound"
            )
        }

        // Last partition should be open-ended
        assertNull(bounds[bounds.size - 1].second)
    }

    @Test
    fun `computePartitionBounds with zero relation size should handle edge case`() {
        // Given: zero relation size
        val lowerBound: JsonNode? = null
        val numPartitions = 3
        val relationSize = 0L

        // When
        val bounds =
            factory.computePartitionBounds(lowerBound, numPartitions, relationSize, testBlockSize)

        // Then: theoretical last page is 0, step size should be coerced to 1
        assertEquals(3, bounds.size)

        assertEquals(Ctid.ZERO, bounds[0].first)
        assertEquals(Ctid(1, 1), bounds[0].second)

        assertEquals(Ctid(1, 1), bounds[1].first)
        assertEquals(Ctid(2, 1), bounds[1].second)

        assertEquals(Ctid(2, 1), bounds[2].first)
        assertNull(bounds[2].second)
    }

    @Test
    fun `computePartitionBounds should handle uneven division`() {
        // Given: 25 pages, 4 partitions (doesn't divide evenly)
        val lowerBound: JsonNode? = null
        val numPartitions = 4
        val relationSize = 204800L // 25 blocks

        // When
        val bounds =
            factory.computePartitionBounds(lowerBound, numPartitions, relationSize, testBlockSize)

        // Then: 25 / 4 = 6 pages per partition (integer division)
        assertEquals(4, bounds.size)

        assertEquals(Ctid.ZERO, bounds[0].first)
        assertEquals(Ctid(6, 1), bounds[0].second)

        assertEquals(Ctid(6, 1), bounds[1].first)
        assertEquals(Ctid(12, 1), bounds[1].second)

        assertEquals(Ctid(12, 1), bounds[2].first)
        assertEquals(Ctid(18, 1), bounds[2].second)

        // Last partition gets the remainder
        assertEquals(Ctid(18, 1), bounds[3].first)
        assertNull(bounds[3].second)
    }

    @Test
    fun `empty xmin incremental state should cold start outside global mode`() {
        val stream = stream(ConfiguredSyncMode.INCREMENTAL)
        val (partitionFactory, _) =
            partitionFactory(
                global = false,
                incrementalConfiguration = XminIncrementalConfiguration
            )

        val partition = partitionFactory.create(streamFeedBootstrap(stream, Jsons.objectNode()))

        assertTrue(partition is PostgresSourceJdbcUnsplittableSnapshotWithXminPartition)
    }

    @Test
    fun `empty xmin full refresh state should cold start outside global mode`() {
        val stream = stream(ConfiguredSyncMode.FULL_REFRESH)
        val (partitionFactory, _) =
            partitionFactory(
                global = false,
                incrementalConfiguration = XminIncrementalConfiguration
            )

        val partition = partitionFactory.create(streamFeedBootstrap(stream, Jsons.objectNode()))

        assertTrue(partition is PostgresSourceJdbcUnsplittableSnapshotPartition)
    }

    @Test
    fun `empty cursor incremental state should cold start without resetting stream`() {
        val stream = stream(ConfiguredSyncMode.INCREMENTAL)
        val (partitionFactory, handler) =
            partitionFactory(
                global = false,
                incrementalConfiguration = UserDefinedCursorIncrementalConfiguration
            )

        val partition = partitionFactory.create(streamFeedBootstrap(stream, Jsons.objectNode()))

        assertTrue(partition is PostgresSourceJdbcUnsplittableSnapshotWithCursorPartition)
        verify(exactly = 0) { handler.accept(any<ResetStream>()) }
    }

    @Test
    fun `empty cursor full refresh state should cold start outside global mode`() {
        val stream = stream(ConfiguredSyncMode.FULL_REFRESH)
        val (partitionFactory, _) =
            partitionFactory(
                global = false,
                incrementalConfiguration = UserDefinedCursorIncrementalConfiguration
            )

        val partition = partitionFactory.create(streamFeedBootstrap(stream, Jsons.objectNode()))

        assertTrue(partition is PostgresSourceJdbcUnsplittableSnapshotPartition)
    }

    @Test
    fun `JSON-null incremental states should remain complete`() {
        val stream = stream(ConfiguredSyncMode.INCREMENTAL)
        val (xminFactory, _) =
            partitionFactory(
                global = false,
                incrementalConfiguration = XminIncrementalConfiguration
            )
        val (cursorFactory, _) =
            partitionFactory(
                global = false,
                incrementalConfiguration = UserDefinedCursorIncrementalConfiguration
            )

        assertNull(xminFactory.create(streamFeedBootstrap(stream, Jsons.nullNode())))
        assertNull(cursorFactory.create(streamFeedBootstrap(stream, Jsons.nullNode())))
    }

    @Test
    fun `xmin incremental state should resume from its checkpoint`() {
        val stream = stream(ConfiguredSyncMode.INCREMENTAL)
        val (partitionFactory, _) =
            partitionFactory(
                global = false,
                incrementalConfiguration = XminIncrementalConfiguration
            )
        val state =
            PostgresSourceJdbcStreamStateValue.xminIncrementalCheckpoint(Jsons.numberNode(123))

        val partition = partitionFactory.create(streamFeedBootstrap(stream, state))

        assertTrue(partition is PostgresSourceJdbcXminIncrementalPartition)
        assertEquals(
            123,
            (partition as PostgresSourceJdbcXminIncrementalPartition).xminLowerBound?.asInt()
        )
    }

    @Test
    fun `completed xmin full refresh snapshot should remain complete`() {
        val stream = stream(ConfiguredSyncMode.FULL_REFRESH)
        val (partitionFactory, _) =
            partitionFactory(
                global = false,
                incrementalConfiguration = XminIncrementalConfiguration
            )

        assertNull(
            partitionFactory.create(
                streamFeedBootstrap(stream, PostgresSourceJdbcStreamStateValue.snapshotCompleted)
            )
        )
    }

    @Test
    fun `empty CDC stream state should remain complete`() {
        val stream = stream(ConfiguredSyncMode.INCREMENTAL)
        val (partitionFactory, _) =
            partitionFactory(
                global = true,
                incrementalConfiguration = mockk<CdcIncrementalConfiguration>(relaxed = true)
            )

        assertNull(partitionFactory.create(streamFeedBootstrap(stream, Jsons.objectNode())))
    }

    private fun partitionFactory(
        global: Boolean,
        incrementalConfiguration: IncrementalConfiguration,
    ): Pair<PostgresSourceJdbcPartitionFactory, CatalogValidationFailureHandler> {
        val config =
            mockk<PostgresSourceConfiguration> {
                every { this@mockk.global } returns global
                every { this@mockk.incrementalConfiguration } returns incrementalConfiguration
            }
        val handler = mockk<CatalogValidationFailureHandler>(relaxed = true)
        return PostgresSourceJdbcPartitionFactory(
            sharedState = mockk<DefaultJdbcSharedState>(relaxed = true),
            selectQueryGenerator = mockk<PostgresSourceSelectQueryGenerator>(relaxed = true),
            config = config,
            handler = handler,
            connectionFactory = mockk<PostgresSourceJdbcConnectionFactory>(relaxed = true)
        ) to handler
    }

    private fun stream(syncMode: ConfiguredSyncMode): Stream {
        val id = EmittedField("id", IntFieldType)
        return Stream(
            id =
                StreamIdentifier.from(
                    StreamDescriptor().withNamespace("public").withName("test_table")
                ),
            schema = setOf(id),
            configuredSyncMode = syncMode,
            configuredPrimaryKey = listOf(id),
            configuredCursor = id,
        )
    }

    private fun streamFeedBootstrap(stream: Stream, state: OpaqueStateValue?) =
        StreamFeedBootstrap(
            outputConsumer = BufferingOutputConsumer(ClockFactory().fixed()),
            metaFieldDecorator =
                object : MetaFieldDecorator {
                    override val globalCursor: MetaField? = null
                    override val globalMetaFields: Set<MetaField> = emptySet()

                    override fun decorateRecordData(
                        timestamp: OffsetDateTime,
                        globalStateValue: OpaqueStateValue?,
                        stream: Stream,
                        recordData: ObjectNode,
                    ) {}

                    override fun decorateRecordData(
                        timestamp: OffsetDateTime,
                        globalStateValue: OpaqueStateValue?,
                        stream: Stream,
                        recordData: NativeRecordPayload,
                    ) {}
                },
            stateManager = StateManager(initialStreamStates = mapOf(stream to state)),
            stream,
            DataChannelFormat.JSONL,
            DataChannelMedium.STDIO,
            8192,
            ClockFactory().fixed(),
        )
}
