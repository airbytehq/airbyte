
package io.airbyte.integrations.destination.clickhouse.dataflow

import com.clickhouse.client.api.Client
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.write.StreamStateStore
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import org.mockito.kotlin.mock
import org.mockito.kotlin.whenever

class ClickhouseAggregateFactoryTest {

    @Test
    fun `test create`() {
        // 1. Setup
        val clickhouseClient = mock<Client>()
        val streamStateStore = mock<StreamStateStore<DirectLoadTableExecutionConfig>>()
        val factory = ClickhouseAggregateFactory(clickhouseClient, streamStateStore)
        val stream = DestinationStream(
            unmappedNamespace = "test_namespace",
            unmappedName = "test_stream",
            importType = io.airbyte.cdk.load.command.Append,
            schema = ObjectType(linkedMapOf<String, FieldType>()),
            generationId = 1,
            minimumGenerationId = 1,
            syncId = 1,
            namespaceMapper = NamespaceMapper.identity(),
        )
        val tableName = TableName("test_table")
        val config = DirectLoadTableExecutionConfig(tableName)

        whenever(streamStateStore.get(stream.mappedDescriptor)).thenReturn(config)

        // 2. Act
        val aggregate = factory.create(stream.mappedDescriptor) as ClickhouseAggregate

        // 3. Assert
        assertEquals(tableName.name, aggregate.buffer.tableName)
    }
}
