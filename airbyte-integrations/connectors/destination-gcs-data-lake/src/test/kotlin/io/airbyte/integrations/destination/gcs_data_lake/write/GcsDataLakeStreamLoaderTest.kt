/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.write

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.config.NamespaceDefinitionType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.iceberg.parquet.toIcebergSchema
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.cdk.load.toolkits.iceberg.parquet.IcebergSuperTypeFinder
import io.airbyte.cdk.load.toolkits.iceberg.parquet.IcebergTableSynchronizer
import io.airbyte.cdk.load.toolkits.iceberg.parquet.IcebergTypesComparator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.gcs_data_lake.catalog.GcsDataLakeCatalogUtil
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.MergeOnReadDeleteEncoding
import io.github.oshai.kotlinlogging.KotlinLogging
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.runs
import io.mockk.verify
import kotlinx.coroutines.runBlocking
import org.apache.iceberg.ManageSnapshots
import org.apache.iceberg.Schema
import org.apache.iceberg.SnapshotRef
import org.apache.iceberg.Table
import org.apache.iceberg.UpdateSchema
import org.apache.iceberg.catalog.Catalog
import org.junit.jupiter.api.Test

internal class GcsDataLakeStreamLoaderTest {
    private val streamStateStore = mockk<StreamStateStore<GcsDataLakeStreamState>>(relaxed = true)
    private val logger = KotlinLogging.logger {}

    @Test
    fun positionalDeletesOnlyApplyToDedupeStreams() {
        val objectSchema = objectSchema()
        val icebergSchema = objectSchema.withAirbyteMeta(true).toIcebergSchema(listOf(listOf("id")))
        val table = table(icebergSchema, emptyMap())

        startLoader(
            stream = stream(objectSchema, Append),
            table = table,
            schema = icebergSchema,
        )

        verify {
            streamStateStore.put(
                any(),
                match { it.positionalDeleteState == null },
            )
        }

        val dedupeStream =
            stream(
                objectSchema,
                Dedupe(primaryKey = listOf(listOf("id")), cursor = emptyList()),
            )
        startLoader(dedupeStream, table, icebergSchema)

        verify {
            streamStateStore.put(
                dedupeStream.mappedDescriptor,
                match { it.positionalDeleteState != null },
            )
        }
    }

    @Test
    fun positionalDeletesCreateStreamScopedResolutionState() {
        val objectSchema = objectSchema()
        val icebergSchema = objectSchema.withAirbyteMeta(true).toIcebergSchema(listOf(listOf("id")))
        val snapshotRef = mockk<SnapshotRef> { every { snapshotId() } returns 42L }
        val stream =
            stream(
                objectSchema,
                Dedupe(primaryKey = listOf(listOf("id")), cursor = emptyList()),
            )
        val table = table(icebergSchema, mapOf("airbyte_staging_test" to snapshotRef))
        startLoader(stream, table, icebergSchema)

        verify {
            streamStateStore.put(
                stream.mappedDescriptor,
                match { it.positionalDeleteState != null },
            )
        }
    }

    @Test
    fun deleteIndexRequiresSuppression() {
        val objectSchema = objectSchema()
        val icebergSchema = objectSchema.withAirbyteMeta(true).toIcebergSchema(listOf(listOf("id")))
        val table = table(icebergSchema, emptyMap())
        val stream =
            stream(
                objectSchema,
                Dedupe(primaryKey = listOf(listOf("id")), cursor = emptyList()),
            )

        startLoader(
            stream = stream,
            table = table,
            schema = icebergSchema,
            suppressDeletedPositions = false,
            indexPositionalDeletes = true,
        )

        verify {
            streamStateStore.put(
                stream.mappedDescriptor,
                match {
                    !it.suppressDeletedPositions &&
                        it.positionalDeleteState?.deleteIndex?.enabled == false
                },
            )
        }
    }

    @Test
    fun deleteIndexIsEnabledAlongsideSuppression() {
        val objectSchema = objectSchema()
        val icebergSchema = objectSchema.withAirbyteMeta(true).toIcebergSchema(listOf(listOf("id")))
        val table = table(icebergSchema, emptyMap())
        val stream =
            stream(
                objectSchema,
                Dedupe(primaryKey = listOf(listOf("id")), cursor = emptyList()),
            )

        startLoader(
            stream = stream,
            table = table,
            schema = icebergSchema,
            indexPositionalDeletes = true,
        )

        verify {
            streamStateStore.put(
                stream.mappedDescriptor,
                match { it.positionalDeleteState?.deleteIndex?.enabled == true },
            )
        }
    }

    private fun startLoader(
        stream: DestinationStream,
        table: Table,
        schema: Schema,
        suppressDeletedPositions: Boolean = true,
        indexPositionalDeletes: Boolean = false,
    ) {
        val configuration =
            mockk<GcsDataLakeConfiguration>(relaxed = true) {
                every { mergeOnReadDeleteEncoding } returns MergeOnReadDeleteEncoding.POSITIONAL
                every { this@mockk.suppressDeletedPositions } returns suppressDeletedPositions
                every { this@mockk.indexPositionalDeletes } returns indexPositionalDeletes
            }
        val catalog = mockk<Catalog>()
        val catalogUtil =
            mockk<GcsDataLakeCatalogUtil> {
                every { toCatalogProperties(any()) } returns emptyMap()
                every { createNamespace(any(), any()) } just runs
            }
        val icebergUtil =
            mockk<IcebergUtil> {
                every { createCatalog(any(), any()) } returns catalog
                every { createTable(any(), any(), any()) } returns table
                every { toIcebergSchema(any()) } returns schema
            }
        val loader =
            GcsDataLakeStreamLoader(
                icebergConfiguration = configuration,
                stream = stream,
                icebergTableSynchronizer =
                    IcebergTableSynchronizer(
                        IcebergTypesComparator(),
                        IcebergSuperTypeFinder(IcebergTypesComparator()),
                    ),
                gcsDataLakeCatalogUtil = catalogUtil,
                icebergUtil = icebergUtil,
                stagingBranchName = "airbyte_staging_test",
                mainBranchName = "main",
                streamStateStore = streamStateStore,
            )
        runBlocking { loader.start() }
    }

    private fun table(schema: Schema, refs: Map<String, SnapshotRef>): Table {
        val manageSnapshots = mockk<ManageSnapshots>(relaxed = true)
        every { manageSnapshots.createBranch(any()) } returns manageSnapshots
        every { manageSnapshots.commit() } just runs
        val updateSchema = mockk<UpdateSchema>(relaxed = true)
        every { updateSchema.apply() } returns schema
        every { updateSchema.commit() } just runs
        val table = mockk<Table>(relaxed = true)
        every { table.schema() } returns schema
        every { table.refs() } returns refs
        every { table.history() } returns listOf(mockk())
        every { table.manageSnapshots() } returns manageSnapshots
        every { table.updateSchema() } returns updateSchema
        every { table.refresh() } just runs
        return table
    }

    private fun stream(
        objectSchema: ObjectType,
        importType: io.airbyte.cdk.load.command.ImportType
    ) =
        DestinationStream(
            generationId = 1,
            minimumGenerationId = 0,
            syncId = logger.hashCode().toLong(),
            unmappedNamespace = "namespace",
            unmappedName = "name",
            namespaceMapper = NamespaceMapper(NamespaceDefinitionType.SOURCE),
            tableSchema =
                StreamTableSchema(
                    columnSchema =
                        ColumnSchema(
                            inputSchema = objectSchema.properties,
                            inputToFinalColumnNames =
                                objectSchema.properties.keys.associateWith { it },
                            finalSchema = emptyMap(),
                        ),
                    importType = importType,
                    tableNames = TableNames(finalTableName = TableName("namespace", "test")),
                ),
        )

    private fun objectSchema() =
        ObjectType(
            linkedMapOf(
                "id" to FieldType(IntegerType, nullable = false),
                "name" to FieldType(StringType, nullable = true),
            ),
        )
}
