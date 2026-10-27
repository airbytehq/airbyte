/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.write

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.command.Overwrite
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
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.BasePositionDeltaTaskWriter
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergDeleteMode
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergTableCommitter
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergTableWriterFactory
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.Operation
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.RecordWrapper
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.gcs_data_lake.catalog.GcsDataLakeCatalogUtil
import io.airbyte.integrations.destination.gcs_data_lake.spec.DEFAULT_STAGING_BRANCH
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsCatalogConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsPartitionFieldSpec
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsPartitionTransform
import io.airbyte.integrations.destination.gcs_data_lake.spec.IcebergDeleteFileType
import io.airbyte.integrations.destination.gcs_data_lake.spec.PolarisCatalogConfiguration
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.runs
import io.mockk.slot
import io.mockk.spyk
import kotlin.test.assertEquals
import kotlin.test.assertNotEquals
import kotlin.test.assertNotNull
import kotlin.test.assertNotSame
import kotlin.test.assertNull
import kotlin.test.assertTrue
import kotlinx.coroutines.runBlocking
import org.apache.iceberg.CatalogProperties
import org.apache.iceberg.DataFiles
import org.apache.iceberg.FileFormat
import org.apache.iceberg.PartitionSpec
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.TableProperties
import org.apache.iceberg.catalog.Catalog
import org.apache.iceberg.catalog.SupportsNamespaces
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.data.IcebergGenerics
import org.apache.iceberg.inmemory.InMemoryCatalog
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir

internal class GcsDataLakeStreamLoaderTest {
    private val streamStateStore: StreamStateStore<GcsDataLakeStreamState> = mockk(relaxed = true)

    @TempDir lateinit var warehouseDir: java.nio.file.Path

    private val tableIdentifier = TableIdentifier.of("namespace", "name")

    private lateinit var catalog: Catalog

    private fun makeStream(
        importType: ImportType,
        syncId: Long = 1,
        columnNames: Map<String, String> = emptyMap(),
        generationId: Long = 1,
        minimumGenerationId: Long = 0,
    ): DestinationStream {
        val objectSchema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = true),
                    "name" to FieldType(StringType, nullable = true),
                ),
            )
        val inputSchema = objectSchema.properties
        return DestinationStream(
            generationId = generationId,
            minimumGenerationId = minimumGenerationId,
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
                            inputToFinalColumnNames =
                                inputSchema.keys.associateWith { columnNames[it] ?: it },
                            finalSchema = mapOf(),
                        ),
                    importType = importType,
                    tableNames = TableNames(finalTableName = TableName("namespace", "name")),
                ),
        )
    }

    private fun makeConfiguration(
        mainBranchName: String = "main",
        partitionFields: List<GcsPartitionFieldSpec> = emptyList(),
    ) =
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
            icebergDeleteFileType = IcebergDeleteFileType.POSITIONAL,
            partitionFields = partitionFields,
        )

    private fun makeTableSchema(
        primaryKeys: List<List<String>> = listOf(listOf("id")),
        idFieldType: FieldType = FieldType(IntegerType, nullable = true),
    ): Schema =
        ObjectType(
                linkedMapOf(
                    "id" to idFieldType,
                    "name" to FieldType(StringType, nullable = true),
                ),
            )
            .withAirbyteMeta(true)
            .toIcebergSchema(primaryKeys)

    private fun createTable(
        schema: Schema,
        partitionSpec: PartitionSpec = PartitionSpec.unpartitioned(),
    ): Table {
        (catalog as SupportsNamespaces).createNamespace(tableIdentifier.namespace())
        return catalog
            .buildTable(tableIdentifier, schema)
            .withPartitionSpec(partitionSpec)
            .withProperty(TableProperties.FORMAT_VERSION, "2")
            .create()
    }

    private fun makeLoader(
        stream: DestinationStream,
        table: Table,
        mainBranchName: String = "main",
        incomingSchema: Schema = table.schema(),
        partitionFields: List<GcsPartitionFieldSpec> = emptyList(),
        onCreateTable: ((PartitionSpec) -> Table)? = null,
    ): GcsDataLakeStreamLoader {
        val gcsDataLakeCatalogUtil: GcsDataLakeCatalogUtil = mockk {
            every { createNamespace(any(), any()) } just runs
            every { toCatalogProperties(any()) } returns emptyMap()
        }
        val icebergUtil: IcebergUtil = mockk {
            every { createCatalog(any(), any()) } returns catalog
            every { createTable(any(), any(), any(), any(), any()) } answers
                {
                    onCreateTable?.invoke(arg<PartitionSpec>(4)) ?: table
                }
            every { constructGenerationIdSuffix(any<DestinationStream>()) } returns
                "test-generation-id-1-e"
            every { toIcebergSchema(any()) } returns incomingSchema
        }
        return GcsDataLakeStreamLoader(
            makeConfiguration(mainBranchName, partitionFields),
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

    private fun appendSnapshot(
        table: Table,
        branchName: String? = null,
    ) {
        val dataFile =
            DataFiles.builder(table.spec())
                .withPath(warehouseDir.resolve("data-${System.nanoTime()}.parquet").toString())
                .withFormat(FileFormat.PARQUET)
                .withFileSizeInBytes(1)
                .withRecordCount(1)
                .build()
        val append = table.newAppend()
        if (branchName != null) {
            append.toBranch(branchName)
        }
        append.appendFile(dataFile).commit()
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
    fun `optional primary key is required before setting identifier fields`() {
        val table =
            createTable(
                makeTableSchema(
                    primaryKeys = emptyList(),
                    idFieldType = FieldType(StringType, nullable = true),
                ),
            )
        assertTrue(table.schema().findField("id").isOptional)
        assertEquals(emptySet<Int>(), table.schema().identifierFieldIds())

        val stream = makeStream(Dedupe(listOf(listOf("id")), listOf("id")))
        val incomingSchema = makeTableSchema(idFieldType = FieldType(StringType, nullable = true))
        runBlocking {
            makeLoader(stream, table, incomingSchema = incomingSchema).start()
        }

        table.refresh()
        val idField = assertNotNull(table.schema().findField("id"))
        assertTrue(idField.isRequired)
        assertEquals(setOf(idField.fieldId()), table.schema().identifierFieldIds())
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

    @Test
    fun `second sync seeds staging from the configured main branch snapshot`() {
        val table = createTable(makeTableSchema())
        appendSnapshot(table)
        table.manageSnapshots().createBranch("prod").commit()

        val firstLoader = makeLoader(makeStream(Append), table, mainBranchName = "prod")
        runBlocking { firstLoader.start() }
        appendSnapshot(table, "airbyte_staging_test")
        runBlocking { firstLoader.teardown(completedSuccessfully = true) }

        val publishedSnapshotId = table.refs()["prod"]!!.snapshotId()
        val secondLoader =
            makeLoader(makeStream(Append, syncId = 2), table, mainBranchName = "prod")
        runBlocking { secondLoader.start() }

        assertEquals(
            publishedSnapshotId,
            table.refs()["airbyte_staging_test"]!!.snapshotId(),
        )
    }

    @Test
    fun `legacy staging branch seeds generated staging branch and is removed after publish`() {
        val table = createTable(makeTableSchema())
        appendSnapshot(table)
        table.manageSnapshots().createBranch("prod").commit()
        table.manageSnapshots().createBranch(DEFAULT_STAGING_BRANCH).commit()
        appendSnapshot(table, DEFAULT_STAGING_BRANCH)
        val legacySnapshotId = table.refs()[DEFAULT_STAGING_BRANCH]!!.snapshotId()

        val loader = makeLoader(makeStream(Append), table, mainBranchName = "prod")
        runBlocking { loader.start() }

        assertEquals(
            legacySnapshotId,
            table.refs()["airbyte_staging_test"]!!.snapshotId(),
        )
        runBlocking { loader.teardown(completedSuccessfully = true) }

        assertNull(table.refs()[DEFAULT_STAGING_BRANCH])
        assertEquals(legacySnapshotId, table.refs()["prod"]!!.snapshotId())
    }

    @Test
    fun `new table spec uses the mapped source column name`() {
        val table = createTable(makeTableSchema())
        catalog = spyk(catalog)
        every { catalog.tableExists(any()) } returns false
        var createdSpec: PartitionSpec? = null
        val fields =
            listOf(
                GcsPartitionFieldSpec(
                    column = "id",
                    transform = GcsPartitionTransform.IDENTITY,
                ),
            )
        val stream = makeStream(Append, columnNames = mapOf("id" to "mapped_id"))

        runBlocking {
            makeLoader(
                    stream,
                    table,
                    incomingSchema = makeTableSchema(),
                    partitionFields = fields,
                    onCreateTable = { spec ->
                        createdSpec = spec
                        table
                    },
                )
                .start()
        }

        assertEquals("mapped_id", createdSpec!!.fields().single().name())
    }

    @Test
    fun `stream filter excludes fields for other streams`() {
        val table = createTable(makeTableSchema())
        val fields =
            listOf(
                GcsPartitionFieldSpec(
                    column = "id",
                    transform = GcsPartitionTransform.IDENTITY,
                    streams = listOf("other_stream"),
                ),
            )

        runBlocking {
            makeLoader(makeStream(Append), table, partitionFields = fields).start()
        }

        assertTrue(table.spec().fields().isEmpty())
    }

    @Test
    fun `existing table evolves partition spec`() {
        val table = createTable(makeTableSchema())
        val fields =
            listOf(
                GcsPartitionFieldSpec(
                    column = "id",
                    transform = GcsPartitionTransform.IDENTITY,
                ),
            )

        runBlocking {
            makeLoader(makeStream(Append), table, partitionFields = fields).start()
        }

        assertEquals(listOf("identity"), table.spec().fields().map { it.transform().toString() })
    }

    @Test
    fun `overwrite removal defers partition evolution for deleted source column`() {
        val tableSchema = makeTableSchema()
        val table =
            createTable(
                tableSchema,
                PartitionSpec.builderFor(tableSchema).identity("name").build(),
            )
        val incomingSchema =
            ObjectType(linkedMapOf("id" to FieldType(IntegerType, nullable = true)))
                .withAirbyteMeta(true)
                .toIcebergSchema(listOf(listOf("id")))
        val partitionFields = listOf(GcsPartitionFieldSpec("name", GcsPartitionTransform.IDENTITY))
        val loader =
            makeLoader(
                makeStream(Overwrite, generationId = 1, minimumGenerationId = 1),
                table,
                incomingSchema = incomingSchema,
                partitionFields = partitionFields,
            )

        runBlocking {
            loader.start()
            loader.teardown(completedSuccessfully = true)
        }

        table.refresh()
        assertNull(table.schema().findField("name"))
        assertTrue(table.spec().fields().isEmpty())
    }

    @Test
    fun `partitioned positional dedupe writes latest row and references old spec`() {
        val schema =
            Schema(
                listOf(
                    org.apache.iceberg.types.Types.NestedField.required(
                        1,
                        "id",
                        org.apache.iceberg.types.Types.IntegerType.get(),
                    ),
                    org.apache.iceberg.types.Types.NestedField.required(
                        2,
                        "name",
                        org.apache.iceberg.types.Types.StringType.get(),
                    ),
                ),
                setOf(1),
            )
        (catalog as SupportsNamespaces).createNamespace(tableIdentifier.namespace())
        val table =
            catalog
                .buildTable(tableIdentifier, schema)
                .withPartitionSpec(PartitionSpec.unpartitioned())
                .withProperty(TableProperties.FORMAT_VERSION, "2")
                .create()
        fun record(name: String) =
            GenericRecord.create(schema).apply {
                setField("id", 42)
                setField("name", name)
            }
        val writerFactory = IcebergTableWriterFactory()
        val seedWriter = writerFactory.create(table, "ab-generation-id-0-e", Append, schema)
        seedWriter.write(record("old"))
        val seedResult = seedWriter.complete()
        val oldDataFile = seedResult.dataFiles().single()
        table.newAppend().apply { seedResult.dataFiles().forEach(::appendFile) }.commit()

        val fields =
            listOf(
                GcsPartitionFieldSpec("id", GcsPartitionTransform.IDENTITY),
            )
        val loader =
            makeLoader(
                makeStream(Dedupe(listOf(listOf("id")), emptyList())),
                table,
                incomingSchema = schema,
                partitionFields = fields,
            )
        val state = startAndCaptureState(loader)
        assertTrue(table.spec().isPartitioned)

        val writer =
            writerFactory.create(
                table,
                "ab-generation-id-1-e",
                Dedupe(listOf(listOf("id")), emptyList()),
                schema,
                positionalDeleteRef = state.stagingBranchName,
                positionalDeleteState = state.positionalDeleteState,
                deleteMode = state.deleteMode,
            ) as BasePositionDeltaTaskWriter
        writer.write(RecordWrapper(record("latest"), Operation.UPDATE))
        val result = writer.complete()
        val deleteFile = result.deleteFiles().single()
        assertEquals(oldDataFile.specId(), deleteFile.specId())
        assertEquals(oldDataFile.partition(), deleteFile.partition())
        assertNotEquals(oldDataFile.specId(), result.dataFiles().single().specId())

        IcebergTableCommitter.commit(
            table,
            state.stagingBranchName,
            result,
            table.refs()[state.stagingBranchName]!!.snapshotId(),
            emptySet(),
            writer.rewrittenDeleteFiles().toSet(),
            resolvesDeletes = true,
        )
        runBlocking { loader.teardown(completedSuccessfully = true) }
        val rows =
            IcebergGenerics.read(table).build().use { records ->
                records.map { it.getField("id").toString() to it.getField("name").toString() }
            }
        assertEquals(listOf("42" to "latest"), rows)
    }
}
