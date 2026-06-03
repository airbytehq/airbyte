/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.dataflow

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.config.NamespaceDefinitionType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.iceberg.parquet.toIcebergSchema
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.airbyte.cdk.load.dataflow.aggregate.StoreKey
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergTableWriterFactory
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.s3_data_lake.write.S3DataLakeStreamState
import io.mockk.every
import io.mockk.mockk
import kotlin.test.assertEquals
import org.apache.iceberg.Table
import org.apache.iceberg.data.Record
import org.apache.iceberg.io.BaseTaskWriter
import org.junit.jupiter.api.Test

internal class S3DataLakeAggregateFactoryTest {
    @Test
    fun testAggregateUsesStagingBranchFromStreamState() {
        val key = StoreKey(namespace = "namespace", name = "name")
        val objectSchema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = true),
                ),
            )
        val stream =
            DestinationStream(
                generationId = 1,
                minimumGenerationId = 0,
                syncId = 1,
                unmappedNamespace = key.namespace,
                unmappedName = key.name,
                namespaceMapper =
                    NamespaceMapper(namespaceDefinitionType = NamespaceDefinitionType.SOURCE),
                tableSchema =
                    StreamTableSchema(
                        columnSchema =
                            ColumnSchema(
                                inputSchema = objectSchema.properties,
                                inputToFinalColumnNames =
                                    objectSchema.properties.keys.associateWith { it },
                                finalSchema = mapOf(),
                            ),
                        importType = Append,
                        tableNames = TableNames(finalTableName = TableName("namespace", "name")),
                    ),
            )
        val schema = objectSchema.withAirbyteMeta(true).toIcebergSchema(emptyList())
        val table: Table = mockk()
        val streamStateStore = StreamStateStore<S3DataLakeStreamState>()
        streamStateStore.put(
            key,
            S3DataLakeStreamState(
                table = table,
                schema = schema,
                stagingBranchName = "airbyte_staging_unique",
            ),
        )
        val writer: BaseTaskWriter<Record> = mockk()
        val icebergTableWriterFactory: IcebergTableWriterFactory = mockk {
            every { create(any(), any(), any(), any()) } returns writer
        }
        val icebergUtil: IcebergUtil = mockk {
            every { constructGenerationIdSuffix(stream) } returns "ab-generation-id-1-e"
        }

        val aggregate =
            S3DataLakeAggregateFactory(
                    catalog = DestinationCatalog(listOf(stream)),
                    streamStateStore = streamStateStore,
                    icebergTableWriterFactory = icebergTableWriterFactory,
                    icebergUtil = icebergUtil,
                )
                .create(key)

        val stagingBranchNameField =
            aggregate::class.java.getDeclaredField("stagingBranchName").apply {
                isAccessible = true
            }
        assertEquals("airbyte_staging_unique", stagingBranchNameField.get(aggregate))
    }
}
