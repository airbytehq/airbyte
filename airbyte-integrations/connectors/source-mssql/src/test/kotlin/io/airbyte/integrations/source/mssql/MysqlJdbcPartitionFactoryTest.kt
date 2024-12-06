/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.read.*

class MysqlJdbcPartitionFactoryTest {
    /*
    companion object {
        private val selectQueryGenerator = MsSqlServerSelectQueryGenerator()
        private val sharedState = sharedState()
        private val cdcSharedState = sharedState(global = true)
        private val config = mockk<MsSqlServerSourceConfiguration>()

        val mysqlJdbcPartitionFactory =
            DefaultJdbcPartitionFactory(sharedState, selectQueryGenerator, config)
        val mysqlCdcJdbcPartitionFactory =
            DefaultJdbcPartitionFactory(cdcSharedState, selectQueryGenerator, config)

        val fieldId = Field("id", IntFieldType)
        val stream =
            Stream(
                id =
                    StreamIdentifier.from(
                        StreamDescriptor().withNamespace("test").withName("stream1")
                    ),
                schema = setOf(fieldId),
                configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
                configuredPrimaryKey = listOf(fieldId),
                configuredCursor = fieldId,
            )
        val timestampFieldId = Field("id2", OffsetDateTimeFieldType)

        val timestampStream =
            Stream(
                id =
                    StreamIdentifier.from(
                        StreamDescriptor().withNamespace("test").withName("stream2")
                    ),
                schema = setOf(timestampFieldId),
                configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
                configuredPrimaryKey = listOf(timestampFieldId),
                configuredCursor = timestampFieldId,
            )

        val binaryFieldId = Field("id3", BinaryStreamFieldType)

        val binaryStream =
            Stream(
                id =
                    StreamIdentifier.from(
                        StreamDescriptor().withNamespace("test").withName("stream3")
                    ),
                schema = setOf(binaryFieldId),
                configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
                configuredPrimaryKey = listOf(binaryFieldId),
                configuredCursor = binaryFieldId,
            )

        private fun sharedState(
            global: Boolean = false,
        ): DefaultJdbcSharedState {

            val configSpec =
                MsSqlServerSourceConfigurationSpecification().apply {
                    host = ""
                    port = 0
                    username = "foo"
                    password = "bar"
                    database = "localhost"
                }
            if (global) {
                configSpec.setMethodValue(CdcCursor())
            } else {
                configSpec.setMethodValue(UserDefinedCursor)
            }
            val configFactory = MsSqlServerSourceConfigurationFactory()
            val configuration = configFactory.make(configSpec)

            val mockSelectQuerier = mockk<SelectQuerier>()

            return DefaultJdbcSharedState(
                configuration,
                mockSelectQuerier,
                DefaultJdbcConstants(),
                ConcurrencyResource(configuration),
                NoOpGlobalLockResource()
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
                    },
                stateQuerier =
                    object : StateQuerier {
                        override val feeds: List<Feed> = listOf(stream)
                        override fun current(feed: Feed): OpaqueStateValue? =
                            if (feed == stream) incumbentStateValue else null
                    },
                stream,
            )
    }

    @Test
    fun testColdStartWithPkCursorBased() {
        val jdbcPartition = mysqlJdbcPartitionFactory.create(streamFeedBootstrap(stream))
        assertTrue(jdbcPartition is MysqlJdbcSnapshotWithCursorPartition)
    }

    @Test
    fun testColdStartWithPkCdc() {
        val jdbcPartition = mysqlCdcJdbcPartitionFactory.create(streamFeedBootstrap(stream))
        assertTrue(jdbcPartition is MysqlJdbcCdcSnapshotPartition)
    }

    @Test
    fun testColdStartWithoutPk() {
        val streamWithoutPk =
            Stream(
                id =
                    StreamIdentifier.from(
                        StreamDescriptor().withNamespace("test").withName("stream7")
                    ),
                schema = setOf(fieldId),
                configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
                configuredPrimaryKey = listOf(),
                configuredCursor = fieldId,
            )
        val jdbcPartition = mysqlJdbcPartitionFactory.create(streamFeedBootstrap(streamWithoutPk))
        assertTrue(jdbcPartition is MysqlJdbcNonResumableSnapshotWithCursorPartition)
    }

    @Test
    fun testResumeFromCompletedCursorBasedRead() {
        val incomingStateValue: OpaqueStateValue =
            Jsons.readTree(
                """
              {
              "cursor": "2",
              "version": 2,
              "state_type": "cursor_based",
              "stream_name": "stream1",
              "cursor_field": [
                "id"
              ],
              "stream_namespace": "test",
              "cursor_record_count": 1
              }
        """.trimIndent()
            )

        val jdbcPartition =
            mysqlJdbcPartitionFactory.create(streamFeedBootstrap(stream, incomingStateValue))
        assertTrue(jdbcPartition is MysqlJdbcCursorIncrementalPartition)
    }

    @Test
    fun testResumeFromCompletedCursorBasedReadTimestamp() {
        val incomingStateValue: OpaqueStateValue =
            Jsons.readTree(
                """
              {
                  "cursor": "2025-09-03T05:23:35",
                  "version": 2,
                  "state_type": "cursor_based",
                  "stream_name": "stream2",
                  "cursor_field": [
                    "id2"
                  ],
                  "stream_namespace": "test",
                  "cursor_record_count": 1
              }
        """.trimIndent()
            )

        val jdbcPartition =
            mysqlJdbcPartitionFactory.create(
                streamFeedBootstrap(timestampStream, incomingStateValue)
            )
        assertTrue(jdbcPartition is MysqlJdbcCursorIncrementalPartition)

        assertEquals(
            Jsons.valueToTree("2025-09-02T05:23:35.000000Z"),
            (jdbcPartition as MysqlJdbcCursorIncrementalPartition).cursorLowerBound
        )
    }

    @Test
    fun testResumeFromCursorBasedReadInitialRead() {
        val incomingStateValue: OpaqueStateValue =
            Jsons.readTree(
                """
                      {
                      "pk_val": "9063170",
                      "pk_name": "id",
                      "version": 2,
                      "state_type": "primary_key",
                      "incremental_state": {}
                      }
        """.trimIndent()
            )

        val jdbcPartition =
            mysqlJdbcPartitionFactory.create(streamFeedBootstrap(stream, incomingStateValue))

        assertTrue(jdbcPartition is MysqlJdbcSnapshotWithCursorPartition)
    }

    @Test
    fun testResumeFromCdcInitialRead() {
        val incomingStateValue: OpaqueStateValue =
            Jsons.readTree(
                """
            {
            "pk_val": "29999",
            "pk_name": "id",
            "version": 2,
            "state_type": "primary_key",
            "incremental_state": {}
            }
        """.trimIndent()
            )

        val jdbcPartition =
            mysqlCdcJdbcPartitionFactory.create(streamFeedBootstrap(stream, incomingStateValue))
        assertTrue(jdbcPartition is MysqlJdbcCdcSnapshotPartition)
    }

    @Test
    fun testResumeFromCdcInitialReadComplete() {
        val incomingStateValue: OpaqueStateValue =
            Jsons.readTree(
                """
        {
        "stream_name": "stream1",
        "cursor_field": [],
        "stream_namespace": "test"
        }
        """.trimIndent()
            )

        val jdbcPartition =
            mysqlCdcJdbcPartitionFactory.create(streamFeedBootstrap(stream, incomingStateValue))
        assertNull(jdbcPartition)
    }

    @Test
    fun testResumeFromCompletedCursorBasedReadBinary() {
        val incomingStateValue: OpaqueStateValue =
            Jsons.readTree(
                """
              {
                  "cursor": "OQAAAAAAAAAAAAAAAAAAAA==",
                  "version": 2,
                  "state_type": "cursor_based",
                  "stream_name": "stream3",
                  "cursor_field": [
                    "id3"
                  ],
                  "stream_namespace": "test",
                  "cursor_record_count": 1
              }
        """.trimIndent()
            )

        val jdbcPartition =
            mysqlJdbcPartitionFactory.create(streamFeedBootstrap(binaryStream, incomingStateValue))
        assertTrue(jdbcPartition is MysqlJdbcCursorIncrementalPartition)

        assertEquals(
            Jsons.valueToTree<BinaryNode>(Base64.getDecoder().decode("OQAAAAAAAAAAAAAAAAAAAA==")),
            (jdbcPartition as MysqlJdbcCursorIncrementalPartition).cursorLowerBound
        )
    }
     */
}
