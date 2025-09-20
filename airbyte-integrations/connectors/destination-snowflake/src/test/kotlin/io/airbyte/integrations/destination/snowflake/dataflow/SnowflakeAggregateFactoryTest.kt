/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.dataflow

import io.airbyte.cdk.load.command.DestinationStream.Descriptor
import io.airbyte.cdk.load.dataflow.aggregate.StoreKey
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Test

internal class SnowflakeAggregateFactoryTest {
    @Test
    fun testCreatingAggregate() {
        val descriptor = Descriptor(namespace = "namespace", name = "name")
        val directLoadTableExecutionConfig =
            DirectLoadTableExecutionConfig(
                tableName =
                    TableName(
                        namespace = descriptor.namespace!!,
                        name = descriptor.name,
                    )
            )
        val key = StoreKey(namespace = descriptor.namespace!!, name = descriptor.name)
        val streamStore = StreamStateStore<DirectLoadTableExecutionConfig>()
        streamStore.put(descriptor, directLoadTableExecutionConfig)
        val snowflakeClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val factory = SnowflakeAggregateFactory(snowflakeClient, streamStore)
        val aggregate = factory.create(key)
        assertNotNull(aggregate)
        assertEquals(SnowflakeAggregate::class, aggregate::class)
    }
}
