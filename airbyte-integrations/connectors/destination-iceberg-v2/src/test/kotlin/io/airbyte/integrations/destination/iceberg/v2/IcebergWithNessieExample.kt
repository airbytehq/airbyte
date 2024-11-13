package io.airbyte.integrations.destination.iceberg.v2

import org.apache.hadoop.conf.Configuration
import org.apache.iceberg.*
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.data.Record
import org.apache.iceberg.data.parquet.GenericParquetWriter
import org.apache.iceberg.nessie.NessieCatalog
import org.apache.iceberg.parquet.Parquet
import org.apache.iceberg.types.Types
import org.apache.parquet.schema.MessageType
import java.io.IOException
import java.util.*
import org.junit.jupiter.api.Test


class IcebergWithNessieExample {

    @Throws(IOException::class)
    fun writeToParquet() {
        val catalog = nessieCatalog()
        val schema = schema()
        val spec = partitionSpec()

        val tableIdentifier = TableIdentifier.of("default", "my_table")
        val table: Table = table(catalog, tableIdentifier, schema, spec)

        val records: MutableList<Record> = ArrayList()
        val record = GenericRecord.create(schema)


        val rec1: Record = record.copy()
        rec1.setField("id", 1)
        rec1.setField("data", "foo")
        records.add(rec1)

        val rec2: Record = record.copy()
        rec2.setField("id", 2)
        rec2.setField("data", "bar")
        records.add(rec2)

        val filename = table.locationProvider().newDataLocation(UUID.randomUUID().toString() + ".parquet")
        val outputFile = table.io().newOutputFile(filename)

        val appender = Parquet.write(outputFile)
                .schema(schema)
                .createWriterFunc { type: MessageType? -> GenericParquetWriter.buildWriter(type) }
                .build<Record>()

        appender.use { it.addAll(records) }

        val dataFile = DataFiles.builder(spec)
                .withPath(filename)
                .withFormat(FileFormat.PARQUET)
                .withFileSizeInBytes(appender.length())
                .withRecordCount(records.size.toLong())
                .build()

        table.newAppend()
                .appendFile(dataFile)
                .commit()


        println("Data written successfully to Iceberg table in MinIO.")
    }

    private fun partitionSpec(): PartitionSpec? = PartitionSpec.unpartitioned()

    private fun schema() = Schema(
            Types.NestedField.required(1, "id", Types.IntegerType.get()),
            Types.NestedField.optional(2, "data", Types.StringType.get())
    )

    private fun table(catalog: NessieCatalog, tableIdentifier: TableIdentifier, schema: Schema, spec: PartitionSpec?): Table {
        if (!catalog.tableExists(tableIdentifier)) {
            if (!catalog.namespaceExists(tableIdentifier.namespace())) {
                catalog.createNamespace(tableIdentifier.namespace())
            }
            return catalog.createTable(tableIdentifier, schema, spec)
        } else {
            return catalog.loadTable(tableIdentifier)
        }
    }

    private fun nessieCatalog(): NessieCatalog {
        val catalogProperties: MutableMap<String, String> = HashMap()

        catalogProperties[CatalogProperties.URI] = "http://localhost:19120/api/v1"
        catalogProperties["nessie.ref"] = "main"
        catalogProperties["nessie.authentication.type"] = "BEARER"
        catalogProperties["nessie.authentication.token"] = getToken()


        catalogProperties[CatalogProperties.WAREHOUSE_LOCATION] = "s3://demobucket/"

        catalogProperties[CatalogProperties.FILE_IO_IMPL] = "org.apache.iceberg.aws.s3.S3FileIO"

        catalogProperties["s3.access-key-id"] = "minioadmin"
        catalogProperties["s3.secret-access-key"] = "minioadmin"
        catalogProperties["s3.region"] = "us-east-1"
        catalogProperties["s3.endpoint"] = "http://localhost:9002"
        catalogProperties["s3.path-style-access"] = "true" // Required for MinIO
        catalogProperties["s3.disableChunkedEncoding"] = "true"

        val catalog = NessieCatalog()
        catalog.setConf(Configuration()) // Required for S3FileIO
        catalog.initialize("nessie", catalogProperties)
        return catalog
    }

    private fun getToken() = "<put_your_token>"

    @Test
     fun test() {
        val icebergWithNessieExample = IcebergWithNessieExample()
        icebergWithNessieExample.writeToParquet()
     }
}
