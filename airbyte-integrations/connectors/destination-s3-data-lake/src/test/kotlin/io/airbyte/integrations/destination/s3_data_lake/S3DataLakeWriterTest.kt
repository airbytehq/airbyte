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
import io.airbyte.integrations.destination.s3_data_lake.io.S3DataLakeTableWriterFactory
import io.airbyte.integrations.destination.s3_data_lake.io.S3DataLakeUtil
import io.mockk.every
import io.mockk.mockk
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.catalog.Catalog
import org.apache.iceberg.types.Types
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

internal class S3DataLakeWriterTest {

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
                        )
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
                                        Types.StringType.get()
                                    ),
                                    Types.NestedField.of(
                                        11,
                                        false,
                                        "reason",
                                        Types.StringType.get()
                                    )
                                )
                            )
                        )
                    )
                ),
                Types.NestedField.of(12, false, COLUMN_NAME_AB_GENERATION_ID, Types.LongType.get()),
            )
        val s3DataLakeTableWriterFactory: S3DataLakeTableWriterFactory = mockk()
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
                NessieCatalogConfiguration("http://localhost:8080/api/v1", "access-token")
        }
        val icebergConfiguration: S3DataLakeConfiguration = mockk {
            every { awsAccessKeyConfiguration } returns awsConfiguration
            every { icebergCatalogConfiguration } returns icebergCatalogConfig
            every { s3BucketConfiguration } returns bucketConfiguration
        }
        val catalog: Catalog = mockk()
        val table: Table = mockk { every { schema() } returns icebergSchema }
        val s3DataLakeUtil: S3DataLakeUtil = mockk {
            every { createCatalog(any(), any()) } returns catalog
            every { createTable(any(), any(), any(), any()) } returns table
            every { toCatalogProperties(any()) } returns mapOf()
            every { toIcebergSchema(any(), any<MapperPipeline>()) } answers
                {
                    val pipeline = secondArg() as MapperPipeline
                    pipeline.finalSchema.withAirbyteMeta(true).toIcebergSchema(emptyList())
                }
        }
        val s3DataLakeWriter =
            S3DataLakeWriter(
                s3DataLakeTableWriterFactory = s3DataLakeTableWriterFactory,
                icebergConfiguration = icebergConfiguration,
                s3DataLakeUtil = s3DataLakeUtil,
            )
        val streamLoader = s3DataLakeWriter.createStreamLoader(stream = stream)
        assertNotNull(streamLoader)
    }

    @Test
    fun testCreateStreamLoaderWithMismatchedSchemas() {
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
                        )
                    ),
                generationId = 1,
                minimumGenerationId = 1,
                syncId = 1,
            )
        val icebergSchema =
            Schema(
                Types.NestedField.of(2, true, "name", Types.StringType.get()),
            )
        val s3DataLakeTableWriterFactory: S3DataLakeTableWriterFactory = mockk()
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
                NessieCatalogConfiguration("http://localhost:8080/api/v1", "access-token")
        }
        val icebergConfiguration: S3DataLakeConfiguration = mockk {
            every { awsAccessKeyConfiguration } returns awsConfiguration
            every { icebergCatalogConfiguration } returns icebergCatalogConfig
            every { s3BucketConfiguration } returns bucketConfiguration
        }
        val catalog: Catalog = mockk()
        val table: Table = mockk { every { schema() } returns icebergSchema }
        val s3DataLakeUtil: S3DataLakeUtil = mockk {
            every { createCatalog(any(), any()) } returns catalog
            every { createTable(any(), any(), any(), any()) } returns table
            every { toCatalogProperties(any()) } returns mapOf()
            every { toIcebergSchema(any(), any<MapperPipeline>()) } answers
                {
                    val pipeline = secondArg() as MapperPipeline
                    pipeline.finalSchema.withAirbyteMeta(true).toIcebergSchema(emptyList())
                }
        }
        val s3DataLakeWriter =
            S3DataLakeWriter(
                s3DataLakeTableWriterFactory = s3DataLakeTableWriterFactory,
                icebergConfiguration = icebergConfiguration,
                s3DataLakeUtil = s3DataLakeUtil,
            )
        val e =
            assertThrows<IllegalArgumentException> {
                s3DataLakeWriter.createStreamLoader(stream = stream)
            }
        assertTrue(
            e.message?.startsWith("Table schema fields are different than catalog schema") ?: false
        )
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
                        )
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
                                        Types.StringType.get()
                                    ),
                                    Types.NestedField.of(
                                        11,
                                        false,
                                        "reason",
                                        Types.StringType.get()
                                    )
                                )
                            )
                        )
                    )
                ),
                Types.NestedField.of(12, false, COLUMN_NAME_AB_GENERATION_ID, Types.LongType.get()),
            )
        val icebergSchema = Schema(columns, emptySet())
        val s3DataLakeTableWriterFactory: S3DataLakeTableWriterFactory = mockk()
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
                NessieCatalogConfiguration("http://localhost:8080/api/v1", "access-token")
        }
        val icebergConfiguration: S3DataLakeConfiguration = mockk {
            every { awsAccessKeyConfiguration } returns awsConfiguration
            every { icebergCatalogConfiguration } returns icebergCatalogConfig
            every { s3BucketConfiguration } returns bucketConfiguration
        }
        val catalog: Catalog = mockk()
        val table: Table = mockk { every { schema() } returns icebergSchema }
        val s3DataLakeUtil: S3DataLakeUtil = mockk {
            every { createCatalog(any(), any()) } returns catalog
            every { createTable(any(), any(), any(), any()) } returns table
            every { toCatalogProperties(any()) } returns mapOf()
            every { toIcebergSchema(any(), any<MapperPipeline>()) } answers
                {
                    val pipeline = secondArg() as MapperPipeline
                    pipeline.finalSchema.withAirbyteMeta(true).toIcebergSchema(listOf(primaryKeys))
                }
        }
        val s3DataLakeWriter =
            S3DataLakeWriter(
                s3DataLakeTableWriterFactory = s3DataLakeTableWriterFactory,
                icebergConfiguration = icebergConfiguration,
                s3DataLakeUtil = s3DataLakeUtil,
            )
        val e =
            assertThrows<IllegalArgumentException> {
                s3DataLakeWriter.createStreamLoader(stream = stream)
            }
        assertTrue(e.message?.startsWith("Identifier fields are different") ?: false)
    }
}
