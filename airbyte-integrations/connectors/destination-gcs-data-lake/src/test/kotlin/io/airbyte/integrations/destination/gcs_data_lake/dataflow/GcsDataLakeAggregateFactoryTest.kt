/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.dataflow

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.config.NamespaceDefinitionType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergTableWriterFactory
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.gcs_data_lake.write.GcsDataLakeStreamState
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.runs
import io.mockk.verify
import kotlinx.coroutines.runBlocking
import org.apache.iceberg.AppendFiles
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.data.Record
import org.apache.iceberg.io.BaseTaskWriter
import org.apache.iceberg.io.WriteResult
import org.apache.iceberg.types.Types
import org.junit.jupiter.api.Test

internal class GcsDataLakeAggregateFactoryTest {
    @Test
    fun testCreateUsesStreamStateStagingBranch() {
        val stagingBranchName = "airbyte_staging_unique"
        val stream = makeStream()
        val schema =
            Schema(
                Types.NestedField.optional(1, "id", Types.LongType.get()),
                Types.NestedField.optional(2, "name", Types.StringType.get()),
            )
        val table: Table = mockk { every { newAppend() } returns mockk<AppendFiles>() }
        val append: AppendFiles = mockk {
            every { toBranch(stagingBranchName) } returns this
            every { commit() } just runs
        }
        every { table.newAppend() } returns append
        val writer: BaseTaskWriter<Record> = mockk {
            every { complete() } returns
                WriteResult.builder().addDataFiles(emptyList()).addDeleteFiles(emptyList()).build()
            every { close() } just runs
        }
        val streamStateStore = StreamStateStore<GcsDataLakeStreamState>()
        streamStateStore.put(
            stream.mappedDescriptor,
            GcsDataLakeStreamState(table, schema, stagingBranchName),
        )
        val icebergUtil: IcebergUtil = mockk {
            every { constructGenerationIdSuffix(stream) } returns "ab-generation-id-1-e"
        }
        val writerFactory: IcebergTableWriterFactory = mockk {
            every {
                create(
                    table = table,
                    generationId = "ab-generation-id-1-e",
                    importType = Append,
                    schema = schema,
                )
            } returns writer
        }
        val aggregateFactory =
            GcsDataLakeAggregateFactory(
                catalog = DestinationCatalog(listOf(stream)),
                streamStateStore = streamStateStore,
                icebergTableWriterFactory = writerFactory,
                icebergUtil = icebergUtil,
            )

        val aggregate = aggregateFactory.create(stream.mappedDescriptor)
        runBlocking { aggregate.flush() }

        verify { append.toBranch(stagingBranchName) }
    }

    private fun makeStream(): DestinationStream {
        val objectSchema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = true),
                    "name" to FieldType(StringType, nullable = true),
                ),
            )
        return DestinationStream(
            generationId = 1,
            minimumGenerationId = 0,
            syncId = 1,
            unmappedNamespace = "namespace",
            unmappedName = "name",
            namespaceMapper =
                NamespaceMapper(namespaceDefinitionType = NamespaceDefinitionType.SOURCE),
            tableSchema = makeTableSchema(objectSchema, Append),
        )
    }

    private fun makeTableSchema(schema: ObjectType, importType: ImportType): StreamTableSchema {
        val inputSchema = schema.properties
        return StreamTableSchema(
            columnSchema =
                ColumnSchema(
                    inputSchema = inputSchema,
                    inputToFinalColumnNames = inputSchema.keys.associateWith { it },
                    finalSchema = mapOf(),
                ),
            importType = importType,
            tableNames = TableNames(finalTableName = TableName("namespace", "test")),
        )
    }
}
