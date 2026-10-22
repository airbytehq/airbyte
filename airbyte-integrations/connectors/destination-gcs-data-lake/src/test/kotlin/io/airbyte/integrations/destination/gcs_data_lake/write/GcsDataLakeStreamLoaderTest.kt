/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.write

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.ImportType
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
import io.airbyte.cdk.load.toolkits.iceberg.parquet.TableIdGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergDeleteMode
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.gcs_data_lake.catalog.GcsDataLakeCatalogUtil
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsCatalogConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.IcebergDeleteFileType
import io.airbyte.integrations.destination.gcs_data_lake.spec.PolarisCatalogConfiguration
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.runs
import io.mockk.slot
import kotlin.test.assertEquals
import kotlin.test.assertNotNull
import kotlin.test.assertNotSame
import kotlin.test.assertNull
import kotlinx.coroutines.runBlocking
import org.apache.iceberg.CatalogProperties
import org.apache.iceberg.PartitionSpec
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.TableProperties
import org.apache.iceberg.catalog.Catalog
import org.apache.iceberg.catalog.SupportsNamespaces
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.inmemory.InMemoryCatalog
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir

internal class GcsDataLakeStreamLoaderTest {
    private val streamStateStore: StreamStateStore<GcsDataLakeStreamState> = mockk(relaxed = true)

    @TempDir lateinit var warehouseDir: java.nio.file.Path

    private val tableIdentifier = TableIdentifier.of("namespace", "name")

    private lateinit var catalog: Catalog

    private fun makeStream(importType: ImportType, syncId: Long = 1): DestinationStream {
        val objectSchema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = true),
                    "name" to FieldType(StringType, nullable = true),
                ),
            )
        val inputSchema = objectSchema.properties
        return DestinationStream(
            generationId = 1,
            minimumGenerationId = 0,
            syncId = syncId,
            unmappedNamespace = "namespace",
            unmappedName = "name",
            namespaceMapper =
                NamespaceMapper(namespaceDefinitionType = NamespaceDefinitionType.SOURCE),
            tableSchema =
                StreamTableSchema(
                    columnSchema =
                        ColumnSchema(
                            inputSchema = inputSchema,
                            inputToFinalColumnNames = inputSchema.keys.associateWith { it },
                            finalSchema = mapOf(),
                        ),
                    importType = importType,
                    tableNames = TableNames(finalTableName = TableName("namespace", "name")),
                ),
        )
    }

    private fun makeConfiguration() =
        GcsDataLakeConfiguration(
            gcsBucketName = "bucket",
            serviceAccountJson = "{}",
            gcpProjectId = "project",
            gcpLocation = "us-central1",
            gcsEndpoint = "http://localhost:8080",
            namespace = "namespace",
            gcsCatalogConfiguration =
                GcsCatalogConfiguration(
                    warehouseLocation = "gs://bucket/",
                    mainBranchName = "main",
                    catalogConfiguration =
                        PolarisCatalogConfiguration(
                            serverUri = "http://localhost:8080/api/catalog",
                            catalogName = "test",
                            clientId = "client",
                            clientSecret = "secret",
                        ),
                ),
            icebergDeleteFileType = IcebergDeleteFileType.POSITIONAL,
        )

    private fun makeTableSchema(): Schema =
        ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = true),
                    "name" to FieldType(StringType, nullable = true),
                ),
            )
            .withAirbyteMeta(true)
            .toIcebergSchema(listOf(listOf("id")))

    private fun createTable(schema: Schema): Table {
        (catalog as SupportsNamespaces).createNamespace(tableIdentifier.namespace())
        return catalog
            .buildTable(tableIdentifier, schema)
            .withPartitionSpec(PartitionSpec.unpartitioned())
            .withProperty(TableProperties.FORMAT_VERSION, "2")
            .create()
    }

    private fun makeLoader(stream: DestinationStream, table: Table): GcsDataLakeStreamLoader {
        val gcsDataLakeCatalogUtil: GcsDataLakeCatalogUtil = mockk {
            every { createNamespace(any(), any()) } just runs
            every { toCatalogProperties(any()) } returns emptyMap()
        }
        val icebergUtil: IcebergUtil = mockk {
            every { createCatalog(any(), any()) } returns catalog
            every { createTable(any(), any(), any(), any()) } returns table
            every { toIcebergSchema(any()) } returns table.schema()
        }
        return GcsDataLakeStreamLoader(
            makeConfiguration(),
            stream,
            IcebergTableSynchronizer(
                IcebergTypesComparator(),
                IcebergSuperTypeFinder(IcebergTypesComparator()),
            ),
            gcsDataLakeCatalogUtil,
            icebergUtil,
            mockk<TableIdGenerator> {
                every { toTableIdentifier(any()) } returns tableIdentifier
            },
            stagingBranchName = "airbyte_staging_test",
            mainBranchName = "main",
            streamStateStore = streamStateStore,
        )
    }

    private fun startAndCaptureState(loader: GcsDataLakeStreamLoader): GcsDataLakeStreamState {
        val stateSlot = slot<GcsDataLakeStreamState>()
        every { streamStateStore.put(any(), capture(stateSlot)) } returns Unit
        runBlocking { loader.start() }
        return stateSlot.captured
    }

    @BeforeEach
    fun setup() {
        catalog = InMemoryCatalog()
        catalog.initialize(
            "test",
            mapOf(CatalogProperties.WAREHOUSE_LOCATION to warehouseDir.toString()),
        )
    }

    @Test
    fun `positional resolution state is not created for append streams`() {
        val table = createTable(makeTableSchema())

        val state = startAndCaptureState(makeLoader(makeStream(Append), table))

        assertEquals(IcebergDeleteMode.EQUALITY, state.deleteMode)
        assertNull(state.positionalDeleteState)
    }

    @Test
    fun `positional resolution state is created for dedupe streams`() {
        val table = createTable(makeTableSchema())
        val stream = makeStream(Dedupe(listOf(listOf("id")), listOf("id")))

        val state = startAndCaptureState(makeLoader(stream, table))

        assertNotNull(state.positionalDeleteState)
        assertEquals(
            IcebergDeleteMode.POSITIONAL,
            state.deleteMode,
        )
    }

    @Test
    fun `positional resolution state is scoped to each stream loader`() {
        val table = createTable(makeTableSchema())
        val importType = Dedupe(listOf(listOf("id")), listOf("id"))
        val firstState = startAndCaptureState(makeLoader(makeStream(importType), table))
        val secondState =
            startAndCaptureState(makeLoader(makeStream(importType, syncId = 2), table))

        assertNotSame(firstState.positionalDeleteState, secondState.positionalDeleteState)
    }
}
