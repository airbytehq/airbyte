/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake_g2.write

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.config.NamespaceDefinitionType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
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
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.tableFormatVersion
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.gcs_data_lake_g2.catalog.GcsDataLakeCatalogUtil
import io.airbyte.integrations.destination.gcs_data_lake_g2.spec.AllowNonReversibleUpgrades
import io.airbyte.integrations.destination.gcs_data_lake_g2.spec.GcsCatalogConfiguration
import io.airbyte.integrations.destination.gcs_data_lake_g2.spec.GcsDataLakeConfiguration
import io.airbyte.integrations.destination.gcs_data_lake_g2.spec.IcebergDeleteFileType
import io.airbyte.integrations.destination.gcs_data_lake_g2.spec.IcebergTableFormatVersion
import io.airbyte.integrations.destination.gcs_data_lake_g2.spec.PolarisCatalogConfiguration
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.runs
import io.mockk.slot
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertNotNull
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

internal class GcsDataLakeDeleteModeResolutionTest {

    private val streamStateStore: StreamStateStore<GcsDataLakeStreamState> = mockk(relaxed = true)

    @TempDir lateinit var warehouseDir: java.nio.file.Path

    private val tableIdentifier = TableIdentifier.of("namespace", "name")

    private lateinit var catalog: Catalog

    private fun makeStream(
        importType: ImportType = Dedupe(listOf(listOf("id")), listOf("id")),
    ): DestinationStream {
        val objectSchema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = true),
                    "name" to FieldType(io.airbyte.cdk.load.data.StringType, nullable = true),
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
            tableSchema =
                StreamTableSchema(
                    columnSchema =
                        ColumnSchema(
                            inputSchema = objectSchema.properties,
                            inputToFinalColumnNames =
                                objectSchema.properties.keys.associateWith { it },
                            finalSchema = mapOf(),
                        ),
                    importType = importType,
                    tableNames = TableNames(finalTableName = TableName("namespace", "name")),
                ),
        )
    }

    private fun makeConfiguration(
        deleteFileType: IcebergDeleteFileType = IcebergDeleteFileType.AUTOMATIC,
        formatVersion: IcebergTableFormatVersion = IcebergTableFormatVersion.V2,
        allowUpgrade: AllowNonReversibleUpgrades = AllowNonReversibleUpgrades.NO,
        mainBranchName: String = "main",
    ): GcsDataLakeConfiguration =
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
                    mainBranchName = mainBranchName,
                    catalogConfiguration =
                        PolarisCatalogConfiguration(
                            serverUri = "http://localhost:8080/api/catalog",
                            catalogName = "test",
                            clientId = "client",
                            clientSecret = "secret",
                        ),
                ),
            tableFormatVersion = formatVersion,
            icebergDeleteFileType = deleteFileType,
            allowNonReversibleUpgrades = allowUpgrade,
        )

    private fun icebergSchema(): Schema =
        ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = true),
                    "name" to FieldType(io.airbyte.cdk.load.data.StringType, nullable = true),
                ),
            )
            .withAirbyteMeta(true)
            .toIcebergSchema(listOf(listOf("id")))

    private fun createTableAt(version: Int, schema: Schema): Table {
        (catalog as SupportsNamespaces).createNamespace(tableIdentifier.namespace())
        val builder = catalog.buildTable(tableIdentifier, schema)
        return builder
            .withPartitionSpec(PartitionSpec.unpartitioned())
            .withProperty(TableProperties.FORMAT_VERSION, version.toString())
            .create()
    }

    private fun makeLoader(
        stream: DestinationStream,
        configuration: GcsDataLakeConfiguration,
        table: Table,
        mainBranchName: String = "main",
    ): GcsDataLakeStreamLoader {
        val gcsDataLakeCatalogUtil: GcsDataLakeCatalogUtil = mockk {
            every { createNamespace(any(), any()) } just runs
            every { toCatalogProperties(any()) } returns mapOf()
        }
        val icebergUtil: IcebergUtil = mockk {
            every { createCatalog(any(), any()) } returns catalog
            every { createTable(any(), any(), any(), any()) } returns table
            every { toIcebergSchema(any()) } returns table.schema()
        }
        return GcsDataLakeStreamLoader(
            configuration,
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
            mainBranchName = mainBranchName,
            streamStateStore = streamStateStore,
        )
    }

    private fun captureState(loader: GcsDataLakeStreamLoader): GcsDataLakeStreamState {
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
    fun `new v2 table resolves AUTOMATIC to EQUALITY`() {
        val stream = makeStream()
        val table = createTableAt(2, icebergSchema())
        val state = captureState(makeLoader(stream, makeConfiguration(), table))
        assertEquals(IcebergDeleteMode.EQUALITY, state.deleteMode)
        assertNull(state.positionalDeleteState)
    }

    @Test
    fun `new v3 table resolves AUTOMATIC to DELETION_VECTOR`() {
        val stream = makeStream()
        val table = createTableAt(3, icebergSchema())
        val state =
            captureState(
                makeLoader(
                    stream,
                    makeConfiguration(formatVersion = IcebergTableFormatVersion.V3),
                    table,
                ),
            )
        assertEquals(IcebergDeleteMode.DELETION_VECTOR, state.deleteMode)
        assertNotNull(state.positionalDeleteState)
    }

    @Test
    fun `existing v2 table targeting v3 with NO stays at v2`() {
        val stream = makeStream()
        val table = createTableAt(2, icebergSchema())
        val state =
            captureState(
                makeLoader(
                    stream,
                    makeConfiguration(formatVersion = IcebergTableFormatVersion.V3),
                    table,
                ),
            )
        assertEquals(IcebergDeleteMode.EQUALITY, state.deleteMode)
        assertEquals(2, tableFormatVersion(table))
    }

    @Test
    fun `existing v2 table targeting v3 with explicit DELETION_VECTOR and NO fails`() {
        val stream = makeStream()
        val table = createTableAt(2, icebergSchema())
        assertFailsWith<ConfigErrorException> {
            runBlocking {
                makeLoader(
                        stream,
                        makeConfiguration(
                            deleteFileType = IcebergDeleteFileType.DELETION_VECTOR,
                            formatVersion = IcebergTableFormatVersion.V3,
                        ),
                        table,
                    )
                    .start()
            }
        }
    }

    @Test
    fun `existing v2 table targeting v3 with YES upgrades and uses deletion vectors`() {
        val stream = makeStream()
        val table = createTableAt(2, icebergSchema())
        val state =
            captureState(
                makeLoader(
                    stream,
                    makeConfiguration(
                        formatVersion = IcebergTableFormatVersion.V3,
                        allowUpgrade = AllowNonReversibleUpgrades.YES,
                    ),
                    table,
                ),
            )
        assertEquals(IcebergDeleteMode.DELETION_VECTOR, state.deleteMode)
        table.refresh()
        assertEquals(3, tableFormatVersion(table))
    }

    @Test
    fun `existing v2 table targeting v3 with WITH_TABLE_BACKUP registers a v2 backup`() {
        val stream = makeStream()
        val table = createTableAt(2, icebergSchema())
        captureState(
            makeLoader(
                stream,
                makeConfiguration(
                    formatVersion = IcebergTableFormatVersion.V3,
                    allowUpgrade = AllowNonReversibleUpgrades.WITH_TABLE_BACKUP,
                ),
                table,
            ),
        )
        table.refresh()
        assertEquals(3, tableFormatVersion(table))
        val backups =
            catalog.listTables(tableIdentifier.namespace()).filter {
                it.name().startsWith("name_v2_backup_")
            }
        assertEquals(1, backups.size)
        val backup = catalog.loadTable(backups.single())
        assertEquals(2, tableFormatVersion(backup))
    }

    @Test
    fun `existing v3 table targeting v2 stays at v3`() {
        val stream = makeStream()
        val table = createTableAt(3, icebergSchema())
        val state = captureState(makeLoader(stream, makeConfiguration(), table))
        assertEquals(IcebergDeleteMode.DELETION_VECTOR, state.deleteMode)
    }

    @Test
    fun `append stream targeting v3 with YES also upgrades the existing v2 table`() {
        val stream = makeStream(Append)
        val table = createTableAt(2, icebergSchema())
        val state =
            captureState(
                makeLoader(
                    stream,
                    makeConfiguration(
                        formatVersion = IcebergTableFormatVersion.V3,
                        allowUpgrade = AllowNonReversibleUpgrades.YES,
                    ),
                    table,
                ),
            )
        assertEquals(IcebergDeleteMode.EQUALITY, state.deleteMode)
        table.refresh()
        assertEquals(3, tableFormatVersion(table))
    }

    @Test
    fun `explicit POSITIONAL on an existing v3 table fails at stream start`() {
        val stream = makeStream()
        val table = createTableAt(3, icebergSchema())
        assertFailsWith<ConfigErrorException> {
            runBlocking {
                makeLoader(
                        stream,
                        makeConfiguration(
                            deleteFileType = IcebergDeleteFileType.POSITIONAL,
                        ),
                        table,
                    )
                    .start()
            }
        }
    }

    @Test
    fun `explicit EQUALITY on an existing v3 table fails at stream start`() {
        val stream = makeStream()
        val table = createTableAt(3, icebergSchema())
        assertFailsWith<ConfigErrorException> {
            runBlocking {
                makeLoader(
                        stream,
                        makeConfiguration(
                            deleteFileType = IcebergDeleteFileType.EQUALITY,
                        ),
                        table,
                    )
                    .start()
            }
        }
    }

    @Test
    fun `explicit EQUALITY on a v2 table allowed to upgrade fails before any upgrade`() {
        val stream = makeStream()
        val table = createTableAt(2, icebergSchema())
        assertFailsWith<ConfigErrorException> {
            runBlocking {
                makeLoader(
                        stream,
                        makeConfiguration(
                            deleteFileType = IcebergDeleteFileType.EQUALITY,
                            formatVersion = IcebergTableFormatVersion.V3,
                            allowUpgrade = AllowNonReversibleUpgrades.YES,
                        ),
                        table,
                    )
                    .start()
            }
        }
        table.refresh()
        assertEquals(2, tableFormatVersion(table))
    }

    @Test
    fun `explicit POSITIONAL on a v2 table allowed to upgrade fails before any upgrade`() {
        val stream = makeStream()
        val table = createTableAt(2, icebergSchema())
        assertFailsWith<ConfigErrorException> {
            runBlocking {
                makeLoader(
                        stream,
                        makeConfiguration(
                            deleteFileType = IcebergDeleteFileType.POSITIONAL,
                            formatVersion = IcebergTableFormatVersion.V3,
                            allowUpgrade = AllowNonReversibleUpgrades.YES,
                        ),
                        table,
                    )
                    .start()
            }
        }
        table.refresh()
        assertEquals(2, tableFormatVersion(table))
    }

    @Test
    fun `check validation rejects EQUALITY with target v3`() {
        assertFailsWith<ConfigErrorException> {
            makeConfiguration(
                formatVersion = IcebergTableFormatVersion.V3,
                deleteFileType = IcebergDeleteFileType.EQUALITY,
            )
        }
    }

    @Test
    fun `upgrader is called with the configured main branch name`() {
        val stream = makeStream()
        val table = createTableAt(2, icebergSchema())
        table.manageSnapshots().createBranch("prod").commit()
        captureState(
            makeLoader(
                stream,
                makeConfiguration(
                    formatVersion = IcebergTableFormatVersion.V3,
                    allowUpgrade = AllowNonReversibleUpgrades.YES,
                    mainBranchName = "prod",
                ),
                table,
                mainBranchName = "prod",
            ),
        )
        table.refresh()
        assertEquals(3, tableFormatVersion(table))
    }

    @Test
    fun `check validation rejects POSITIONAL with target v3`() {
        assertFailsWith<ConfigErrorException> {
            makeConfiguration(
                formatVersion = IcebergTableFormatVersion.V3,
                deleteFileType = IcebergDeleteFileType.POSITIONAL,
            )
        }
    }

    @Test
    fun `check validation rejects DELETION_VECTOR with target v2`() {
        assertFailsWith<ConfigErrorException> {
            makeConfiguration(
                formatVersion = IcebergTableFormatVersion.V2,
                deleteFileType = IcebergDeleteFileType.DELETION_VECTOR,
            )
        }
    }
}
