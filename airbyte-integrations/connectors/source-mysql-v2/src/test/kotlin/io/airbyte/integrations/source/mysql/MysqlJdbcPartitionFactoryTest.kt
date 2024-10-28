/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.ClockFactory
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.DefaultJdbcSharedState
import io.airbyte.cdk.read.NoOpGlobalLockResource
import io.airbyte.cdk.read.SelectQuerier
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.mockk.mockk
import kotlin.test.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class MysqlJdbcPartitionFactoryTest {
    companion object {
        private val selectQueryGenerator = MysqlSourceOperations()
        private val sharedState = sharedState()
        private val cdcSharedState = sharedState(global = true)

        val mysqlJdbcPartitionFactory = MysqlJdbcPartitionFactory(sharedState, selectQueryGenerator)
        val mysqlCdcJdbcPartitionFactory =
            MysqlJdbcPartitionFactory(cdcSharedState, selectQueryGenerator)

        val fieldId = Field("id", IntFieldType)
        val stream =
            Stream(
                id =
                    StreamIdentifier.from(
                        StreamDescriptor().withNamespace("test").withName("stream1")
                    ),
                fields = listOf(fieldId),
                configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
                configuredPrimaryKey = listOf(fieldId),
                configuredCursor = fieldId,
            )

        private fun sharedState(
            global: Boolean = false,
        ): DefaultJdbcSharedState {

            val configSpec =
                MysqlSourceConfigurationSpecification().apply {
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
            val configFactory = MysqlSourceConfigurationFactory()
            val configuration = configFactory.make(configSpec)

            val mockSelectQuerier = mockk<SelectQuerier>()

            return DefaultJdbcSharedState(
                configuration,
                BufferingOutputConsumer(ClockFactory().fixed()),
                mockSelectQuerier,
                DefaultJdbcConstants(),
                ConcurrencyResource(configuration),
                NoOpGlobalLockResource()
            )
        }
    }

    @Test
    fun testColdStartWithPkCursorBased() {
        val jdbcPartition = mysqlJdbcPartitionFactory.create(stream, null)
        assertTrue(jdbcPartition is MysqlJdbcSnapshotWithCursorPartition)
    }

    @Test
    fun testColdStartWithPkCdc() {
        val jdbcPartition = mysqlCdcJdbcPartitionFactory.create(stream, null)
        assertTrue(jdbcPartition is MysqlJdbcCdcSnapshotPartition)
    }

    @Test
    fun testColdStartWithoutPk() {
        val streamWithoutPk =
            Stream(
                id =
                    StreamIdentifier.from(
                        StreamDescriptor().withNamespace("test").withName("stream2")
                    ),
                fields = listOf(fieldId),
                configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
                configuredPrimaryKey = listOf(),
                configuredCursor = fieldId,
            )
        val jdbcPartition = mysqlJdbcPartitionFactory.create(streamWithoutPk, null)
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

        val jdbcPartition = mysqlJdbcPartitionFactory.create(stream, incomingStateValue)
        assertTrue(jdbcPartition is MysqlJdbcCursorIncrementalPartition)
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

        val jdbcPartition = mysqlJdbcPartitionFactory.create(stream, incomingStateValue)

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

        val jdbcPartition = mysqlCdcJdbcPartitionFactory.create(stream, incomingStateValue)
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

        val jdbcPartition = mysqlCdcJdbcPartitionFactory.create(stream, incomingStateValue)
        assertNull(jdbcPartition)
    }
}
