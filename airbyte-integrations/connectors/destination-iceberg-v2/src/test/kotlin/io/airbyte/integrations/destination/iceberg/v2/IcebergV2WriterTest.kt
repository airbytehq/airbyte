/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

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
import io.airbyte.integrations.destination.iceberg.v2.io.IcebergTableWriterFactory
import io.airbyte.integrations.destination.iceberg.v2.io.IcebergUtil
import io.mockk.every
import io.mockk.mockk
import java.time.Duration
import org.apache.hadoop.conf.Configuration
import org.apache.iceberg.CatalogUtil
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.aws.AwsClientProperties
import org.apache.iceberg.aws.AwsProperties
import org.apache.iceberg.catalog.Catalog
import org.apache.iceberg.catalog.Namespace
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.types.Types
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.slf4j.LoggerFactory

internal class IcebergV2WriterTest {

    class IcebergCatalogFactory(
        private val warehousePath: String,
        private val region: String,
        private val roleArn: String,
        private val baseAccessKeyId: String,
        private val baseSecretKey: String
    ) {
        private val logger = LoggerFactory.getLogger(IcebergCatalogFactory::class.java)

        fun createCatalog(catalogName: String): Catalog {
            logger.info("Creating catalog with name: $catalogName, region: $region, role: $roleArn")

//            System.setProperty("aws.accessKeyId", baseAccessKeyId)
//            System.setProperty("aws.secretAccessKey", baseSecretKey)

            val properties = buildCatalogProperties()
            logProperties(properties)

            val hadoopConfig = Configuration()
//            hadoopConfig.set("aws.region", region)

            return CatalogUtil.buildIcebergCatalog(catalogName, properties, hadoopConfig)
        }

        private fun buildCatalogProperties(): Map<String, String> {
            return mapOf(
                "catalog-impl" to "org.apache.iceberg.aws.glue.GlueCatalog",
                "warehouse" to warehousePath,
                "aws.region" to region,
                "io-impl" to "org.apache.iceberg.aws.s3.S3FileIO",

                // Base credentials
                "rest.access-key-id" to baseAccessKeyId,
                "rest.secret-access-key" to baseSecretKey,
                AwsProperties.CLIENT_FACTORY to "org.apache.iceberg.aws.AssumeRoleAwsClientFactory",
                AwsProperties.CLIENT_ASSUME_ROLE_ARN to roleArn,
                AwsProperties.CLIENT_ASSUME_ROLE_REGION to region,
                AwsProperties.CLIENT_ASSUME_ROLE_TIMEOUT_SEC to
                    Duration.ofHours(1).toSeconds().toString(),
                AwsProperties.CLIENT_ASSUME_ROLE_EXTERNAL_ID to "8eee93517501b43a"
            )
        }

        private fun logProperties(properties: Map<String, String>) {
            logger.info("Catalog properties:")
            properties.forEach { (key, value) ->
                val sanitizedValue =
                    if (key.contains("secret", ignoreCase = true)) "****" else value
                logger.info("  $key: $sanitizedValue")
            }
        }
    }

    class CatalogTestHelper(private val catalog: Catalog, private val databaseName: String) {
        private val logger = LoggerFactory.getLogger(CatalogTestHelper::class.java)

        fun validateCatalogConnection(): Boolean {
            return try {
                val namespace = Namespace.of(databaseName)
                // List tables in the namespace
                logger.info("Listing tables in namespace: $databaseName")
                catalog.listTables(namespace)
                logger.info("Successfully connected to catalog and listed tables")
                true
            } catch (e: Exception) {
                logger.error("Failed to validate catalog connection", e)
                false
            }
        }

        fun testTableOperations(tableName: String): Boolean {
            return try {
                val tableId = TableIdentifier.of(databaseName, tableName)
                val schema = Schema() // Empty schema for test

                logger.info("Creating test table: $tableName in database: $databaseName")
                catalog.createTable(tableId, schema)

                logger.info("Loading test table: $tableName")
                val table = catalog.loadTable(tableId)
                logger.info("Loaded test table: $table")

                logger.info("Dropping test table: $tableName")
                catalog.dropTable(tableId)

                logger.info("Table operations completed successfully")
                true
            } catch (e: Exception) {
                logger.error("Failed during table operations test", e)
                false
            }
        }
    }

    // Usage example
    @Test
    fun mainTest() {
        val region = "us-east-2"
//        System.setProperty("aws.region", region)

        try {
            val catalog =
                createAuthenticatedCatalog(
                    catalogName = "frifri-test",
                    warehousePath = "s3://airbyte-integration-test-destination-s3/frifri-test",
                    region = region,
                    roleArn =
                        "arn:aws:iam::317283927606:role/s3_acceptance_test_iam_assume_role_role",
                    baseAccessKeyId = "",
                    baseSecretKey = ""
                )

            val databaseName = "frifri_test_db" // Specify your database name
            val helper = CatalogTestHelper(catalog, databaseName)

            // Test connection
            assert(helper.validateCatalogConnection()) { "Failed to validate catalog connection" }

            // Test table operations
            assert(helper.testTableOperations("test_table")) {
                "Failed to perform table operations"
            }

            println("All tests passed successfully!")
        } catch (e: Exception) {
            println("Test failed with exception: ${e.message}")
            e.printStackTrace()
            throw e
        }
    }

    fun createAuthenticatedCatalog(
        catalogName: String,
        warehousePath: String,
        region: String,
        roleArn: String,
        baseAccessKeyId: String,
        baseSecretKey: String
    ): Catalog {
        val factory =
            IcebergCatalogFactory(
                warehousePath = warehousePath,
                region = region,
                roleArn = roleArn,
                baseAccessKeyId = baseAccessKeyId,
                baseSecretKey = baseSecretKey
            )

        return factory.createCatalog(catalogName)
    }

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

        icebergSchema.asStruct().fields().asSequence().associateBy { it.name() }

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
                NessieCatalogConfiguration("http://localhost:8080/api/v1", "access-token")
        }
        val icebergConfiguration: IcebergV2Configuration = mockk {
            every { awsAccessKeyConfiguration } returns awsConfiguration
            every { icebergCatalogConfiguration } returns icebergCatalogConfig
            every { s3BucketConfiguration } returns bucketConfiguration
        }
        val catalog: Catalog = mockk()
        val table: Table = mockk { every { schema() } returns icebergSchema }
        val icebergUtil: IcebergUtil = mockk {
            every { createCatalog(any(), any()) } returns catalog
            every { createTable(any(), any(), any(), any()) } returns table
            every { toCatalogProperties(any()) } returns mapOf()
            every { toIcebergSchema(any(), any<MapperPipeline>()) } answers
                {
                    val pipeline = secondArg() as MapperPipeline
                    pipeline.finalSchema.withAirbyteMeta(true).toIcebergSchema(emptyList())
                }
        }
        val icebergV2Writer =
            IcebergV2Writer(
                icebergTableWriterFactory = icebergTableWriterFactory,
                icebergConfiguration = icebergConfiguration,
                icebergUtil = icebergUtil,
            )
        val streamLoader = icebergV2Writer.createStreamLoader(stream = stream)
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
                NessieCatalogConfiguration("http://localhost:8080/api/v1", "access-token")
        }
        val icebergConfiguration: IcebergV2Configuration = mockk {
            every { awsAccessKeyConfiguration } returns awsConfiguration
            every { icebergCatalogConfiguration } returns icebergCatalogConfig
            every { s3BucketConfiguration } returns bucketConfiguration
        }
        val catalog: Catalog = mockk()
        val table: Table = mockk { every { schema() } returns icebergSchema }
        val icebergUtil: IcebergUtil = mockk {
            every { createCatalog(any(), any()) } returns catalog
            every { createTable(any(), any(), any(), any()) } returns table
            every { toCatalogProperties(any()) } returns mapOf()
            every { toIcebergSchema(any(), any<MapperPipeline>()) } answers
                {
                    val pipeline = secondArg() as MapperPipeline
                    pipeline.finalSchema.withAirbyteMeta(true).toIcebergSchema(emptyList())
                }
        }
        val icebergV2Writer =
            IcebergV2Writer(
                icebergTableWriterFactory = icebergTableWriterFactory,
                icebergConfiguration = icebergConfiguration,
                icebergUtil = icebergUtil,
            )
        val e =
            assertThrows<IllegalArgumentException> {
                icebergV2Writer.createStreamLoader(stream = stream)
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
                NessieCatalogConfiguration("http://localhost:8080/api/v1", "access-token")
        }
        val icebergConfiguration: IcebergV2Configuration = mockk {
            every { awsAccessKeyConfiguration } returns awsConfiguration
            every { icebergCatalogConfiguration } returns icebergCatalogConfig
            every { s3BucketConfiguration } returns bucketConfiguration
        }
        val catalog: Catalog = mockk()
        val table: Table = mockk { every { schema() } returns icebergSchema }
        val icebergUtil: IcebergUtil = mockk {
            every { createCatalog(any(), any()) } returns catalog
            every { createTable(any(), any(), any(), any()) } returns table
            every { toCatalogProperties(any()) } returns mapOf()
            every { toIcebergSchema(any(), any<MapperPipeline>()) } answers
                {
                    val pipeline = secondArg() as MapperPipeline
                    pipeline.finalSchema.withAirbyteMeta(true).toIcebergSchema(listOf(primaryKeys))
                }
        }
        val icebergV2Writer =
            IcebergV2Writer(
                icebergTableWriterFactory = icebergTableWriterFactory,
                icebergConfiguration = icebergConfiguration,
                icebergUtil = icebergUtil,
            )
        val e =
            assertThrows<IllegalArgumentException> {
                icebergV2Writer.createStreamLoader(stream = stream)
            }
        assertTrue(e.message?.startsWith("Identifier fields are different") ?: false)
    }
}
