/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.io

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
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.parquet.ParquetMapperPipelineFactory
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.toolkits.iceberg.parquet.SimpleTableIdGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.AIRBYTE_CDC_DELETE_COLUMN
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.Operation
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.RecordWrapper
import io.airbyte.integrations.destination.s3_data_lake.S3DataLakeConfiguration
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import org.apache.iceberg.CatalogProperties.FILE_IO_IMPL
import org.apache.iceberg.CatalogProperties.URI
import org.apache.iceberg.CatalogProperties.WAREHOUSE_LOCATION
import org.apache.iceberg.CatalogUtil.ICEBERG_CATALOG_TYPE
import org.apache.iceberg.CatalogUtil.ICEBERG_CATALOG_TYPE_NESSIE
import org.apache.iceberg.FileFormat
import org.apache.iceberg.Schema
import org.apache.iceberg.TableProperties.DEFAULT_FILE_FORMAT
import org.apache.iceberg.aws.s3.S3FileIO
import org.apache.iceberg.catalog.Catalog
import org.apache.iceberg.nessie.NessieCatalog
import org.apache.iceberg.types.Types
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertDoesNotThrow
import org.junit.jupiter.api.assertThrows

internal class S3DataLakeUtilTest {

    private lateinit var s3DataLakeUtil: S3DataLakeUtil
    private lateinit var icebergUtil: IcebergUtil
    private val tableIdGenerator = SimpleTableIdGenerator()

    @BeforeEach
    fun setup() {
        icebergUtil = IcebergUtil(tableIdGenerator)
        s3DataLakeUtil = S3DataLakeUtil(icebergUtil, assumeRoleCredentials = null)
    }

    @Test
    fun testCreateCatalog() {
        val catalogName = "test-catalog"
        val properties =
            mapOf(
                ICEBERG_CATALOG_TYPE to ICEBERG_CATALOG_TYPE_NESSIE,
                URI to "http://localhost:19120/api/v1",
                WAREHOUSE_LOCATION to "s3://test/"
            )
        val catalog = icebergUtil.createCatalog(catalogName = catalogName, properties = properties)
        assertNotNull(catalog)
        assertEquals(catalogName, catalog.name())
        assertEquals(NessieCatalog::class.java, catalog.javaClass)
    }

    @Test
    fun testCreateTableWithMissingNamespace() {
        val properties = mapOf<String, String>()
        val streamDescriptor = DestinationStream.Descriptor("namespace", "name")
        val schema = Schema()
        val tableBuilder: Catalog.TableBuilder = mockk {
            every { withProperties(any()) } returns this
            every { withProperty(DEFAULT_FILE_FORMAT, FileFormat.PARQUET.name.lowercase()) } returns
                this
            every { withSortOrder(any()) } returns this
            every { create() } returns mockk()
        }
        val catalog: NessieCatalog = mockk {
            every {
                buildTable(tableIdGenerator.toTableIdentifier(streamDescriptor), any())
            } returns tableBuilder
            every { createNamespace(any()) } returns Unit
            every { namespaceExists(any()) } returns false
            every { tableExists(tableIdGenerator.toTableIdentifier(streamDescriptor)) } returns
                false
        }
        s3DataLakeUtil.createNamespaceWithGlueHandling(streamDescriptor, catalog)
        val table =
            icebergUtil.createTable(
                streamDescriptor = streamDescriptor,
                catalog = catalog,
                schema = schema,
                properties = properties
            )
        assertNotNull(table)
        verify(exactly = 1) {
            catalog.createNamespace(
                tableIdGenerator.toTableIdentifier(streamDescriptor).namespace()
            )
        }
        verify(exactly = 1) { tableBuilder.create() }
    }

    @Test
    fun testCreateTableWithExistingNamespace() {
        val properties = mapOf<String, String>()
        val streamDescriptor = DestinationStream.Descriptor("namespace", "name")
        val schema = Schema()
        val tableBuilder: Catalog.TableBuilder = mockk {
            every { withProperties(any()) } returns this
            every { withProperty(DEFAULT_FILE_FORMAT, FileFormat.PARQUET.name.lowercase()) } returns
                this
            every { withSortOrder(any()) } returns this
            every { create() } returns mockk()
        }
        val catalog: NessieCatalog = mockk {
            every {
                buildTable(tableIdGenerator.toTableIdentifier(streamDescriptor), any())
            } returns tableBuilder
            every { namespaceExists(any()) } returns true
            every { tableExists(tableIdGenerator.toTableIdentifier(streamDescriptor)) } returns
                false
        }
        s3DataLakeUtil.createNamespaceWithGlueHandling(streamDescriptor, catalog)
        val table =
            icebergUtil.createTable(
                streamDescriptor = streamDescriptor,
                catalog = catalog,
                schema = schema,
                properties = properties
            )
        assertNotNull(table)
        verify(exactly = 0) {
            catalog.createNamespace(
                tableIdGenerator.toTableIdentifier(streamDescriptor).namespace()
            )
        }
        verify(exactly = 1) { tableBuilder.create() }
    }

    @Test
    fun testLoadTable() {
        val properties = mapOf<String, String>()
        val streamDescriptor = DestinationStream.Descriptor("namespace", "name")
        val schema = Schema()
        val catalog: NessieCatalog = mockk {
            every { loadTable(tableIdGenerator.toTableIdentifier(streamDescriptor)) } returns
                mockk()
            every { namespaceExists(any()) } returns true
            every { tableExists(tableIdGenerator.toTableIdentifier(streamDescriptor)) } returns true
        }
        s3DataLakeUtil.createNamespaceWithGlueHandling(streamDescriptor, catalog)
        val table =
            icebergUtil.createTable(
                streamDescriptor = streamDescriptor,
                catalog = catalog,
                schema = schema,
                properties = properties
            )
        assertNotNull(table)
        verify(exactly = 0) {
            catalog.createNamespace(
                tableIdGenerator.toTableIdentifier(streamDescriptor).namespace()
            )
        }
        verify(exactly = 1) {
            catalog.loadTable(tableIdGenerator.toTableIdentifier(streamDescriptor))
        }
    }

    @Test
    fun testConvertAirbyteRecordToIcebergRecordInsert() {
        val streamDescriptor = DestinationStream.Descriptor(namespace = "namespace", name = "name")
        val airbyteStream =
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
        val airbyteRecord =
            DestinationRecordAirbyteValue(
                stream = airbyteStream.descriptor,
                data =
                    ObjectValue(
                        linkedMapOf("id" to IntegerValue(42L), "name" to StringValue("John Doe"))
                    ),
                emittedAtMs = System.currentTimeMillis(),
                meta = Meta(),
            )
        val pipeline = ParquetMapperPipelineFactory().create(airbyteStream)
        val columns =
            mutableListOf(
                Types.NestedField.required(1, "id", Types.IntegerType.get()),
                Types.NestedField.required(2, "name", Types.StringType.get()),
            )
        val schema = Schema(columns)
        val icebergRecord =
            icebergUtil.toRecord(
                record = airbyteRecord,
                pipeline = pipeline,
                tableSchema = schema,
                stream = airbyteStream
            )
        assertNotNull(icebergRecord)
        assertEquals(RecordWrapper::class.java, icebergRecord.javaClass)
        assertEquals(Operation.INSERT, (icebergRecord as RecordWrapper).operation)
    }

    @Test
    fun testConvertAirbyteRecordToIcebergRecordDelete() {
        val streamDescriptor = DestinationStream.Descriptor(namespace = "namespace", name = "name")
        val airbyteStream =
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
        val airbyteRecord =
            DestinationRecordAirbyteValue(
                stream = airbyteStream.descriptor,
                data =
                    ObjectValue(
                        linkedMapOf(
                            "id" to IntegerValue(42L),
                            "name" to StringValue("John Doe"),
                            AIRBYTE_CDC_DELETE_COLUMN to
                                TimestampWithTimezoneValue("2024-01-01T00:00:00Z"),
                        )
                    ),
                emittedAtMs = System.currentTimeMillis(),
                meta = Meta(),
            )
        val pipeline = ParquetMapperPipelineFactory().create(airbyteStream)
        val columns =
            mutableListOf(
                Types.NestedField.required(1, "id", Types.IntegerType.get()),
                Types.NestedField.required(2, "name", Types.StringType.get()),
            )
        val schema = Schema(columns, setOf(1))
        val icebergRecord =
            icebergUtil.toRecord(
                record = airbyteRecord,
                pipeline = pipeline,
                tableSchema = schema,
                stream = airbyteStream
            )
        assertNotNull(icebergRecord)
        assertEquals(RecordWrapper::class.java, icebergRecord.javaClass)
        assertEquals(Operation.DELETE, (icebergRecord as RecordWrapper).operation)
    }

    @Test
    fun testConvertAirbyteRecordToIcebergRecordUpdate() {
        val streamDescriptor = DestinationStream.Descriptor(namespace = "namespace", name = "name")
        val airbyteStream =
            DestinationStream(
                descriptor = streamDescriptor,
                importType = Dedupe(primaryKey = listOf(listOf("id")), cursor = listOf("id")),
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
        val airbyteRecord =
            DestinationRecordAirbyteValue(
                stream = airbyteStream.descriptor,
                data =
                    ObjectValue(
                        linkedMapOf("id" to IntegerValue(42L), "name" to StringValue("John Doe"))
                    ),
                emittedAtMs = System.currentTimeMillis(),
                meta = Meta(),
            )
        val pipeline = ParquetMapperPipelineFactory().create(airbyteStream)
        val columns =
            mutableListOf(
                Types.NestedField.required(1, "id", Types.IntegerType.get()),
                Types.NestedField.required(2, "name", Types.StringType.get()),
            )
        val schema = Schema(columns, setOf(1))
        val icebergRecord =
            icebergUtil.toRecord(
                record = airbyteRecord,
                pipeline = pipeline,
                tableSchema = schema,
                stream = airbyteStream
            )
        assertNotNull(icebergRecord)
        assertEquals(RecordWrapper::class.java, icebergRecord.javaClass)
        assertEquals(Operation.UPDATE, (icebergRecord as RecordWrapper).operation)
    }

    @Test
    fun testCatalogProperties() {
        val awsAccessKey = "access-key"
        val awsSecretAccessKey = "secret-access-key"
        val nessieAccessToken = "nessie-access-token"
        val nessieServerUri = "http://localhost:8080"
        val warehouseLocation = "s3://test/"
        val s3BucketName = "test"
        val s3Endpoint = "http://localhost:9000"
        val databaseName = ""
        val awsAccessKeyConfiguration =
            AWSAccessKeyConfiguration(
                accessKeyId = awsAccessKey,
                secretAccessKey = awsSecretAccessKey,
            )
        val s3BucketConfiguration =
            S3BucketConfiguration(
                s3BucketName = s3BucketName,
                s3BucketRegion = S3BucketRegion.`us-east-1`,
                s3Endpoint = s3Endpoint,
            )
        val icebergCatalogConfiguration =
            IcebergCatalogConfiguration(
                warehouseLocation,
                "main",
                NessieCatalogConfiguration(nessieServerUri, nessieAccessToken, databaseName),
            )
        val configuration =
            S3DataLakeConfiguration(
                awsAccessKeyConfiguration = awsAccessKeyConfiguration,
                icebergCatalogConfiguration = icebergCatalogConfiguration,
                s3BucketConfiguration = s3BucketConfiguration,
                numProcessRecordsWorkers = 1,
                numProcessBatchWorkers = 1,
            )
        val catalogProperties = s3DataLakeUtil.toCatalogProperties(config = configuration)
        assertEquals(ICEBERG_CATALOG_TYPE_NESSIE, catalogProperties[ICEBERG_CATALOG_TYPE])
        assertEquals(nessieServerUri, catalogProperties[URI])
        assertEquals(warehouseLocation, catalogProperties[WAREHOUSE_LOCATION])
        assertEquals(S3FileIO::class.java.name, catalogProperties[FILE_IO_IMPL])
        assertEquals("main", catalogProperties["nessie.ref"])
        assertEquals(awsAccessKey, catalogProperties["s3.access-key-id"])
        assertEquals(awsSecretAccessKey, catalogProperties["s3.secret-access-key"])
        assertEquals(s3Endpoint, catalogProperties["s3.endpoint"])
        assertEquals("true", catalogProperties["s3.path-style-access"])
        assertEquals("BEARER", catalogProperties["nessie.authentication.type"])
        assertEquals(nessieAccessToken, catalogProperties["nessie.authentication.token"])
    }

    @Test
    fun `assertGenerationIdSuffixIsOfValidFormat accepts valid format`() {
        val validGenerationId = "ab-generation-id-123-e"
        assertDoesNotThrow {
            icebergUtil.assertGenerationIdSuffixIsOfValidFormat(validGenerationId)
        }
    }

    @Test
    fun `assertGenerationIdSuffixIsOfValidFormat throws exception for invalid prefix`() {
        val invalidGenerationId = "invalid-generation-id-123"
        val exception =
            assertThrows<IcebergUtil.InvalidFormatException> {
                icebergUtil.assertGenerationIdSuffixIsOfValidFormat(invalidGenerationId)
            }
        assertEquals(
            "Invalid format: $invalidGenerationId. Expected format is 'ab-generation-id-<number>-e'",
            exception.message
        )
    }

    @Test
    fun `assertGenerationIdSuffixIsOfValidFormat throws exception for missing number`() {
        val invalidGenerationId = "ab-generation-id-"
        val exception =
            assertThrows<IcebergUtil.InvalidFormatException> {
                icebergUtil.assertGenerationIdSuffixIsOfValidFormat(invalidGenerationId)
            }
        assertEquals(
            "Invalid format: $invalidGenerationId. Expected format is 'ab-generation-id-<number>-e'",
            exception.message
        )
    }

    @Test
    fun `constructGenerationIdSuffix constructs valid suffix`() {
        val stream = mockk<DestinationStream>()
        every { stream.generationId } returns 42
        val expectedSuffix = "ab-generation-id-42-e"
        val result = icebergUtil.constructGenerationIdSuffix(stream)
        assertEquals(expectedSuffix, result)
    }

    @Test
    fun `constructGenerationIdSuffix throws exception for negative generationId`() {
        val stream = mockk<DestinationStream>()
        every { stream.generationId } returns -1
        val exception =
            assertThrows<IllegalArgumentException> {
                icebergUtil.constructGenerationIdSuffix(stream)
            }
        assertEquals(
            "GenerationId must be non-negative. Provided: ${stream.generationId}",
            exception.message
        )
    }

    @Test
    fun testConversionToIcebergSchemaWithMetadataAndPrimaryKey() {
        val streamDescriptor = DestinationStream.Descriptor(namespace = "namespace", name = "name")
        val primaryKeys = listOf("id")
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
        val pipeline = ParquetMapperPipelineFactory().create(stream)
        val schema = icebergUtil.toIcebergSchema(stream = stream, pipeline = pipeline)
        assertEquals(primaryKeys.toSet(), schema.identifierFieldNames())
        assertEquals(6, schema.columns().size)
        assertNotNull(schema.findField("id"))
        assertNotNull(schema.findField("name"))
        assertNotNull(schema.findField(COLUMN_NAME_AB_RAW_ID))
        assertNotNull(schema.findField(COLUMN_NAME_AB_EXTRACTED_AT))
        assertNotNull(schema.findField(COLUMN_NAME_AB_META))
        assertNotNull(schema.findField(COLUMN_NAME_AB_GENERATION_ID))
    }

    @Test
    fun testConversionToIcebergSchemaWithMetadataAndWithoutPrimaryKey() {
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
        val pipeline = ParquetMapperPipelineFactory().create(stream)
        val schema = icebergUtil.toIcebergSchema(stream = stream, pipeline = pipeline)
        assertEquals(emptySet<String>(), schema.identifierFieldNames())
        assertEquals(6, schema.columns().size)
        assertNotNull(schema.findField("id"))
        assertNotNull(schema.findField("name"))
        assertNotNull(schema.findField(COLUMN_NAME_AB_RAW_ID))
        assertNotNull(schema.findField(COLUMN_NAME_AB_EXTRACTED_AT))
        assertNotNull(schema.findField(COLUMN_NAME_AB_META))
        assertNotNull(schema.findField(COLUMN_NAME_AB_GENERATION_ID))
    }
}
