/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.IcebergCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.NessieCatalogConfiguration
import io.airbyte.cdk.load.command.s3.S3BucketConfiguration
import io.airbyte.cdk.load.command.s3.S3BucketRegion
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.MapperPipeline
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.iceberg.parquet.toIcebergSchema
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.toolkits.iceberg.parquet.ColumnTypeChangeBehavior
import io.airbyte.cdk.load.toolkits.iceberg.parquet.IcebergSuperTypeFinder
import io.airbyte.cdk.load.toolkits.iceberg.parquet.IcebergTableSynchronizer
import io.airbyte.cdk.load.toolkits.iceberg.parquet.IcebergTypesComparator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergTableWriterFactory
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.integrations.destination.s3_data_lake.io.S3DataLakeUtil
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.runs
import io.mockk.verify
import kotlin.test.assertEquals
import kotlinx.coroutines.runBlocking
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.UpdateSchema
import org.apache.iceberg.catalog.Catalog
import org.apache.iceberg.io.CloseableIterable
import org.apache.iceberg.types.Type.PrimitiveType
import org.apache.iceberg.types.Types
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Test

internal class S3DataLakeStreamLoaderTest {

    @Test
    fun testCreateStreamLoader() {
        val streamDescriptor = DestinationStream.Descriptor(namespace = "namespace", name = "name")
        val stream =
            DestinationStream(
                descriptor = streamDescriptor,
                importType = Append,
                schema =
                    ObjectType(
                        linkedMapOf(
                            "id" to FieldType(IntegerType, nullable = true),
                            "name" to FieldType(StringType, nullable = true),
                        ),
                    ),
                generationId = 1,
                minimumGenerationId = 1,
                syncId = 1,
            )
        val icebergSchema =
            Schema(
                Types.NestedField.of(1, true, "id", Types.LongType.get()),
                Types.NestedField.of(2, true, "name", Types.StringType.get()),
                Types.NestedField.of(3, false, COLUMN_NAME_AB_RAW_ID, Types.StringType.get()),
                Types.NestedField.of(4, false, COLUMN_NAME_AB_EXTRACTED_AT, Types.LongType.get()),
                Types.NestedField.of(
                    5,
                    false,
                    COLUMN_NAME_AB_META,
                    Types.StructType.of(
                        Types.NestedField.of(6, false, "sync_id", Types.LongType.get()),
                        Types.NestedField.of(
                            7,
                            false,
                            "changes",
                            Types.ListType.ofRequired(
                                8,
                                Types.StructType.of(
                                    Types.NestedField.of(9, false, "field", Types.StringType.get()),
                                    Types.NestedField.of(
                                        10,
                                        false,
                                        "change",
                                        Types.StringType.get(),
                                    ),
                                    Types.NestedField.of(
                                        11,
                                        false,
                                        "reason",
                                        Types.StringType.get(),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
                Types.NestedField.of(12, false, COLUMN_NAME_AB_GENERATION_ID, Types.LongType.get()),
            )
        val icebergTableWriterFactory: IcebergTableWriterFactory = mockk()
        val awsConfiguration: AWSAccessKeyConfiguration = mockk {
            every { accessKeyId } returns "access-key"
            every { secretAccessKey } returns "secret-access-key"
        }
        val bucketConfiguration: S3BucketConfiguration = mockk {
            every { s3BucketRegion } returns S3BucketRegion.`us-east-1`
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
            every { createTable(any(), any(), any(), any()) } returns table
            every { toIcebergSchema(any(), any<MapperPipeline>()) } answers
                {
                    val pipeline = secondArg() as MapperPipeline
                    pipeline.finalSchema.withAirbyteMeta(true).toIcebergSchema(emptyList())
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
                icebergTableWriterFactory,
                s3DataLakeUtil,
                icebergUtil,
                stagingBranchName = DEFAULT_STAGING_BRANCH,
                mainBranchName = "main",
            )
        assertNotNull(streamLoader)
    }

    @Test
    fun testCreateStreamLoaderWithMismatchedSchemasAndAlreadyExistingStagingBranch() {
        val streamDescriptor = DestinationStream.Descriptor(namespace = "namespace", name = "name")
        val stream =
            DestinationStream(
                descriptor = streamDescriptor,
                importType = Append,
                schema =
                    ObjectType(
                        linkedMapOf(
                            "id" to FieldType(IntegerType, nullable = true),
                            "name" to FieldType(StringType, nullable = true),
                        ),
                    ),
                generationId = 1,
                minimumGenerationId = 1,
                syncId = 1,
            )
        val icebergSchema =
            Schema(
                Types.NestedField.of(2, true, "name", Types.StringType.get()),
            )
        val icebergTableWriterFactory: IcebergTableWriterFactory = mockk()
        val awsConfiguration: AWSAccessKeyConfiguration = mockk {
            every { accessKeyId } returns "access-key"
            every { secretAccessKey } returns "secret-access-key"
        }
        val bucketConfiguration: S3BucketConfiguration = mockk {
            every { s3BucketRegion } returns S3BucketRegion.`us-east-1`
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
        val updateSchema: UpdateSchema = mockk()
        every { table.updateSchema().allowIncompatibleChanges() } returns updateSchema
        every {
            updateSchema.updateColumn(
                any<String>(),
                any<PrimitiveType>(),
            )
        } returns updateSchema
        every {
            updateSchema.addColumn(
                any<String>(),
                any<String>(),
                any<PrimitiveType>(),
            )
        } returns updateSchema
        every { updateSchema.setIdentifierFields(any<Collection<String>>()) } returns updateSchema
        every { updateSchema.commit() } just runs
        every { updateSchema.apply() } returns icebergSchema
        every { table.refresh() } just runs
        every { table.manageSnapshots().createBranch(any()).commit() } throws
            IllegalArgumentException("branch already exists")
        every { table.manageSnapshots().fastForwardBranch(any(), any()).commit() } just runs
        every { table.newScan().planFiles() } returns CloseableIterable.empty()
        val s3DataLakeUtil: S3DataLakeUtil = mockk {
            every { createNamespaceWithGlueHandling(any(), any()) } just runs
            every { toCatalogProperties(any()) } returns mapOf()
        }
        val icebergUtil: IcebergUtil = mockk {
            every { createCatalog(any(), any()) } returns catalog
            every { createTable(any(), any(), any(), any()) } returns table
            every { toIcebergSchema(any(), any<MapperPipeline>()) } answers
                {
                    val pipeline = secondArg() as MapperPipeline
                    pipeline.finalSchema.withAirbyteMeta(true).toIcebergSchema(emptyList())
                }
            every { constructGenerationIdSuffix(any() as Long) } returns ""
            every { assertGenerationIdSuffixIsOfValidFormat(any()) } just runs
        }
        val streamLoader =
            S3DataLakeStreamLoader(
                icebergConfiguration,
                stream,
                IcebergTableSynchronizer(
                    IcebergTypesComparator(),
                    IcebergSuperTypeFinder(IcebergTypesComparator()),
                ),
                icebergTableWriterFactory,
                s3DataLakeUtil,
                icebergUtil,
                stagingBranchName = DEFAULT_STAGING_BRANCH,
                mainBranchName = "main",
            )
        runBlocking { streamLoader.start() }

        verify(exactly = 0) { updateSchema.deleteColumn(any()) }
        verify(exactly = 0) { updateSchema.updateColumn(any(), any<PrimitiveType>()) }
        verify(exactly = 0) { updateSchema.makeColumnOptional(any()) }
        verify(exactly = 0) { updateSchema.requireColumn(any()) }
        verify(exactly = 0) { updateSchema.setIdentifierFields(any<Collection<String>>()) }
        verify { updateSchema.addColumn(null, "_airbyte_raw_id", Types.StringType.get()) }
        verify { updateSchema.addColumn(null, "id", Types.LongType.get()) }
        verify { updateSchema.addColumn(null, "_airbyte_meta", any()) }
        verify { updateSchema.addColumn(null, "_airbyte_generation_id", Types.LongType.get()) }
        verify { updateSchema.addColumn(null, "id", Types.LongType.get()) }
        verify(exactly = 0) { updateSchema.commit() }

        runBlocking { streamLoader.close(streamFailure = null) }
        verify { updateSchema.commit() }
    }

    @Test
    fun testCreateStreamLoaderMismatchedPrimaryKeys() {
        val primaryKeys = listOf("id")
        val streamDescriptor = DestinationStream.Descriptor(namespace = "namespace", name = "name")
        val stream =
            DestinationStream(
                descriptor = streamDescriptor,
                importType = Dedupe(primaryKey = listOf(primaryKeys), cursor = primaryKeys),
                schema =
                    ObjectType(
                        linkedMapOf(
                            "id" to FieldType(IntegerType, nullable = false),
                            "name" to FieldType(StringType, nullable = true),
                        ),
                    ),
                generationId = 1,
                minimumGenerationId = 1,
                syncId = 1,
            )
        val columns =
            listOf(
                Types.NestedField.of(1, false, "id", Types.LongType.get()),
                Types.NestedField.of(2, true, "name", Types.StringType.get()),
                Types.NestedField.of(3, false, COLUMN_NAME_AB_RAW_ID, Types.StringType.get()),
                Types.NestedField.of(4, false, COLUMN_NAME_AB_EXTRACTED_AT, Types.LongType.get()),
                Types.NestedField.of(
                    5,
                    false,
                    COLUMN_NAME_AB_META,
                    Types.StructType.of(
                        Types.NestedField.of(6, false, "sync_id", Types.LongType.get()),
                        Types.NestedField.of(
                            7,
                            false,
                            "changes",
                            Types.ListType.ofRequired(
                                8,
                                Types.StructType.of(
                                    Types.NestedField.of(9, false, "field", Types.StringType.get()),
                                    Types.NestedField.of(
                                        10,
                                        false,
                                        "change",
                                        Types.StringType.get(),
                                    ),
                                    Types.NestedField.of(
                                        11,
                                        false,
                                        "reason",
                                        Types.StringType.get(),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
                Types.NestedField.of(12, false, COLUMN_NAME_AB_GENERATION_ID, Types.LongType.get()),
            )
        val icebergSchema = Schema(columns, emptySet())
        val icebergTableWriterFactory: IcebergTableWriterFactory = mockk()
        val awsConfiguration: AWSAccessKeyConfiguration = mockk {
            every { accessKeyId } returns "access-key"
            every { secretAccessKey } returns "secret-access-key"
        }
        val bucketConfiguration: S3BucketConfiguration = mockk {
            every { s3BucketRegion } returns S3BucketRegion.`us-east-1`
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
        val updateSchema: UpdateSchema = mockk()
        every { table.updateSchema().allowIncompatibleChanges() } returns updateSchema
        every {
            updateSchema.updateColumn(
                any<String>(),
                any<PrimitiveType>(),
            )
        } returns updateSchema
        every {
            updateSchema.addColumn(
                any<String>(),
                any<String>(),
                any<PrimitiveType>(),
            )
        } returns updateSchema
        every { updateSchema.requireColumn("id") } returns updateSchema
        every { updateSchema.setIdentifierFields(primaryKeys) } returns updateSchema
        every { updateSchema.commit() } just runs
        every { updateSchema.apply() } returns icebergSchema
        every { table.refresh() } just runs
        every { table.manageSnapshots().createBranch(any()).commit() } just runs
        every { table.manageSnapshots().fastForwardBranch(any(), any()).commit() } just runs
        every { table.newScan().planFiles() } returns CloseableIterable.empty()
        val s3DataLakeUtil: S3DataLakeUtil = mockk {
            every { createNamespaceWithGlueHandling(any(), any()) } just runs
            every { toCatalogProperties(any()) } returns mapOf()
        }
        val icebergUtil: IcebergUtil = mockk {
            every { createCatalog(any(), any()) } returns catalog
            every { createTable(any(), any(), any(), any()) } returns table
            every { toIcebergSchema(any(), any<MapperPipeline>()) } answers
                {
                    val pipeline = secondArg() as MapperPipeline
                    pipeline.finalSchema.withAirbyteMeta(true).toIcebergSchema(listOf(primaryKeys))
                }
            every { constructGenerationIdSuffix(any() as Long) } returns ""
            every { assertGenerationIdSuffixIsOfValidFormat(any()) } just runs
        }
        val streamLoader =
            S3DataLakeStreamLoader(
                icebergConfiguration,
                stream,
                IcebergTableSynchronizer(
                    IcebergTypesComparator(),
                    IcebergSuperTypeFinder(IcebergTypesComparator()),
                ),
                icebergTableWriterFactory,
                s3DataLakeUtil,
                icebergUtil,
                stagingBranchName = DEFAULT_STAGING_BRANCH,
                mainBranchName = "main",
            )
        runBlocking { streamLoader.start() }

        verify(exactly = 0) { updateSchema.deleteColumn(any()) }
        verify(exactly = 0) { updateSchema.updateColumn(any(), any<PrimitiveType>()) }
        verify(exactly = 0) { updateSchema.makeColumnOptional(any()) }
        verify(exactly = 0) {
            updateSchema.addColumn(any<String>(), any<String>(), any<PrimitiveType>())
        }
        verify(exactly = 1) { updateSchema.requireColumn("id") }
        verify(exactly = 1) { updateSchema.setIdentifierFields(primaryKeys) }
        verify(exactly = 0) { updateSchema.commit() }

        runBlocking { streamLoader.close(streamFailure = null) }
        verify { updateSchema.commit() }
    }

    @Test
    fun testColumnTypeChangeBehaviorNonOverwrite() {
        val stream =
            DestinationStream(
                descriptor = DestinationStream.Descriptor(namespace = "namespace", name = "name"),
                importType = Append,
                schema =
                    ObjectType(
                        linkedMapOf(
                            "id" to FieldType(IntegerType, nullable = false),
                            "name" to FieldType(StringType, nullable = true),
                        ),
                    ),
                generationId = 1,
                minimumGenerationId = 0,
                syncId = 1,
            )
        val icebergConfiguration: S3DataLakeConfiguration = mockk()
        val icebergTableWriterFactory: IcebergTableWriterFactory = mockk()
        val s3DataLakeUtil: S3DataLakeUtil = mockk()
        val icebergUtil: IcebergUtil = mockk {
            every { toIcebergSchema(any(), any<MapperPipeline>()) } answers
                {
                    val pipeline = secondArg() as MapperPipeline
                    pipeline.finalSchema.withAirbyteMeta(true).toIcebergSchema(emptyList())
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
                icebergTableWriterFactory,
                s3DataLakeUtil,
                icebergUtil,
                stagingBranchName = DEFAULT_STAGING_BRANCH,
                mainBranchName = "main",
            )

        assertEquals(
            ColumnTypeChangeBehavior.SAFE_SUPERTYPE,
            streamLoader.columnTypeChangeBehavior,
        )
    }
}
