/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.dataflow

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.DestinationStream.Descriptor
import io.airbyte.cdk.load.dataflow.aggregate.StoreKey
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.directload.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.schema.SnowflakeColumnManager
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.write.load.SnowflakeRawRecordFormatter
import io.airbyte.integrations.destination.snowflake.write.load.SnowflakeRecordFormatter
import io.airbyte.integrations.destination.snowflake.write.load.SnowflakeSchemaRecordFormatter
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Test

internal class SnowflakeAggregateFactoryTest {
    @Test
    fun testCreatingAggregateWithRawBuffer() {
        val descriptor = Descriptor(namespace = "namespace", name = "name")
        val tableName =
            TableName(
                namespace = descriptor.namespace!!,
                name = descriptor.name,
            )
        val directLoadTableExecutionConfig = DirectLoadTableExecutionConfig(tableName = tableName)
        val key = StoreKey(namespace = descriptor.namespace!!, name = descriptor.name)
        val streamStore = StreamStateStore<DirectLoadTableExecutionConfig>()
        streamStore.put(key, directLoadTableExecutionConfig)

        val stream = mockk<DestinationStream>(relaxed = true)
        val catalog = mockk<DestinationCatalog> { every { getStream(key) } returns stream }

        val snowflakeClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val snowflakeConfiguration =
            mockk<SnowflakeConfiguration> { every { legacyRawTablesOnly } returns true }
        val columnManager = SnowflakeColumnManager(snowflakeConfiguration)
        val snowflakeRecordFormatter: SnowflakeRecordFormatter = SnowflakeRawRecordFormatter()

        val factory =
            SnowflakeAggregateFactory(
                snowflakeClient = snowflakeClient,
                streamStateStore = streamStore,
                snowflakeConfiguration = snowflakeConfiguration,
                catalog = catalog,
                columnManager = columnManager,
                snowflakeRecordFormatter = snowflakeRecordFormatter,
            )
        val aggregate = factory.create(key)
        assertNotNull(aggregate)
        assertEquals(SnowflakeAggregate::class, aggregate::class)
    }

    @Test
    fun testCreatingAggregateWithStagingBuffer() {
        val descriptor = Descriptor(namespace = "namespace", name = "name")
        val tableName =
            TableName(
                namespace = descriptor.namespace!!,
                name = descriptor.name,
            )
        val directLoadTableExecutionConfig = DirectLoadTableExecutionConfig(tableName = tableName)
        val key = StoreKey(namespace = descriptor.namespace!!, name = descriptor.name)
        val streamStore = StreamStateStore<DirectLoadTableExecutionConfig>()
        streamStore.put(key, directLoadTableExecutionConfig)

        val stream = mockk<DestinationStream>(relaxed = true)
        val catalog = mockk<DestinationCatalog> { every { getStream(key) } returns stream }

        val snowflakeClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val snowflakeConfiguration =
            mockk<SnowflakeConfiguration> { every { legacyRawTablesOnly } returns false }
        val columnManager = SnowflakeColumnManager(snowflakeConfiguration)
        val snowflakeRecordFormatter: SnowflakeRecordFormatter = SnowflakeSchemaRecordFormatter()

        val factory =
            SnowflakeAggregateFactory(
                snowflakeClient = snowflakeClient,
                streamStateStore = streamStore,
                snowflakeConfiguration = snowflakeConfiguration,
                catalog = catalog,
                columnManager = columnManager,
                snowflakeRecordFormatter = snowflakeRecordFormatter,
            )
        val aggregate = factory.create(key)
        assertNotNull(aggregate)
        assertEquals(SnowflakeAggregate::class, aggregate::class)
    }
}
