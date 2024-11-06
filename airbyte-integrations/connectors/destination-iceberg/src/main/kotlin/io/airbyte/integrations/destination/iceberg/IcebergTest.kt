package io.airbyte.integrations.destination.iceberg

import java.net.URI
import java.time.OffsetDateTime
import java.util.UUID
import org.apache.iceberg.BaseMetastoreCatalog
import org.apache.iceberg.BaseMetastoreTableOperations
import org.apache.iceberg.CatalogProperties
import org.apache.iceberg.CatalogUtil
import org.apache.iceberg.DataFiles
import org.apache.iceberg.FileFormat
import org.apache.iceberg.PartitionSpec
import org.apache.iceberg.Schema
import org.apache.iceberg.StructLike
import org.apache.iceberg.Table
import org.apache.iceberg.TableMetadata
import org.apache.iceberg.TableOperations
import org.apache.iceberg.aws.s3.S3FileIO
import org.apache.iceberg.catalog.Namespace
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.data.Record
import org.apache.iceberg.data.parquet.GenericParquetWriter
import org.apache.iceberg.io.FileIO
import org.apache.iceberg.io.LocationProvider
import org.apache.iceberg.parquet.Parquet
import org.apache.iceberg.types.Types
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials
import software.amazon.awssdk.regions.Region
import software.amazon.awssdk.services.s3.S3Client
import software.amazon.awssdk.services.s3.model.CreateBucketRequest
import software.amazon.awssdk.services.s3.model.HeadBucketRequest
import software.amazon.awssdk.services.s3.model.ListObjectsV2Request

const val WAREHOUSE_LOCATION = "warehouse"
const val S3_SCHEME = "s3://"

fun main(args: Array<String>) {
    val s3Client = S3Client
        .builder()
        .serviceConfiguration {
            it.chunkedEncodingEnabled(false)
            it.pathStyleAccessEnabled(true)
        }
        .credentialsProvider { AwsBasicCredentials.create(args[1], args[2]) }
        .endpointOverride(URI(args[0]))
        // The region isn't actually used but is required.
        // Set to us-east-1 based on https://github.com/minio/minio/discussions/15063.
        .region(Region.US_EAST_1)
        .build()

    val catalogProperties = mapOf(
        CatalogProperties.WAREHOUSE_LOCATION to WAREHOUSE_LOCATION
    )

    val s3Catalog = S3Catalog(s3Client=s3Client)
    s3Catalog.initialize(name="catalog_name", properties=catalogProperties)

    val spec = PartitionSpec.unpartitioned()
    val schema = Schema(
        Types.NestedField.required(1, "id", Types.IntegerType.get()),
        Types.NestedField.required(2, "name", Types.StringType.get()),
        Types.NestedField.required(3, "timestamp", Types.TimestampType.withZone()),
    )
    val tableIdentifier = TableIdentifier.of("default", "my_table")
    val table = getTable(tableIdentifier=tableIdentifier, catalog=s3Catalog, schema=schema, spec=spec)

    val records = (1..10).map {
        val record = GenericRecord.create(schema)
        record.set(0, it)
        record.set(1, "name$it")
        record.set(2, OffsetDateTime.now())
        record
    }.toMutableList() as List<Record>

    val filename = table.locationProvider().newDataLocation("${UUID.randomUUID()}.parquet")

    table.io().use { io ->
        val outputFile = io.newOutputFile(filename)
        val appender = Parquet.write(outputFile)
            .schema(schema)
            .createWriterFunc(GenericParquetWriter::buildWriter)
            .build<Record>()

        appender.use {
            it.addAll(records)
        }

        val dataFile = DataFiles.builder(spec)
            .withPath(filename)
            .withFormat(FileFormat.PARQUET)
            .withFileSizeInBytes(appender.length())
            .withRecordCount(records.size.toLong())
            .build()

        table.newAppend().appendFile(dataFile).commit()
    }
}

fun getTable(tableIdentifier: TableIdentifier, catalog: S3Catalog,
             schema: Schema, spec: PartitionSpec): Table {
    return if(!catalog.tableExists(tableIdentifier)) {
        catalog.createTable(tableIdentifier, schema, spec)
    } else {
        catalog.loadTable(tableIdentifier)
    }
}

class S3TableOperations(val s3Client: S3Client,
                        val tableIdentifier: TableIdentifier,
                        val bucketName: String): BaseMetastoreTableOperations() {
    override fun io(): FileIO {
        return S3FileIO({ s3Client })
    }

    override fun tableName(): String {
        return "${tableIdentifier.namespace()}/${tableIdentifier.name()}"
    }

    override fun doRefresh() {
        requestRefresh()
        val objects = s3Client.listObjectsV2(ListObjectsV2Request.builder()
            .bucket(bucketName)
            .prefix("${buildPrefix(identifier = tableIdentifier)}/metadata")
            .build())
        if (objects.contents().isNotEmpty()) {
            val metadataFile = objects.contents().last { !it.key().endsWith(".avro") }
            refreshFromMetadataLocation("$S3_SCHEME$bucketName/${metadataFile.key()}")
        } else {
            disableRefresh()
        }
    }

    override fun doCommit(base: TableMetadata?, metadata: TableMetadata?) {
        val newVersion =  currentVersion() + 1
        writeNewMetadata(metadata, newVersion)
    }

    override fun metadataFileLocation(filename: String): String {
        return super.metadataFileLocation(filename)
    }

    override fun locationProvider(): LocationProvider {
        return S3LocationProvider(basePath=
            buildPath(location=bucketName, identifier = tableIdentifier))
    }
}

class S3Catalog(val s3Client: S3Client): BaseMetastoreCatalog() {
    private lateinit var catalogName: String
    private lateinit var warehouseLocation: String

    override fun initialize(name: String, properties: Map<String, String>) {
        catalogName = name
        warehouseLocation = properties.getOrDefault(CatalogProperties.WAREHOUSE_LOCATION,
            WAREHOUSE_LOCATION)
        createBucketIfNotExists()
    }

    override fun name(): String {
        return catalogName
    }

    override fun createTable(
        identifier: TableIdentifier,
        schema: Schema,
        spec: PartitionSpec
    ): Table {
        return super.createTable(identifier, schema, spec,
            "$S3_SCHEME${buildPath(location = warehouseLocation, identifier = identifier)}",
            emptyMap())
    }

    override fun listTables(namespace: Namespace): List<TableIdentifier> {
//        return s3Client.listObjects(ListObjectsRequest.builder().bucket(warehouseLocation).prefix("$catalogName/${namespace.levels().first()}").build()).contents().filter { it.key().startsWith(namespace.toString()) }.map { toTableIdentifier(it) }
        return emptyList()
    }

    override fun dropTable(tableIdentifier: TableIdentifier, purge: Boolean): Boolean {
        try {
            val tableOperations = newTableOps(tableIdentifier)
            val tableMetadata = tableOperations.current()
            tableOperations.io().use { io ->
                CatalogUtil.dropTableData(io, tableMetadata)
            }
            return true
        } catch(e: Exception) {
            return false
        }
    }

    override fun renameTable(from: TableIdentifier, to: TableIdentifier) {
//        val fromIo = newTableOps(from).io()
//        val fromFile = fromIo.newInputFile(toS3Uri(tableIdentifier=from, catalog=name()))
//        val toFile = newTableOps(to).io().newOutputFile(toS3Uri(tableIdentifier=to, catalog=name()))
//        val outputStream = toFile.create()
//        outputStream.use {
//            IoUtils.copy(ByteArrayInputStream(fromFile.newStream().readAllBytes()), it)
//        }
//        fromIo.deleteFile(toS3Uri(tableIdentifier=from, catalog=name()))
    }

    override fun newTableOps(tableIdentifier: TableIdentifier): TableOperations {
        return S3TableOperations(s3Client=s3Client, tableIdentifier = tableIdentifier, bucketName=warehouseLocation)
    }

    override fun defaultWarehouseLocation(tableIdentifier: TableIdentifier): String {
        return "$S3_SCHEME${buildPath(location=warehouseLocation, identifier = tableIdentifier)}"
    }

    private fun createBucketIfNotExists() {
        if (!doesBucketExist(bucketName=warehouseLocation)) {
            val createBucketRequest = CreateBucketRequest.builder().bucket(warehouseLocation).build()
            s3Client.createBucket(createBucketRequest)
        }
    }

    private fun doesBucketExist(bucketName: String): Boolean {
        val headBucketRequest = HeadBucketRequest.builder().bucket(bucketName).build()
        return try {
            s3Client.headBucket(headBucketRequest)
            true
        } catch (e: Exception) {
            false
        }
    }
}

class S3LocationProvider(val basePath: String): LocationProvider {
    override fun newDataLocation(filename: String): String {
        return "$S3_SCHEME$basePath/data/$filename"
    }

    override fun newDataLocation(
        spec: PartitionSpec,
        partitionData: StructLike,
        filename: String
    ): String {
        return newDataLocation(filename=filename)
    }
}

private fun buildPath(location: String, identifier: TableIdentifier) =
    "${location}/${buildPrefix(identifier=identifier)}"

private fun buildPrefix(identifier: TableIdentifier) =
    "${identifier.namespace().levels().first()}/${identifier.name()}"
