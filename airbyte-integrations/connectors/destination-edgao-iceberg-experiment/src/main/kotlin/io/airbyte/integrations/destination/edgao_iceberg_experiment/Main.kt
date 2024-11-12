package io.airbyte.integrations.destination.edgao_iceberg_experiment

import io.airbyte.cdk.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import kotlinx.coroutines.runBlocking
import org.apache.iceberg.CatalogProperties
import org.apache.iceberg.PartitionSpec
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.aws.glue.GlueCatalog
import org.apache.iceberg.aws.s3.S3FileIOProperties
import org.apache.iceberg.catalog.Namespace
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.data.parquet.GenericParquetWriter
import org.apache.iceberg.io.DataWriter
import org.apache.iceberg.parquet.Parquet
import org.apache.iceberg.types.Types
import java.io.File
import java.time.OffsetDateTime

private val logger = KotlinLogging.logger {}

fun main(): Unit = runBlocking {
    val glueConfig = Jsons.readTree(File("/Users/edgao/code/airbyte/airbyte-integrations/connectors/destination-edgao-iceberg-experiment/secrets/glue.json"))
    val accessKeyId = glueConfig["storage_config"]["access_key_id"].asText()
    val secretAccessKey = glueConfig["storage_config"]["secret_access_key"].asText()

    val catalog = GlueCatalog()
    catalog.initialize(
        "iceberg",
        mapOf(
            CatalogProperties.CATALOG_IMPL to "org.apache.iceberg.aws.glue.GlueCatalog",
            CatalogProperties.WAREHOUSE_LOCATION to "s3://ab-destination-iceberg/edgao_test_via_iceberg",
            CatalogProperties.FILE_IO_IMPL to "org.apache.iceberg.aws.s3.S3FileIO",
            S3FileIOProperties.ACCESS_KEY_ID to accessKeyId,
            S3FileIOProperties.SECRET_ACCESS_KEY to secretAccessKey,

//            CatalogProperties.CATALOG_IMPL to "org.apache.iceberg.rest.RESTCatalog",
//            CatalogProperties.URI to "http://localhost:8181/",
        ),
    )
    val namespaceId = Namespace.of("edgao_test_namespace")
    val tableId = TableIdentifier.of("edgao_test_namespace", "edgao_test_table")
    val incomingDataBranchName = "_airbyte_incoming_data"

    val structType = Types.StructType.of(
        Types.NestedField.required(4, "bar", Types.IntegerType.get()),
    )
    val schema =
        Schema(
            Types.NestedField.required(1, "uuid", Types.StringType.get()),
            Types.NestedField.required(2, "updated_at", Types.TimestampType.withZone()),
            Types.NestedField.required(
                3,
                "foo",
                structType,
            ),
        )

    // TODO create if not exists (... or just wrap in a try catch)
//    catalog.createNamespace(namespaceId)
//    catalog.createTable(tableId, schema)
    val table = catalog.loadTable(tableId)
//    table.manageSnapshots().createBranch(incomingDataBranchName).commit()









    // Sync 1 - write (and commit) data to a separate branch, then crash
    writeRecordToTable(table, incomingDataBranchName, schema, structType, 2)
    // !!! let's say we crash here.

    // Sync 2
    // first: write new records to the same branch as the previous sync
    writeRecordToTable(table, incomingDataBranchName, schema, structType, 3)
    // and at the end of the sync, fast-forward the main branch to catch up with the temp branch
    table.manageSnapshots().fastForwardBranch("main", incomingDataBranchName).commit()
}

private fun writeRecordToTable(
    table: Table,
    branchName: String,
    schema: Schema,
    structType: Types.StructType,
    number: Int,
) {
    val structValue: GenericRecord = GenericRecord.create(structType)
    val dataWriter: DataWriter<GenericRecord> =
        Parquet.writeData(table.io().newOutputFile(table.location() + "/" + System.currentTimeMillis()))
            .schema(schema)
            .createWriterFunc(GenericParquetWriter::buildWriter)
            .overwrite()
            .withSpec(PartitionSpec.unpartitioned())
            .build()
    dataWriter.use { writer ->
        writer.write(
            GenericRecord.create(schema).copy(
                mapOf(
                    "uuid" to "4f37e94e-741e-40fc-9e3f-f75f5ffacaba",
                    "updated_at" to OffsetDateTime.now(),
                    "foo" to structValue.copy(mapOf("bar" to number)),
                ),
            )
        )
    }
    table.newAppend()
        .toBranch(branchName)
        .appendFile(dataWriter.toDataFile())
        .commit()
}
