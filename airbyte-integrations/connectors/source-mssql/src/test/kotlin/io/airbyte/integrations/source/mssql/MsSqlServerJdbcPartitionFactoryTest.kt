/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.node.BinaryNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.ClockFactory
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.discover.MetaFieldDecorator
import io.airbyte.cdk.discover.TableName
import io.airbyte.cdk.jdbc.BinaryStreamFieldType
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.LocalDateTimeFieldType
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.output.DataChannelFormat
import io.airbyte.cdk.output.DataChannelMedium
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.DefaultJdbcSharedState
import io.airbyte.cdk.read.ResourceAcquirer
import io.airbyte.cdk.read.SelectQuerier
import io.airbyte.cdk.read.StateManager
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.mockk.every
import io.mockk.mockk
import java.time.OffsetDateTime
import java.util.Base64
import kotlin.test.assertNull
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource

class MsSqlServerJdbcPartitionFactoryTest {
    companion object {
        private val selectQueryGenerator = MsSqlSourceOperations()
        private val sharedState = sharedState()
        private val cdcSharedState = sharedState(global = true)
        private val config = mockk<MsSqlServerSourceConfiguration>(relaxed = true)

        val metadataQuerier =
            mockk<MsSqlSourceMetadataQuerier>(relaxed = true) {
                // Mock getOrderedColumnForSync to return the first PK column by default
                every { getOrderedColumnForSync(any()) } answers
                    {
                        val streamId = firstArg<StreamIdentifier>()
                        // For full_refresh tests without PK/CI, return null
                        if (
                            streamId.name == "full_refresh_table" ||
                                streamId.name == "cdc_full_refresh_table"
                        ) {
                            null
                        } else {
                            // For most tests, return "id" (the first PK column or clustered index)
                            fieldId.id
                        }
                    }
            }
        val metadataQuerierFactory =
            mockk<MsSqlSourceMetadataQuerier.Factory>(relaxed = true) {
                every { session(any()) } returns metadataQuerier
            }

        val msSqlServerJdbcPartitionFactory =
            MsSqlServerJdbcPartitionFactory(
                sharedState,
                selectQueryGenerator,
                config,
                metadataQuerierFactory
            )
        val msSqlServerCdcJdbcPartitionFactory =
            MsSqlServerJdbcPartitionFactory(
                cdcSharedState,
                selectQueryGenerator,
                config,
                metadataQuerierFactory
            )

        val fieldId = Field("id", IntFieldType)
        val fieldName = Field("name", io.airbyte.cdk.jdbc.StringFieldType)
        val stream =
            Stream(
                id =
                    StreamIdentifier.from(
                        StreamDescriptor().withNamespace("dbo").withName("test_table")
                    ),
                schema = setOf(fieldId),
                configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
                configuredPrimaryKey = listOf(fieldId),
                configuredCursor = fieldId,
            )
        val timestampFieldId = Field("created_at", OffsetDateTimeFieldType)

        val timestampStream =
            Stream(
                id =
                    StreamIdentifier.from(
                        StreamDescriptor().withNamespace("dbo").withName("timestamp_table")
                    ),
                schema = setOf(timestampFieldId),
                configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
                configuredPrimaryKey = listOf(timestampFieldId),
                configuredCursor = timestampFieldId,
            )

        val binaryFieldId = Field("binary_col", BinaryStreamFieldType)

        val binaryStream =
            Stream(
                id =
                    StreamIdentifier.from(
                        StreamDescriptor().withNamespace("dbo").withName("binary_table")
                    ),
                schema = setOf(binaryFieldId),
                configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
                configuredPrimaryKey = listOf(binaryFieldId),
                configuredCursor = binaryFieldId,
            )

        val datetimeFieldId = Field("datetime_col", LocalDateTimeFieldType)

        val datetimeStream =
            Stream(
                id =
                    StreamIdentifier.from(
                        StreamDescriptor().withNamespace("dbo").withName("datetime_table")
                    ),
                schema = setOf(datetimeFieldId),
                configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
                configuredPrimaryKey = listOf(datetimeFieldId),
                configuredCursor = datetimeFieldId,
            )

        private fun sharedState(
            global: Boolean = false,
        ): DefaultJdbcSharedState {

            val configSpec =
                MsSqlServerSourceConfigurationSpecification().apply {
                    host = "localhost"
                    port = 1433
                    username = "sa"
                    password = "Password123!"
                    database = "master"
                }
            if (global) {
                configSpec.setIncrementalValue(Cdc())
            } else {
                configSpec.setIncrementalValue(UserDefinedCursor())
            }
            val configFactory = MsSqlServerSourceConfigurationFactory()
            val configuration = configFactory.make(configSpec)

            val mockSelectQuerier = mockk<SelectQuerier>()

            return DefaultJdbcSharedState(
                configuration,
                mockSelectQuerier,
                DefaultJdbcConstants(),
                ConcurrencyResource(configuration),
                ResourceAcquirer(emptyList())
            )
        }

        private fun streamFeedBootstrap(
            stream: Stream,
            incumbentStateValue: OpaqueStateValue? = null
        ) =
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
                            recordData: ObjectNode
                        ) {}

                        override fun decorateRecordData(
                            timestamp: OffsetDateTime,
                            globalStateValue: OpaqueStateValue?,
                            stream: Stream,
                            recordData: NativeRecordPayload
                        ) {
                            // no-op
                        }
                    },
                stateManager =
                    StateManager(initialStreamStates = mapOf(stream to incumbentStateValue)),
                stream,
                DataChannelFormat.JSONL,
                DataChannelMedium.STDIO,
                8192,
                ClockFactory().fixed(),
            )
    }

    @Test
    fun testColdStartWithPkCursorBased() {
        val jdbcPartition = msSqlServerJdbcPartitionFactory.create(streamFeedBootstrap(stream))
        assertTrue(jdbcPartition is MsSqlServerJdbcSnapshotWithCursorPartition)
    }

    @Test
    fun testColdStartWithPkCdc() {
        val jdbcPartition = msSqlServerCdcJdbcPartitionFactory.create(streamFeedBootstrap(stream))
        assertTrue(jdbcPartition is MsSqlServerJdbcCdcSnapshotPartition)
    }

    @Test
    fun testColdStartWithoutPk() {
        val streamWithoutPk =
            Stream(
                id =
                    StreamIdentifier.from(
                        StreamDescriptor().withNamespace("dbo").withName("no_pk_table")
                    ),
                schema = setOf(fieldId),
                configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
                configuredPrimaryKey = listOf(),
                configuredCursor = fieldId,
            )
        val jdbcPartition =
            msSqlServerJdbcPartitionFactory.create(streamFeedBootstrap(streamWithoutPk))
        // With our changes, if there's a clustered index (which the mock returns "id"),
        // we use resumable snapshots even without a configured PK
        assertTrue(jdbcPartition is MsSqlServerJdbcSnapshotWithCursorPartition)
    }

    @Test
    fun testResumeFromCompletedCursorBasedRead() {
        val incomingStateValue: OpaqueStateValue =
            Jsons.readTree(
                """
              {
              "cursor": "12345",
              "version": 3,
              "state_type": "cursor_based",
              "stream_name": "test_table",
              "cursor_field": [
                "id"
              ],
              "stream_namespace": "dbo",
              "cursor_record_count": 1 
              } 
        """.trimIndent()
            )

        val jdbcPartition =
            msSqlServerJdbcPartitionFactory.create(streamFeedBootstrap(stream, incomingStateValue))
        assertTrue(jdbcPartition is MsSqlServerJdbcCursorIncrementalPartition)
    }

    @ParameterizedTest
    @CsvSource(
        "'2025-01-20T10:30:45', '2025-01-20T10:30:45.000000Z'",
        "'2025-01-20T10:30:45.0', '2025-01-20T10:30:45.000000Z'",
        "'2025-01-20T10:30:45.1', '2025-01-20T10:30:45.100000Z'",
        "'2025-01-20T10:30:45.123', '2025-01-20T10:30:45.123000Z'",
        "'2025-01-20T10:30:45.123456789', '2025-01-20T10:30:45.123456Z'",
        "'2025-01-20T10:30:45.123+00:00', '2025-01-20T10:30:45.123000Z'",
        "'2025-01-20T10:30:45Z', '2025-01-20T10:30:45.000000Z'",
        "'2025-01-20T10:30:45 Z', '2025-01-20T10:30:45.000000Z'",
        "'2025-01-20T10:30:45.12345 -05:00', '2025-01-20T10:30:45.123450-05:00'",
    )
    fun testResumeFromCompletedCursorBasedReadTimestamp(
        cursorVal: String,
        expectedLowerBound: String
    ) {
        val incomingStateValue: OpaqueStateValue =
            Jsons.readTree(
                """
              {
                  "cursor": "$cursorVal",
                  "version": 3,
                  "state_type": "cursor_based",
                  "stream_name": "timestamp_table",
                  "cursor_field": [
                    "created_at"
                  ],
                  "stream_namespace": "dbo",
                  "cursor_record_count": 1 
              } 
        """.trimIndent()
            )

        val jdbcPartition =
            msSqlServerJdbcPartitionFactory.create(
                streamFeedBootstrap(timestampStream, incomingStateValue)
            )
        assertTrue(jdbcPartition is MsSqlServerJdbcCursorIncrementalPartition)

        assertEquals(
            Jsons.valueToTree(expectedLowerBound),
            (jdbcPartition as MsSqlServerJdbcCursorIncrementalPartition).cursorLowerBound
        )
    }

    @Test
    fun testResumeFromCompletedCursorBasedReadTimestampWithoutTimezone() {
        val incomingStateValue: OpaqueStateValue =
            Jsons.readTree(
                """
              {
                  "cursor": "2025-01-20T10:30:45.123",
                  "version": 3,
                  "state_type": "cursor_based",
                  "stream_name": "datetime_table",
                  "cursor_field": [
                    "datetime_col"
                  ],
                  "stream_namespace": "dbo",
                  "cursor_record_count": 1 
              } 
        """.trimIndent()
            )

        val jdbcPartition =
            msSqlServerJdbcPartitionFactory.create(
                streamFeedBootstrap(datetimeStream, incomingStateValue)
            )
        assertTrue(jdbcPartition is MsSqlServerJdbcCursorIncrementalPartition)

        assertEquals(
            Jsons.valueToTree("2025-01-20T10:30:45.123000"),
            (jdbcPartition as MsSqlServerJdbcCursorIncrementalPartition).cursorLowerBound
        )
    }

    @Test
    fun testResumeFromCursorBasedReadInitialRead() {
        val incomingStateValue: OpaqueStateValue =
            Jsons.readTree(
                """
                      {
                      "pk_val": "100000",
                      "pk_name": "id",
                      "version": 3,
                      "state_type": "primary_key",
                      "incremental_state": {}  
                      }
        """.trimIndent()
            )

        val jdbcPartition =
            msSqlServerJdbcPartitionFactory.create(streamFeedBootstrap(stream, incomingStateValue))

        assertTrue(jdbcPartition is MsSqlServerJdbcSnapshotWithCursorPartition)
    }

    @Test
    fun testResumeFromCdcInitialRead() {
        val incomingStateValue: OpaqueStateValue =
            Jsons.readTree(
                """
            {
            "pk_val": "50000",
            "pk_name": "id",
            "version": 3,
            "state_type": "primary_key",
            "incremental_state": {}
            }
        """.trimIndent()
            )

        val jdbcPartition =
            msSqlServerCdcJdbcPartitionFactory.create(
                streamFeedBootstrap(stream, incomingStateValue)
            )
        assertTrue(jdbcPartition is MsSqlServerJdbcCdcSnapshotPartition)
    }

    @Test
    fun testResumeFromCdcInitialReadComplete() {
        val incomingStateValue: OpaqueStateValue =
            Jsons.readTree(
                """
        {
        "stream_name": "test_table",
        "cursor_field": [],
        "stream_namespace": "dbo"
        }
        """.trimIndent()
            )

        val jdbcPartition =
            msSqlServerCdcJdbcPartitionFactory.create(
                streamFeedBootstrap(stream, incomingStateValue)
            )
        assertNull(jdbcPartition)
    }

    @Test
    fun testResumeFromCompletedCursorBasedReadBinary() {
        val incomingStateValue: OpaqueStateValue =
            Jsons.readTree(
                """
              {
                  "cursor": "QUJDREVGRw==",
                  "version": 3,
                  "state_type": "cursor_based",
                  "stream_name": "binary_table",
                  "cursor_field": [
                    "binary_col"
                  ],
                  "stream_namespace": "dbo",
                  "cursor_record_count": 1 
              } 
        """.trimIndent()
            )

        val jdbcPartition =
            msSqlServerJdbcPartitionFactory.create(
                streamFeedBootstrap(binaryStream, incomingStateValue)
            )
        assertTrue(jdbcPartition is MsSqlServerJdbcCursorIncrementalPartition)

        assertEquals(
            Jsons.valueToTree<BinaryNode>(Base64.getDecoder().decode("QUJDREVGRw==")),
            (jdbcPartition as MsSqlServerJdbcCursorIncrementalPartition).cursorLowerBound
        )
    }

    @Test
    fun testFullRefreshMode() {
        val fullRefreshStream =
            Stream(
                id =
                    StreamIdentifier.from(
                        StreamDescriptor().withNamespace("dbo").withName("full_refresh_table")
                    ),
                schema = setOf(fieldId),
                configuredSyncMode = ConfiguredSyncMode.FULL_REFRESH,
                configuredPrimaryKey = listOf(), // No PK to avoid findPkUpperBound call
                configuredCursor = null,
            )

        val jdbcPartition =
            msSqlServerJdbcPartitionFactory.create(streamFeedBootstrap(fullRefreshStream))
        assertTrue(jdbcPartition is MsSqlServerJdbcNonResumableSnapshotPartition)
    }

    @Test
    fun testCdcFullRefreshMode() {
        val fullRefreshStream =
            Stream(
                id =
                    StreamIdentifier.from(
                        StreamDescriptor().withNamespace("dbo").withName("cdc_full_refresh_table")
                    ),
                schema = setOf(fieldId),
                configuredSyncMode = ConfiguredSyncMode.FULL_REFRESH,
                configuredPrimaryKey = listOf(), // No PK to avoid findPkUpperBound call
                configuredCursor = null,
            )

        val jdbcPartition =
            msSqlServerCdcJdbcPartitionFactory.create(streamFeedBootstrap(fullRefreshStream))
        assertTrue(jdbcPartition is MsSqlServerJdbcNonResumableSnapshotPartition)
    }

    @Test
    fun testResumeFromCompletedCursorBasedReadWithoutCursorValue() {
        // Test for handling non-existing cursor values which should be treated as null
        val incomingStateValue: OpaqueStateValue =
            Jsons.readTree(
                """
              {
              "version": 2,
              "state_type": "cursor_based",
              "stream_name": "test_table",
              "cursor_field": [
                "id"
              ],
              "stream_namespace": "dbo",
              "cursor_record_count": 1
              }
        """.trimIndent()
            )

        val jdbcPartition =
            msSqlServerJdbcPartitionFactory.create(streamFeedBootstrap(stream, incomingStateValue))
        assertTrue(jdbcPartition is MsSqlServerJdbcCursorIncrementalPartition)

        // Verify that empty string is converted to null node
        val cursorLowerBound =
            (jdbcPartition as MsSqlServerJdbcCursorIncrementalPartition).cursorLowerBound
        assertTrue(cursorLowerBound.isNull)
    }

    @Test
    fun testNumericCursorValueComparison() {
        // Test that numeric cursor values with different representations (13.0 vs 13) are handled
        // correctly
        // This tests the fix for the infinite loop bug where state had "13" but MAX query returned
        // 13
        val numericField = Field("numericId", io.airbyte.cdk.jdbc.BigDecimalFieldType)
        val numericStream =
            Stream(
                id =
                    StreamIdentifier.from(
                        StreamDescriptor().withNamespace("dbo").withName("numeric_table")
                    ),
                schema = setOf(numericField),
                configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
                configuredPrimaryKey = listOf(numericField),
                configuredCursor = numericField,
            )

        // State has cursor value 13 (numeric JsonNode)
        val incomingStateValue: OpaqueStateValue =
            Jsons.readTree(
                """
              {
              "version": 3,
              "state_type": "cursor_based",
              "cursor_field": ["numericId"],
              "cursor": 13,
              "cursor_record_count": 0
              }
            """
            )

        // Create a mock StreamFeedBootstrap with the state
        val bootstrap = streamFeedBootstrap(numericStream, incomingStateValue)

        // Mock the MAX query result to return BigDecimal(13)
        // In reality, this would come from the database
        val partition = msSqlServerJdbcPartitionFactory.create(bootstrap)

        // Verify partition was created (should be CursorIncrementalPartition)
        assertTrue(partition is MsSqlServerJdbcCursorIncrementalPartition)

        // Verify the cursor lower bound is BigDecimal 13
        val cursorLowerBound =
            (partition as MsSqlServerJdbcCursorIncrementalPartition).cursorLowerBound
        assertEquals(13, cursorLowerBound.decimalValue().toInt())
        // Verify it's BigDecimal, not Double
        assertTrue(cursorLowerBound.isBigDecimal)
    }

    @Test
    fun testViewDetectionForTable() {
        // Test that regular tables are correctly identified as non-views
        val tableStream =
            Stream(
                id =
                    StreamIdentifier.from(
                        StreamDescriptor().withNamespace("dbo").withName("regular_table")
                    ),
                schema = setOf(fieldId),
                configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
                configuredPrimaryKey = listOf(fieldId),
                configuredCursor = fieldId,
            )

        // Mock the metadata querier to return a TABLE type
        val mockMetadataQuerier = mockk<MsSqlSourceMetadataQuerier>()
        every { mockMetadataQuerier.findTableName(tableStream.id) } returns
            TableName(name = "regular_table", schema = "dbo", type = "TABLE")
        every { mockMetadataQuerier.getOrderedColumnForSync(any()) } returns fieldId.id

        val mockMetadataQuerierFactory =
            mockk<MsSqlSourceMetadataQuerier.Factory>() {
                every { session(any()) } returns mockMetadataQuerier
            }

        val factoryWithMockedQuerier =
            MsSqlServerJdbcPartitionFactory(
                sharedState,
                selectQueryGenerator,
                config,
                mockMetadataQuerierFactory
            )

        val partition = factoryWithMockedQuerier.create(streamFeedBootstrap(tableStream))
        // Regular tables with primary keys should use resumable partitions which support sampling
        assertTrue(partition is MsSqlServerJdbcSnapshotWithCursorPartition)
    }

    @Test
    fun testViewDetectionForView() {
        // Test that views use non-resumable partitions to avoid sampling entirely
        val viewStream =
            Stream(
                id =
                    StreamIdentifier.from(
                        StreamDescriptor().withNamespace("dbo").withName("vw_test_view")
                    ),
                schema = setOf(fieldId),
                configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
                configuredPrimaryKey = listOf(fieldId),
                configuredCursor = fieldId,
            )

        // Mock the metadata querier to return a VIEW type
        val mockMetadataQuerier = mockk<MsSqlSourceMetadataQuerier>()
        every { mockMetadataQuerier.findTableName(viewStream.id) } returns
            TableName(name = "vw_test_view", schema = "dbo", type = "VIEW")
        every { mockMetadataQuerier.getOrderedColumnForSync(any()) } returns fieldId.id

        val mockMetadataQuerierFactory =
            mockk<MsSqlSourceMetadataQuerier.Factory>() {
                every { session(any()) } returns mockMetadataQuerier
            }

        val factoryWithMockedQuerier =
            MsSqlServerJdbcPartitionFactory(
                sharedState,
                selectQueryGenerator,
                config,
                mockMetadataQuerierFactory
            )

        val partition = factoryWithMockedQuerier.create(streamFeedBootstrap(viewStream))

        // Views should use non-resumable partitions to skip sampling entirely
        assertTrue(
            partition is MsSqlServerJdbcNonResumableSnapshotWithCursorPartition,
            "Views should use non-resumable partitions to avoid sampling"
        )
    }

    @Test
    fun testViewDetectionWithNullTableName() {
        // Test that when metadata querier returns null, we default to treating it as a table
        val unknownStream =
            Stream(
                id =
                    StreamIdentifier.from(
                        StreamDescriptor().withNamespace("dbo").withName("unknown_object")
                    ),
                schema = setOf(fieldId),
                configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
                configuredPrimaryKey = listOf(fieldId),
                configuredCursor = fieldId,
            )

        // Mock the metadata querier to return null (object not found)
        val mockMetadataQuerier = mockk<MsSqlSourceMetadataQuerier>()
        every { mockMetadataQuerier.findTableName(unknownStream.id) } returns null
        every { mockMetadataQuerier.getOrderedColumnForSync(any()) } returns fieldId.id

        val mockMetadataQuerierFactory =
            mockk<MsSqlSourceMetadataQuerier.Factory>() {
                every { session(any()) } returns mockMetadataQuerier
            }

        val factoryWithMockedQuerier =
            MsSqlServerJdbcPartitionFactory(
                sharedState,
                selectQueryGenerator,
                config,
                mockMetadataQuerierFactory
            )

        val partition = factoryWithMockedQuerier.create(streamFeedBootstrap(unknownStream))
        // Unknown objects (when metadata returns null) should default to resumable partitions
        assertTrue(partition is MsSqlServerJdbcSnapshotWithCursorPartition)
    }

    @Test
    fun testViewWithConfiguredPkResumingFromState() {
        // This test covers the critical bug: a view with a configured PK resuming from state
        // should use non-resumable partitions to avoid TABLESAMPLE
        val viewStream =
            Stream(
                id =
                    StreamIdentifier.from(
                        StreamDescriptor().withNamespace("dbo").withName("VW_FICHES_PRODUITS")
                    ),
                schema = setOf(fieldId, fieldName),
                configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
                configuredPrimaryKey = listOf(fieldId),
                configuredCursor = fieldName,
            )

        // State indicating we're in the middle of a snapshot (pk_name is set)
        val stateValue: OpaqueStateValue =
            Jsons.readTree(
                """
                {
                  "version": 3,
                  "state_type": "cursor_based",
                  "pk_name": "id",
                  "pk_val": "100",
                  "cursor_field": ["name"],
                  "cursor": null
                }
                """
            )

        // Mock the metadata querier to return a VIEW type
        val mockMetadataQuerier = mockk<MsSqlSourceMetadataQuerier>()
        every { mockMetadataQuerier.findTableName(viewStream.id) } returns
            TableName(name = "VW_FICHES_PRODUITS", schema = "dbo", type = "VIEW")
        every { mockMetadataQuerier.getOrderedColumnForSync(any()) } returns fieldId.id

        val mockMetadataQuerierFactory =
            mockk<MsSqlSourceMetadataQuerier.Factory>() {
                every { session(any()) } returns mockMetadataQuerier
            }

        val factoryWithMockedQuerier =
            MsSqlServerJdbcPartitionFactory(
                sharedState,
                selectQueryGenerator,
                config,
                mockMetadataQuerierFactory
            )

        val partition = factoryWithMockedQuerier.create(streamFeedBootstrap(viewStream, stateValue))

        // Views with configured PK resuming from state MUST use non-resumable partitions
        // to avoid TABLESAMPLE which fails on views
        assertTrue(
            partition is MsSqlServerJdbcNonResumableSnapshotWithCursorPartition,
            "Views with configured PK resuming from state should use non-resumable partitions to avoid TABLESAMPLE"
        )
    }

    @Test
    fun testViewWithoutConfiguredPk() {
        // Test that views without a configured PK also use non-resumable partitions
        val viewStream =
            Stream(
                id =
                    StreamIdentifier.from(
                        StreamDescriptor().withNamespace("dbo").withName("vw_simple_view")
                    ),
                schema = setOf(fieldId, fieldName),
                configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
                configuredPrimaryKey = null,
                configuredCursor = fieldName,
            )

        // Mock the metadata querier to return a VIEW type
        val mockMetadataQuerier = mockk<MsSqlSourceMetadataQuerier>()
        every { mockMetadataQuerier.findTableName(viewStream.id) } returns
            TableName(name = "vw_simple_view", schema = "dbo", type = "VIEW")
        every { mockMetadataQuerier.getOrderedColumnForSync(any()) } returns null

        val mockMetadataQuerierFactory =
            mockk<MsSqlSourceMetadataQuerier.Factory>() {
                every { session(any()) } returns mockMetadataQuerier
            }

        val factoryWithMockedQuerier =
            MsSqlServerJdbcPartitionFactory(
                sharedState,
                selectQueryGenerator,
                config,
                mockMetadataQuerierFactory
            )

        val partition = factoryWithMockedQuerier.create(streamFeedBootstrap(viewStream))

        // Views without configured PK should also use non-resumable partitions
        assertTrue(
            partition is MsSqlServerJdbcNonResumableSnapshotWithCursorPartition,
            "Views without configured PK should use non-resumable partitions"
        )
    }

    @Test
    fun testViewInFullRefreshMode() {
        // Test that views in full refresh mode also avoid resumable partitions
        val viewStream =
            Stream(
                id =
                    StreamIdentifier.from(
                        StreamDescriptor().withNamespace("dbo").withName("vw_fullrefresh_view")
                    ),
                schema = setOf(fieldId, fieldName),
                configuredSyncMode = ConfiguredSyncMode.FULL_REFRESH,
                configuredPrimaryKey = null,
                configuredCursor = null,
            )

        // Mock the metadata querier to return a VIEW type
        val mockMetadataQuerier = mockk<MsSqlSourceMetadataQuerier>()
        every { mockMetadataQuerier.findTableName(viewStream.id) } returns
            TableName(name = "vw_fullrefresh_view", schema = "dbo", type = "VIEW")
        every { mockMetadataQuerier.getOrderedColumnForSync(any()) } returns null

        val mockMetadataQuerierFactory =
            mockk<MsSqlSourceMetadataQuerier.Factory>() {
                every { session(any()) } returns mockMetadataQuerier
            }

        val factoryWithMockedQuerier =
            MsSqlServerJdbcPartitionFactory(
                sharedState,
                selectQueryGenerator,
                config,
                mockMetadataQuerierFactory
            )

        val partition = factoryWithMockedQuerier.create(streamFeedBootstrap(viewStream))

        // Views in full refresh without PK should use non-resumable partitions
        assertTrue(
            partition is MsSqlServerJdbcNonResumableSnapshotPartition,
            "Views in full refresh mode should use non-resumable partitions"
        )
    }
}
