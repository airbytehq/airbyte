/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.write

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.IcebergCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.NessieCatalogConfiguration
import io.airbyte.cdk.load.config.NamespaceDefinitionType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.iceberg.parquet.toIcebergSchema
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.cdk.load.toolkits.iceberg.parquet.ColumnTypeChangeBehavior
import io.airbyte.cdk.load.toolkits.iceberg.parquet.IcebergSuperTypeFinder
import io.airbyte.cdk.load.toolkits.iceberg.parquet.IcebergTableSynchronizer
import io.airbyte.cdk.load.toolkits.iceberg.parquet.IcebergTypesComparator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.s3_data_lake.catalog.S3DataLakeUtil
import io.airbyte.integrations.destination.s3_data_lake.spec.DEFAULT_STAGING_BRANCH
import io.airbyte.integrations.destination.s3_data_lake.spec.S3BucketConfiguration

import io.airbyte.integrations.destination.s3_data_lake.spec.S3DataLakeConfiguration
import io.airbyte.integrations.destination.s3_data_lake.spec.generateStagingBranchName
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.just
import io.mockk.mockk
import io.mockk.runs
import io.mockk.verify
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertNotEquals
import kotlin.test.assertTrue
import kotlinx.coroutines.runBlocking
import org.apache.iceberg.ManageSnapshots
import org.apache.iceberg.Schema
import org.apache.iceberg.SortOrder
import org.apache.iceberg.Table
import org.apache.iceberg.UpdateSchema
import org.apache.iceberg.catalog.Catalog
import org.apache.iceberg.io.CloseableIterable
import org.apache.iceberg.types.Type
import org.apache.iceberg.types.Types
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class S3DataLakeStreamLoaderTest {
    @MockK(relaxed = true)
    private lateinit var streamStateStore: StreamStateStore<S3DataLakeStreamState>

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

    private val emptyTableSchema =
        StreamTableSchema(
            columnSchema =
                ColumnSchema(
                    inputSchema = mapOf(),
                    inputToFinalColumnNames = mapOf(),
                    finalSchema = mapOf(),
                ),
            importType = Append,
            tableNames = TableNames(finalTableName = TableName("namespace", "test")),
        )

    @BeforeEach
    fun setup() {
        every { streamStateStore.put(any(), any()) } returns Unit
    }

    @Test
    fun testGeneratedStagingBranchNamesUseUuidSuffixWithoutSyncId() {
        val firstBranchName = generateStagingBranchName(makeAppendStream(syncId = 42))
        val retryBranchName = generateStagingBranchName(makeAppendStream(syncId = 43))
        val nextGenerationBranchName =
            generateStagingBranchName(makeAppendStream(syncId = 43, generationId = 2))

        assertEquals(firstBranchName, retryBranchName)
        assertNotEquals(firstBranchName, nextGenerationBranchName)
        assertTrue(firstBranchName.matches(Regex("""airbyte_staging_[0-9a-f_]{36}""")))
        assertTrue(nextGenerationBranchName.matches(Regex("""airbyte_staging_[0-9a-f_]{36}""")))
    }

    @Test
    fun testFailedTeardownPreservesUniqueStagingBranchForRecovery() {
        val objectSchema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = true),
                    "name" to FieldType(StringType, nullable = true),
                ),
            )
        val stream =
            DestinationStream(
                generationId = 1,
                minimumGenerationId = 0,
                syncId = 1,
                unmappedNamespace = "namespace",
                unmappedName = "name",
                namespaceMapper =
                    NamespaceMapper(namespaceDefinitionType = NamespaceDefinitionType.SOURCE),
                tableSchema = makeTableSchema(objectSchema, Append),
            )
        val icebergSchema = objectSchema.withAirbyteMeta(true).toIcebergSchema(emptyList())
        val icebergConfiguration = makeIcebergConfiguration()
        val catalog: Catalog = mockk()
        val manageSnapshots: ManageSnapshots = mockk()
        every { manageSnapshots.createBranch("airbyte_staging_test") } returns manageSnapshots
        every { manageSnapshots.removeBranch("airbyte_staging_test") } returns manageSnapshots
        every { manageSnapshots.commit() } just runs
        val table: Table = mockk {
            every { schema() } returns icebergSchema
            every { manageSnapshots() } returns manageSnapshots
        }
        val s3DataLakeUtil: S3DataLakeUtil = mockk {
            every { createNamespaceWithGlueHandling(any(), any()) } just runs
            every { toCatalogProperties(any()) } returns mapOf()
        }
        val icebergUtil: IcebergUtil = mockk {
            every { createCatalog(any(), any()) } returns catalog
            every { createTable(any(), any(), any()) } returns table
            every { toIcebergSchema(any()) } returns icebergSchema
        }
        val streamLoader =
            S3DataLakeStreamLoader(
                icebergConfiguration,
                stream,
                IcebergTableSynchronizer(
                    IcebergTypesComparator(),
                    IcebergSuperTypeFinder(IcebergTypesComparator()),
                ),
                s3DataLakeUtil,
                icebergUtil,
                stagingBranchName = "airbyte_staging_test",
                mainBranchName = "main",
                streamStateStore = streamStateStore,
            )

        runBlocking {
            streamLoader.start()
            streamLoader.teardown(false)
        }

        verify(exactly = 0) { manageSnapshots.removeBranch("airbyte_staging_test") }
        verify(exactly = 0) { manageSnapshots.replaceBranch("main", "airbyte_staging_test") }
    }

    @Test
    fun testSuccessfulTeardownRemovesUniqueStagingBranch() {
        val objectSchema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = true),
                    "name" to FieldType(StringType, nullable = true),
                ),
            )
        val stream =
            DestinationStream(
                generationId = 1,
                minimumGenerationId = 0,
                syncId = 1,
                unmappedNamespace = "namespace",
                unmappedName = "name",
                namespaceMapper =
                    NamespaceMapper(namespaceDefinitionType = NamespaceDefinitionType.SOURCE),
                tableSchema = makeTableSchema(objectSchema, Append),
            )
        val icebergSchema = objectSchema.withAirbyteMeta(true).toIcebergSchema(emptyList())
        val icebergConfiguration = makeIcebergConfiguration()
        val catalog: Catalog = mockk()
        val manageSnapshots: ManageSnapshots = mockk()
        every { manageSnapshots.createBranch("airbyte_staging_test") } returns manageSnapshots
        every { manageSnapshots.replaceBranch("main", "airbyte_staging_test") } returns
            manageSnapshots
        every { manageSnapshots.removeBranch("airbyte_staging_test") } returns manageSnapshots
        every { manageSnapshots.commit() } just runs
        val table: Table = mockk {
            every { schema() } returns icebergSchema
            every { refresh() } just runs
            every { manageSnapshots() } returns manageSnapshots
        }
        val s3DataLakeUtil: S3DataLakeUtil = mockk {
            every { createNamespaceWithGlueHandling(any(), any()) } just runs
            every { toCatalogProperties(any()) } returns mapOf()
        }
        val icebergUtil: IcebergUtil = mockk {
            every { createCatalog(any(), any()) } returns catalog
            every { createTable(any(), any(), any()) } returns table
            every { toIcebergSchema(any()) } returns icebergSchema
        }
        val streamLoader =
            S3DataLakeStreamLoader(
                icebergConfiguration,
                stream,
                IcebergTableSynchronizer(
                    IcebergTypesComparator(),
                    IcebergSuperTypeFinder(IcebergTypesComparator()),
                ),
                s3DataLakeUtil,
                icebergUtil,
                stagingBranchName = "airbyte_staging_test",
                mainBranchName = "main",
                streamStateStore = streamStateStore,
            )

        runBlocking {
            streamLoader.start()
            streamLoader.teardown(true)
        }

        verify { manageSnapshots.replaceBranch("main", "airbyte_staging_test") }
        verify { manageSnapshots.removeBranch("airbyte_staging_test") }
    }

    @Test
    fun testCompletedTeardownPreservesUniqueStagingBranchWhenPromotionFails() {
        val objectSchema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = true),
                    "name" to FieldType(StringType, nullable = true),
                ),
            )
        val stream =
            DestinationStream(
                generationId = 1,
                minimumGenerationId = 0,
                syncId = 1,
                unmappedNamespace = "namespace",
                unmappedName = "name",
                namespaceMapper =
                    NamespaceMapper(namespaceDefinitionType = NamespaceDefinitionType.SOURCE),
                tableSchema = makeTableSchema(objectSchema, Append),
            )
        val icebergSchema = objectSchema.withAirbyteMeta(true).toIcebergSchema(emptyList())
        val icebergConfiguration = makeIcebergConfiguration()
        val catalog: Catalog = mockk()
        val manageSnapshots: ManageSnapshots = mockk()
        var commitCount = 0
        every { manageSnapshots.createBranch("airbyte_staging_test") } returns manageSnapshots
        every { manageSnapshots.replaceBranch("main", "airbyte_staging_test") } returns
            manageSnapshots
        every { manageSnapshots.removeBranch("airbyte_staging_test") } returns manageSnapshots
        every { manageSnapshots.commit() } answers
            {
                commitCount += 1
                if (commitCount == 2) {
                    throw RuntimeException("promotion failed")
                }
            }
        val table: Table = mockk {
            every { schema() } returns icebergSchema
            every { refresh() } just runs
            every { manageSnapshots() } returns manageSnapshots
        }
        val s3DataLakeUtil: S3DataLakeUtil = mockk {
            every { createNamespaceWithGlueHandling(any(), any()) } just runs
            every { toCatalogProperties(any()) } returns mapOf()
        }
        val icebergUtil: IcebergUtil = mockk {
            every { createCatalog(any(), any()) } returns catalog
            every { createTable(any(), any(), any()) } returns table
            every { toIcebergSchema(any()) } returns icebergSchema
        }
        val streamLoader =
            S3DataLakeStreamLoader(
                icebergConfiguration,
                stream,
                IcebergTableSynchronizer(
                    IcebergTypesComparator(),
                    IcebergSuperTypeFinder(IcebergTypesComparator()),
                ),
                s3DataLakeUtil,
                icebergUtil,
                stagingBranchName = "airbyte_staging_test",
                mainBranchName = "main",
                streamStateStore = streamStateStore,
            )

        val failure =
            assertFailsWith<RuntimeException> {
                runBlocking {
                    streamLoader.start()
                    streamLoader.teardown(true)
                }
            }

        assertEquals("promotion failed", failure.message)
        verify { manageSnapshots.replaceBranch("main", "airbyte_staging_test") }
        verify(exactly = 0) { manageSnapshots.removeBranch("airbyte_staging_test") }
    }

    @Test
    fun testStartReusesExistingStagingBranchForRecovery() {
        val stream = makeAppendStream(syncId = 42)
        val objectSchema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = true),
                    "name" to FieldType(StringType, nullable = true),
                ),
            )
        val icebergSchema = objectSchema.withAirbyteMeta(true).toIcebergSchema(emptyList())
        val icebergConfiguration = makeIcebergConfiguration()
        val catalog: Catalog = mockk()
        val manageSnapshots: ManageSnapshots = mockk()
        every { manageSnapshots.createBranch("airbyte_staging_test") } throws
            IllegalArgumentException("already exists")
        every { manageSnapshots.replaceBranch("main", "airbyte_staging_test") } returns
            manageSnapshots
        every { manageSnapshots.removeBranch("airbyte_staging_test") } returns manageSnapshots
        every { manageSnapshots.commit() } just runs
        val table: Table = mockk {
            every { schema() } returns icebergSchema
            every { refresh() } just runs
            every { manageSnapshots() } returns manageSnapshots
        }
        val s3DataLakeUtil: S3DataLakeUtil = mockk {
            every { createNamespaceWithGlueHandling(any(), any()) } just runs
            every { toCatalogProperties(any()) } returns mapOf()
        }
        val icebergUtil: IcebergUtil = mockk {
            every { createCatalog(any(), any()) } returns catalog
            every { createTable(any(), any(), any()) } returns table
            every { toIcebergSchema(any()) } returns icebergSchema
        }
        val streamLoader =
            S3DataLakeStreamLoader(
                icebergConfiguration,
                stream,
                IcebergTableSynchronizer(
                    IcebergTypesComparator(),
                    IcebergSuperTypeFinder(IcebergTypesComparator()),
                ),
                s3DataLakeUtil,
                icebergUtil,
                stagingBranchName = "airbyte_staging_test",
                mainBranchName = "main",
                streamStateStore = streamStateStore,
            )

        runBlocking {
            streamLoader.start()
            streamLoader.teardown(true)
        }

        verify { manageSnapshots.createBranch("airbyte_staging_test") }
        verify { manageSnapshots.replaceBranch("main", "airbyte_staging_test") }
        verify { manageSnapshots.removeBranch("airbyte_staging_test") }
        verify {
            streamStateStore.put(
                stream.mappedDescriptor,
                match { it.stagingBranchName == "airbyte_staging_test" },
            )
        }
    }

    @Test
    fun testCreateStreamLoader() {
        val objectSchema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = true),
                    "name" to FieldType(StringType, nullable = true),
                ),
            )
        val stream =
            DestinationStream(
                generationId = 1,
                minimumGenerationId = 1,
                syncId = 1,
                unmappedNamespace = "namespace",
                unmappedName = "name",
                namespaceMapper =
                    NamespaceMapper(namespaceDefinitionType = NamespaceDefinitionType.SOURCE),
                tableSchema = makeTableSchema(objectSchema, Append),
            )
        val icebergSchema =
            Schema(
                Types.NestedField.optional(1, "id", Types.LongType.get()),
                Types.NestedField.optional(2, "name", Types.StringType.get()),
                Types.NestedField.required(
                    3,
                    Meta.Companion.COLUMN_NAME_AB_RAW_ID,
                    Types.StringType.get()
                ),
                Types.NestedField.required(
                    4,
                    Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT,
                    Types.LongType.get()
                ),
                Types.NestedField.required(
                    5,
                    Meta.Companion.COLUMN_NAME_AB_META,
                    Types.StructType.of(
                        Types.NestedField.required(6, "sync_id", Types.LongType.get()),
                        Types.NestedField.required(
                            7,
                            "changes",
                            Types.ListType.ofRequired(
                                8,
                                Types.StructType.of(
                                    Types.NestedField.required(9, "field", Types.StringType.get()),
                                    Types.NestedField.required(
                                        10,
                                        "change",
                                        Types.StringType.get(),
                                    ),
                                    Types.NestedField.required(
                                        11,
                                        "reason",
                                        Types.StringType.get(),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
                Types.NestedField.required(
                    12,
                    Meta.Companion.COLUMN_NAME_AB_GENERATION_ID,
                    Types.LongType.get()
                ),
            )
        val awsConfiguration: AWSAccessKeyConfiguration = mockk {
            every { accessKeyId } returns "access-key"
            every { secretAccessKey } returns "secret-access-key"
        }
        val bucketConfiguration: S3BucketConfiguration = mockk {
            every { s3BucketRegion } returns "us-east-1"
            every { s3BucketName } returns "bucket"
            every { s3Endpoint } returns "http://localhost:8080"
        }

        val icebergCatalogConfig: IcebergCatalogConfiguration = mockk {
            every { mainBranchName } returns "main"
            every { warehouseLocation } returns "s3://bucket/"
            every { catalogConfiguration } returns
                NessieCatalogConfiguration("http://localhost:8080/api/v1", "access-token", "")
        }
        val icebergConfiguration: S3DataLakeConfiguration = mockk {
            every { awsAccessKeyConfiguration } returns awsConfiguration
            every { icebergCatalogConfiguration } returns icebergCatalogConfig
            every { s3BucketConfiguration } returns bucketConfiguration
        }
        val catalog: Catalog = mockk()
        val table: Table = mockk { every { schema() } returns icebergSchema }
        every { table.manageSnapshots().createBranch(any()).commit() } just runs
        val s3DataLakeUtil: S3DataLakeUtil = mockk {
            every { createNamespaceWithGlueHandling(any(), any()) } just runs
            every { toCatalogProperties(any()) } returns mapOf()
        }
        val icebergUtil: IcebergUtil = mockk {
            every { createCatalog(any(), any()) } returns catalog
            every { createTable(any(), any(), any()) } returns table
            every { toIcebergSchema(any()) } answers
                {
                    objectSchema.withAirbyteMeta(true).toIcebergSchema(emptyList())
                }
        }
        val streamLoader =
            S3DataLakeStreamLoader(
                icebergConfiguration,
                stream,
                IcebergTableSynchronizer(
                    IcebergTypesComparator(),
                    IcebergSuperTypeFinder(IcebergTypesComparator()),
                ),
                s3DataLakeUtil,
                icebergUtil,
                stagingBranchName = DEFAULT_STAGING_BRANCH,
                mainBranchName = "main",
                streamStateStore = streamStateStore,
            )
        Assertions.assertNotNull(streamLoader)
    }

    @Test
    fun testCreateStreamLoaderWithMismatchedSchemasAndUniqueStagingBranch() {
        val objectSchema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = true),
                    "name" to FieldType(StringType, nullable = true),
                ),
            )
        val stream =
            DestinationStream(
                generationId = 1,
                minimumGenerationId = 1,
                syncId = 1,
                unmappedNamespace = "namespace",
                unmappedName = "name",
                namespaceMapper =
                    NamespaceMapper(namespaceDefinitionType = NamespaceDefinitionType.SOURCE),
                tableSchema = makeTableSchema(objectSchema, Append),
            )
        val icebergSchema =
            Schema(
                Types.NestedField.optional(2, "name", Types.StringType.get()),
            )
        val awsConfiguration: AWSAccessKeyConfiguration = mockk {
            every { accessKeyId } returns "access-key"
            every { secretAccessKey } returns "secret-access-key"
        }
        val bucketConfiguration: S3BucketConfiguration = mockk {
            every { s3BucketRegion } returns "us-east-1"
            every { s3BucketName } returns "bucket"
            every { s3Endpoint } returns "http://localhost:8080"
        }
        val icebergCatalogConfig: IcebergCatalogConfiguration = mockk {
            every { mainBranchName } returns "main"
            every { warehouseLocation } returns "s3://bucket/"
            every { catalogConfiguration } returns
                NessieCatalogConfiguration("http://localhost:8080/api/v1", "access-token", "")
        }
        val icebergConfiguration: S3DataLakeConfiguration = mockk {
            every { awsAccessKeyConfiguration } returns awsConfiguration
            every { icebergCatalogConfiguration } returns icebergCatalogConfig
            every { s3BucketConfiguration } returns bucketConfiguration
        }
        val catalog: Catalog = mockk()
        val table: Table = mockk {
            every { schema() } returns icebergSchema
            every { sortOrder() } returns SortOrder.unsorted()
        }
        val updateSchema: UpdateSchema = mockk()
        every { table.updateSchema().allowIncompatibleChanges() } returns updateSchema
        every {
            updateSchema.updateColumn(
                any<String>(),
                any<Type.PrimitiveType>(),
            )
        } returns updateSchema
        every {
            updateSchema.addColumn(
                any<String>(),
                any<String>(),
                any<Type.PrimitiveType>(),
            )
        } returns updateSchema
        every { updateSchema.setIdentifierFields(any<Collection<String>>()) } returns updateSchema

        every { updateSchema.commit() } just runs
        every { updateSchema.apply() } returns icebergSchema
        every { table.refresh() } just runs
        every { table.manageSnapshots().createBranch(any()).commit() } just runs
        every {
            table.manageSnapshots().replaceBranch("main", DEFAULT_STAGING_BRANCH).commit()
        } just runs
        every { table.manageSnapshots().removeBranch(DEFAULT_STAGING_BRANCH).commit() } just runs
        every { table.newScan().planFiles() } returns CloseableIterable.empty()
        val s3DataLakeUtil: S3DataLakeUtil = mockk {
            every { createNamespaceWithGlueHandling(any(), any()) } just runs
            every { toCatalogProperties(any()) } returns mapOf()
        }
        val icebergUtil: IcebergUtil = mockk {
            every { createCatalog(any(), any()) } returns catalog
            every { createTable(any(), any(), any()) } returns table
            every { toIcebergSchema(any()) } answers
                {
                    objectSchema.withAirbyteMeta(true).toIcebergSchema(emptyList())
                }
            every { constructGenerationIdSuffix(any<DestinationStream>()) } returns ""
        }
        val streamLoader =
            S3DataLakeStreamLoader(
                icebergConfiguration,
                stream,
                IcebergTableSynchronizer(
                    IcebergTypesComparator(),
                    IcebergSuperTypeFinder(IcebergTypesComparator()),
                ),
                s3DataLakeUtil,
                icebergUtil,
                stagingBranchName = DEFAULT_STAGING_BRANCH,
                mainBranchName = "main",
                streamStateStore = streamStateStore,
            )
        runBlocking { streamLoader.start() }

        verify(exactly = 0) { updateSchema.deleteColumn(any()) }
        verify(exactly = 0) { updateSchema.updateColumn(any(), any<Type.PrimitiveType>()) }
        verify(exactly = 0) { updateSchema.makeColumnOptional(any()) }
        verify(exactly = 0) { updateSchema.requireColumn(any()) }
        verify(exactly = 0) { updateSchema.setIdentifierFields(any<Collection<String>>()) }
        verify { updateSchema.addColumn(null, "_airbyte_raw_id", Types.StringType.get()) }
        verify { updateSchema.addColumn(null, "id", Types.LongType.get()) }
        verify { updateSchema.addColumn(null, "_airbyte_meta", any()) }
        verify { updateSchema.addColumn(null, "_airbyte_generation_id", Types.LongType.get()) }
        verify { updateSchema.addColumn(null, "id", Types.LongType.get()) }
        verify(exactly = 0) { updateSchema.commit() }

        runBlocking { streamLoader.teardown(true) }
        verify { updateSchema.commit() }
    }

    @Test
    fun testCreateStreamLoaderMismatchedPrimaryKeys() {
        val primaryKeys = listOf("id")
        val objectSchema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = false),
                    "name" to FieldType(StringType, nullable = true),
                ),
            )
        val stream =
            DestinationStream(
                generationId = 1,
                minimumGenerationId = 1,
                syncId = 1,
                unmappedNamespace = "namespace",
                unmappedName = "name",
                namespaceMapper =
                    NamespaceMapper(namespaceDefinitionType = NamespaceDefinitionType.SOURCE),
                tableSchema =
                    makeTableSchema(
                        objectSchema,
                        Dedupe(primaryKey = listOf(primaryKeys), cursor = primaryKeys)
                    ),
            )
        val columns =
            listOf(
                Types.NestedField.required(1, "id", Types.LongType.get()),
                Types.NestedField.optional(2, "name", Types.StringType.get()),
                Types.NestedField.required(
                    3,
                    Meta.Companion.COLUMN_NAME_AB_RAW_ID,
                    Types.StringType.get()
                ),
                Types.NestedField.required(
                    4,
                    Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT,
                    Types.LongType.get()
                ),
                Types.NestedField.required(
                    5,
                    Meta.Companion.COLUMN_NAME_AB_META,
                    Types.StructType.of(
                        Types.NestedField.required(6, "sync_id", Types.LongType.get()),
                        Types.NestedField.required(
                            7,
                            "changes",
                            Types.ListType.ofRequired(
                                8,
                                Types.StructType.of(
                                    Types.NestedField.required(9, "field", Types.StringType.get()),
                                    Types.NestedField.required(
                                        10,
                                        "change",
                                        Types.StringType.get(),
                                    ),
                                    Types.NestedField.required(
                                        11,
                                        "reason",
                                        Types.StringType.get(),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
                Types.NestedField.required(
                    12,
                    Meta.Companion.COLUMN_NAME_AB_GENERATION_ID,
                    Types.LongType.get()
                ),
            )
        val icebergSchema = Schema(columns, emptySet())
        val awsConfiguration: AWSAccessKeyConfiguration = mockk {
            every { accessKeyId } returns "access-key"
            every { secretAccessKey } returns "secret-access-key"
        }
        val bucketConfiguration: S3BucketConfiguration = mockk {
            every { s3BucketRegion } returns "us-east-1"
            every { s3BucketName } returns "bucket"
            every { s3Endpoint } returns "http://localhost:8080"
        }
        val icebergCatalogConfig: IcebergCatalogConfiguration = mockk {
            every { mainBranchName } returns "main"
            every { warehouseLocation } returns "s3://bucket/"
            every { catalogConfiguration } returns
                NessieCatalogConfiguration("http://localhost:8080/api/v1", "access-token", "")
        }
        val icebergConfiguration: S3DataLakeConfiguration = mockk {
            every { awsAccessKeyConfiguration } returns awsConfiguration
            every { icebergCatalogConfiguration } returns icebergCatalogConfig
            every { s3BucketConfiguration } returns bucketConfiguration
        }
        val catalog: Catalog = mockk()
        val table: Table = mockk {
            every { schema() } returns icebergSchema
            every { sortOrder() } returns SortOrder.unsorted()
        }
        val updateSchema: UpdateSchema = mockk()
        every { table.updateSchema().allowIncompatibleChanges() } returns updateSchema
        every {
            updateSchema.updateColumn(
                any<String>(),
                any<Type.PrimitiveType>(),
            )
        } returns updateSchema
        every {
            updateSchema.addColumn(
                any<String>(),
                any<String>(),
                any<Type.PrimitiveType>(),
            )
        } returns updateSchema
        every { updateSchema.requireColumn("id") } returns updateSchema
        every { updateSchema.setIdentifierFields(primaryKeys) } returns updateSchema
        every { updateSchema.commit() } just runs
        every { updateSchema.apply() } returns icebergSchema
        every { table.refresh() } just runs
        every { table.manageSnapshots().createBranch(any()).commit() } just runs
        every {
            table.manageSnapshots().replaceBranch("main", DEFAULT_STAGING_BRANCH).commit()
        } just runs
        every { table.manageSnapshots().removeBranch(DEFAULT_STAGING_BRANCH).commit() } just runs
        every { table.newScan().planFiles() } returns CloseableIterable.empty()
        val s3DataLakeUtil: S3DataLakeUtil = mockk {
            every { createNamespaceWithGlueHandling(any(), any()) } just runs
            every { toCatalogProperties(any()) } returns mapOf()
        }
        val icebergUtil: IcebergUtil = mockk {
            every { createCatalog(any(), any()) } returns catalog
            every { createTable(any(), any(), any()) } returns table
            every { toIcebergSchema(any()) } answers
                {
                    objectSchema.withAirbyteMeta(true).toIcebergSchema(listOf(primaryKeys))
                }
            every { constructGenerationIdSuffix(any<DestinationStream>()) } returns ""
        }
        val streamLoader =
            S3DataLakeStreamLoader(
                icebergConfiguration,
                stream,
                IcebergTableSynchronizer(
                    IcebergTypesComparator(),
                    IcebergSuperTypeFinder(IcebergTypesComparator()),
                ),
                s3DataLakeUtil,
                icebergUtil,
                stagingBranchName = DEFAULT_STAGING_BRANCH,
                mainBranchName = "main",
                streamStateStore = streamStateStore,
            )
        runBlocking { streamLoader.start() }

        verify(exactly = 0) { updateSchema.deleteColumn(any()) }
        verify(exactly = 0) { updateSchema.updateColumn(any(), any<Type.PrimitiveType>()) }
        verify(exactly = 0) { updateSchema.makeColumnOptional(any()) }
        verify(exactly = 0) {
            updateSchema.addColumn(any<String>(), any<String>(), any<Type.PrimitiveType>())
        }
        verify(exactly = 1) { updateSchema.requireColumn("id") }
        verify(exactly = 1) { updateSchema.setIdentifierFields(primaryKeys) }
        verify(exactly = 0) { updateSchema.commit() }

        runBlocking { streamLoader.teardown(true) }
        verify { updateSchema.commit() }
    }

    @Test
    fun testColumnTypeChangeBehaviorNonOverwrite() {
        val objectSchema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = false),
                    "name" to FieldType(StringType, nullable = true),
                ),
            )
        val stream =
            DestinationStream(
                generationId = 1,
                minimumGenerationId = 0,
                syncId = 1,
                unmappedNamespace = "namespace",
                unmappedName = "name",
                namespaceMapper =
                    NamespaceMapper(namespaceDefinitionType = NamespaceDefinitionType.SOURCE),
                tableSchema = makeTableSchema(objectSchema, Append),
            )
        val icebergConfiguration: S3DataLakeConfiguration = mockk()
        val s3DataLakeUtil: S3DataLakeUtil = mockk()
        val icebergUtil: IcebergUtil = mockk {
            every { toIcebergSchema(any()) } answers
                {
                    objectSchema.withAirbyteMeta(true).toIcebergSchema(emptyList())
                }
        }
        val streamLoader =
            S3DataLakeStreamLoader(
                icebergConfiguration,
                stream,
                IcebergTableSynchronizer(
                    IcebergTypesComparator(),
                    IcebergSuperTypeFinder(IcebergTypesComparator()),
                ),
                s3DataLakeUtil,
                icebergUtil,
                stagingBranchName = DEFAULT_STAGING_BRANCH,
                mainBranchName = "main",
                streamStateStore = streamStateStore,
            )

        assertEquals(
            ColumnTypeChangeBehavior.SAFE_SUPERTYPE,
            streamLoader.columnTypeChangeBehavior,
        )
    }

    private fun makeIcebergConfiguration(): S3DataLakeConfiguration {
        val awsConfiguration: AWSAccessKeyConfiguration = mockk {
            every { accessKeyId } returns "access-key"
            every { secretAccessKey } returns "secret-access-key"
        }
        val bucketConfiguration: S3BucketConfiguration = mockk {
            every { s3BucketRegion } returns S3BucketRegion.`us-east-1`.region
            every { s3BucketName } returns "bucket"
            every { s3Endpoint } returns "http://localhost:8080"
        }
        val icebergCatalogConfig: IcebergCatalogConfiguration = mockk {
            every { mainBranchName } returns "main"
            every { warehouseLocation } returns "s3://bucket/"
            every { catalogConfiguration } returns
                NessieCatalogConfiguration("http://localhost:8080/api/v1", "access-token", "")
        }
        return mockk {
            every { awsAccessKeyConfiguration } returns awsConfiguration
            every { icebergCatalogConfiguration } returns icebergCatalogConfig
            every { s3BucketConfiguration } returns bucketConfiguration
        }
    }

    private fun makeAppendStream(
        syncId: Long = 1,
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
        return DestinationStream(
            generationId = generationId,
            minimumGenerationId = minimumGenerationId,
            syncId = syncId,
            unmappedNamespace = "namespace",
            unmappedName = "name",
            namespaceMapper =
                NamespaceMapper(namespaceDefinitionType = NamespaceDefinitionType.SOURCE),
            tableSchema = makeTableSchema(objectSchema, Append),
        )
    }
}
