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
    val tmpTableId = TableIdentifier.of("edgao_test_namespace", "edgao_test_table_tmp")

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
//    catalog.createTable(tmpTableId, schema)
    val table = catalog.loadTable(tableId)
//    table.manageSnapshots().createBranch("airbyte_last_commit").commit()
    val tmpTable = catalog.loadTable(tmpTableId)








    // Sync 1 - write (and commit) data to a temp table, then crash
    // (note that we write files to the _real_ table's location - this is weird, but allowed)
    writeRecordToTable(tmpTable, table.location(), schema, structType, 32)
    // !!! let's say we crash here.

    // Sync 2 - when committing to the real table, also recover data from the temp table.
    // first: write new records to the same temp table as the previous sync
    writeRecordToTable(tmpTable, table.location(), schema, structType, 33)
    // second: find the last snapshot in the real table,
    // and append all files from later snapshots from the temp table.
    val s = table.snapshot(table.refs()["airbyte_last_commit"]!!.snapshotId())
    logger.info { "found previous snapshot ${s.snapshotId()} with timestamp ${s.timestampMillis()}" }
    val latestCommittedSnapshotTs = table.snapshot(table.refs()["airbyte_last_commit"]!!.snapshotId()).timestampMillis()
    val snapshotsToRecover = tmpTable.snapshots().filter { it.timestampMillis() >= latestCommittedSnapshotTs }
    val append = table.newAppend()
    for (snapshot in snapshotsToRecover) {
        logger.info { "adding snapshot ${snapshot.snapshotId()} from timestamp ${snapshot.timestampMillis()}" }
        val files = snapshot.addedDataFiles(tmpTable.io())
        for (file in files) {
            append.appendFile(file)
        }
    }
    val newSnapshot = append.apply()
    append.commit()
    logger.info { "fast forwarding to snapshot ID ${newSnapshot.snapshotId()} with timestamp ${newSnapshot.timestampMillis()}" }
    table.manageSnapshots().replaceBranch("airbyte_last_commit", newSnapshot.snapshotId()).commit()
}

private fun writeRecordToTable(
    tmpTable: Table,
    realTableLocation: String,
    schema: Schema,
    structType: Types.StructType,
    number: Int,
) {
    val structValue: GenericRecord = GenericRecord.create(structType)
    val dataWriter: DataWriter<GenericRecord> =
        Parquet.writeData(tmpTable.io().newOutputFile(realTableLocation + "/" + System.currentTimeMillis()))
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
    tmpTable.newAppend()
        .appendFile(dataWriter.toDataFile())
        .commit()
}
