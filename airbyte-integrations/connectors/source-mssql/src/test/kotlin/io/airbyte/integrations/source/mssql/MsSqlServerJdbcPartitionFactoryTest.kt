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

        val msSqlServerJdbcPartitionFactory =
            MsSqlServerJdbcPartitionFactory(sharedState, selectQueryGenerator, config)
        val msSqlServerCdcJdbcPartitionFactory =
            MsSqlServerJdbcPartitionFactory(cdcSharedState, selectQueryGenerator, config)

        val fieldId = Field("id", IntFieldType)
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
        assertTrue(jdbcPartition is MsSqlServerJdbcNonResumableSnapshotWithCursorPartition)
    }

    @Test
    fun testResumeFromCompletedCursorBasedRead() {
        val incomingStateValue: OpaqueStateValue =
            Jsons.readTree(
                """
              {
              "cursor": "12345",
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
                  "version": 2,
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
                  "version": 2,
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
                      "version": 2,
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
            "version": 2,
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
                  "version": 2,
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
                configuredPrimaryKey = listOf(fieldId),
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
                configuredPrimaryKey = listOf(fieldId),
                configuredCursor = null,
            )

        val jdbcPartition =
            msSqlServerCdcJdbcPartitionFactory.create(streamFeedBootstrap(fullRefreshStream))
        assertTrue(jdbcPartition is MsSqlServerJdbcNonResumableSnapshotPartition)
    }
}
