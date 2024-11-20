/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2.io

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.NessieServerConfiguration
import io.airbyte.cdk.load.command.s3.S3BucketConfiguration
import io.airbyte.cdk.load.command.s3.S3BucketRegion
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.parquet.ParquetMapperPipelineFactory
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.integrations.destination.iceberg.v2.IcebergV2Configuration
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
import org.apache.iceberg.catalog.Namespace
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.nessie.NessieCatalog
import org.apache.iceberg.types.Types
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Test

internal class IcebergUtilTest {

    @Test
    fun testCreateCatalog() {
        val catalogName = "test-catalog"
        val properties =
            mapOf(
                ICEBERG_CATALOG_TYPE to ICEBERG_CATALOG_TYPE_NESSIE,
                URI to "http://localhost:19120/api/v1",
                WAREHOUSE_LOCATION to "s3://test/"
            )
        val catalog = IcebergUtil.createCatalog(catalogName = catalogName, properties = properties)
        assertNotNull(catalog)
        assertEquals(catalogName, catalog.name())
        assertEquals(NessieCatalog::class.java, catalog.javaClass)
    }

    @Test
    fun testCreateTableWithMissingNamespace() {
        val properties = mapOf<String, String>()
        val tableIdentifier = TableIdentifier.of(Namespace.of("namespace"), "name")
        val schema = Schema()
        val tableBuilder: Catalog.TableBuilder = mockk {
            every { withProperties(any()) } returns this
            every { withProperty(DEFAULT_FILE_FORMAT, FileFormat.PARQUET.name.lowercase()) } returns
                this
            every { withSortOrder(any()) } returns this
            every { create() } returns mockk()
        }
        val catalog: NessieCatalog = mockk {
            every { buildTable(tableIdentifier, any()) } returns tableBuilder
            every { createNamespace(any()) } returns Unit
            every { namespaceExists(any()) } returns false
            every { tableExists(tableIdentifier) } returns false
        }
        val table =
            IcebergUtil.createTable(
                tableIdentifier = tableIdentifier,
                catalog = catalog,
                schema = schema,
                properties = properties
            )
        assertNotNull(table)
        verify(exactly = 1) { catalog.createNamespace(tableIdentifier.namespace()) }
        verify(exactly = 1) { tableBuilder.create() }
    }

    @Test
    fun testCreateTableWithExistingNamespace() {
        val properties = mapOf<String, String>()
        val tableIdentifier = TableIdentifier.of(Namespace.of("namespace"), "name")
        val schema = Schema()
        val tableBuilder: Catalog.TableBuilder = mockk {
            every { withProperties(any()) } returns this
            every { withProperty(DEFAULT_FILE_FORMAT, FileFormat.PARQUET.name.lowercase()) } returns
                this
            every { withSortOrder(any()) } returns this
            every { create() } returns mockk()
        }
        val catalog: NessieCatalog = mockk {
            every { buildTable(tableIdentifier, any()) } returns tableBuilder
            every { namespaceExists(any()) } returns true
            every { tableExists(tableIdentifier) } returns false
        }
        val table =
            IcebergUtil.createTable(
                tableIdentifier = tableIdentifier,
                catalog = catalog,
                schema = schema,
                properties = properties
            )
        assertNotNull(table)
        verify(exactly = 0) { catalog.createNamespace(tableIdentifier.namespace()) }
        verify(exactly = 1) { tableBuilder.create() }
    }

    @Test
    fun testLoadTable() {
        val properties = mapOf<String, String>()
        val tableIdentifier = TableIdentifier.of(Namespace.of("namespace"), "name")
        val schema = Schema()
        val catalog: NessieCatalog = mockk {
            every { loadTable(tableIdentifier) } returns mockk()
            every { namespaceExists(any()) } returns true
            every { tableExists(tableIdentifier) } returns true
        }
        val table =
            IcebergUtil.createTable(
                tableIdentifier = tableIdentifier,
                catalog = catalog,
                schema = schema,
                properties = properties
            )
        assertNotNull(table)
        verify(exactly = 0) { catalog.createNamespace(tableIdentifier.namespace()) }
        verify(exactly = 1) { catalog.loadTable(tableIdentifier) }
    }

    @Test
    fun testConvertAirbyteRecordToIcebergRecord() {
        val descriptor = DestinationStream.Descriptor(namespace = "namespace", name = "name")
        val airbyteStream =
            DestinationStream(
                descriptor = descriptor,
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
            DestinationRecord(
                stream = airbyteStream.descriptor,
                data =
                    ObjectValue(
                        linkedMapOf("id" to IntegerValue(42L), "name" to StringValue("John Doe"))
                    ),
                emittedAtMs = System.currentTimeMillis(),
                meta = DestinationRecord.Meta(),
                serialized = "{\"id\":42, \"name\":\"John Doe\"}"
            )
        val pipeline = ParquetMapperPipelineFactory().create(airbyteStream)
        val columns =
            mutableListOf(
                Types.NestedField.required(1, "id", Types.IntegerType.get()),
                Types.NestedField.required(2, "name", Types.StringType.get()),
            )
        val schema = Schema(columns)
        val icebergRecord =
            IcebergUtil.toRecord(
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
    fun testCatalogProperties() {
        val awsAccessKey = "access-key"
        val awsSecretAccessKey = "secret-access-key"
        val nessieAccessToken = "nessie-access-token"
        val nessieServerUri = "http://localhost:8080"
        val warehouseLocation = "s3://test/"
        val s3BucketName = "test"
        val s3Endpoint = "http://localhost:9000"
        val awsAccessKeyConfiguration =
            AWSAccessKeyConfiguration(
                accessKeyId = awsAccessKey,
                secretAccessKey = awsSecretAccessKey,
            )
        val nessieServerConfiguration =
            NessieServerConfiguration(
                serverUri = nessieServerUri,
                accessToken = nessieAccessToken,
                warehouseLocation = warehouseLocation,
                mainBranchName = "main",
            )
        val s3BucketConfiguration =
            S3BucketConfiguration(
                s3BucketName = s3BucketName,
                s3BucketRegion = S3BucketRegion.`us-east-1`,
                s3Endpoint = s3Endpoint,
            )
        val configuration =
            IcebergV2Configuration(
                awsAccessKeyConfiguration = awsAccessKeyConfiguration,
                nessieServerConfiguration = nessieServerConfiguration,
                s3BucketConfiguration = s3BucketConfiguration,
            )
        val catalogProperties =
            IcebergUtil.toCatalogProperties(icebergConfiguration = configuration)
        assertEquals(ICEBERG_CATALOG_TYPE_NESSIE, catalogProperties[ICEBERG_CATALOG_TYPE])
        assertEquals(nessieServerUri, catalogProperties[URI])
        assertEquals(warehouseLocation, catalogProperties[WAREHOUSE_LOCATION])
        assertEquals(S3FileIO::class.java.name, catalogProperties[FILE_IO_IMPL])
        assertEquals("main", catalogProperties["nessie.ref"])
        assertEquals(awsAccessKey, catalogProperties["s3.access-key-id"])
        assertEquals(awsSecretAccessKey, catalogProperties["s3.secret-access-key"])
        assertEquals(S3BucketRegion.`us-east-1`.toString(), catalogProperties["s3.region"])
        assertEquals(s3Endpoint, catalogProperties["s3.endpoint"])
        assertEquals("true", catalogProperties["s3.path-style-access"])
        assertEquals("BEARER", catalogProperties["nessie.authentication.type"])
        assertEquals(nessieAccessToken, catalogProperties["nessie.authentication.token"])
    }
}
