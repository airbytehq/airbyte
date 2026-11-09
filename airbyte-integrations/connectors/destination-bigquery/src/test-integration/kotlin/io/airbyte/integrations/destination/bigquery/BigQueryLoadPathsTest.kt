/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import com.google.api.gax.core.FixedCredentialsProvider
import com.google.auth.oauth2.GoogleCredentials
import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryOptions
import com.google.cloud.bigquery.JobInfo
import com.google.cloud.bigquery.QueryJobConfiguration
import com.google.cloud.bigquery.Schema
import com.google.cloud.bigquery.StandardTableDefinition
import com.google.cloud.bigquery.TableId
import com.google.cloud.bigquery.TableInfo
import com.google.cloud.bigquery.storage.v1.BigQueryWriteClient
import com.google.cloud.bigquery.storage.v1.BigQueryWriteSettings
import com.google.cloud.bigquery.storage.v1.TableName
import com.google.cloud.storage.BlobId
import com.google.cloud.storage.BlobInfo
import com.google.cloud.storage.Storage
import com.google.cloud.storage.StorageOptions
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.file.object_storage.ObjectStorageFormattingWriter
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.orchestration.db.TableName as CdkTableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DefaultDirectLoadTableSqlOperations
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.integrations.destination.bigquery.BigQueryDestinationTestUtils.GCS_STAGING_CONFIG
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfigurationFactory
import io.airbyte.integrations.destination.bigquery.spec.BigquerySpecification
import io.airbyte.integrations.destination.bigquery.spec.GcsStagingConfiguration
import io.airbyte.integrations.destination.bigquery.write.bulk_loader.AllAirbyteTypes
import io.airbyte.integrations.destination.bigquery.write.bulk_loader.BigQueryBulkLoader
import io.airbyte.integrations.destination.bigquery.write.bulk_loader.BigQueryLoadRows
import io.airbyte.integrations.destination.bigquery.write.bulk_loader.BigQueryObjectStorageFormattingWriter as CsvWriter
import io.airbyte.integrations.destination.bigquery.write.bulk_loader.ProtoToBigQueryObjectStorageFormattingWriter as ProtoCsvWriter
import io.airbyte.integrations.destination.bigquery.write.bulk_loader.bigQueryAvroFormattingWriter
import io.airbyte.integrations.destination.bigquery.write.storage_write.BigQueryProtoRows
import io.airbyte.integrations.destination.bigquery.write.storage_write.BigQueryStorageWriteLoader
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.BigQueryDatabaseHandler
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables.BigqueryDirectLoadSqlGenerator
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables.BigqueryDirectLoadSqlTableOperations
import java.io.ByteArrayOutputStream
import java.io.OutputStream
import java.nio.file.Files
import java.nio.file.Path
import java.util.UUID
import java.util.zip.GZIPOutputStream
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.EnumSource

/**
 * Every Airbyte type lands in BigQuery the same through an Avro staging file and through the
 * Storage Write API as through a gzipped CSV staging file: the destination's own writers, load job
 * configurations and Storage Write API loader, against the dataset and bucket of the GCS staging
 * test config. Without credentials_json in it, the test runs as the application default
 * credentials.
 */
class BigQueryLoadPathsTest {
    // Parsed here: BigQueryDestinationTestUtils also reads the standard insert config.
    private val config: BigqueryConfiguration =
        BigqueryConfigurationFactory()
            .make(
                Jsons.readValue(
                    Files.readString(Path.of(GCS_STAGING_CONFIG)),
                    BigquerySpecification::class.java,
                ),
            )
    private val credentials =
        config.credentialsJson?.let { GoogleCredentials.fromStream(it.byteInputStream()) }
            ?: GoogleCredentials.getApplicationDefault()
    private val bigQuery: BigQuery =
        BigQueryOptions.newBuilder()
            .setProjectId(config.projectId)
            .setCredentials(credentials)
            .build()
            .service
    private val storage: Storage =
        StorageOptions.newBuilder()
            .setProjectId(config.projectId)
            .setCredentials(credentials)
            .build()
            .service
    private val writeClient: BigQueryWriteClient =
        BigQueryWriteClient.create(
            BigQueryWriteSettings.newBuilder()
                .setCredentialsProvider(FixedCredentialsProvider.create(credentials))
                .build(),
        )
    private val gcs = (config.loadingMethod as GcsStagingConfiguration).gcsClientConfig
    private val run = "load_paths_test_${UUID.randomUUID().toString().take(8)}"
    private val tables = mutableListOf<TableId>()
    private val objects = mutableListOf<BlobId>()

    @AfterEach
    fun cleanUp() {
        objects.forEach { storage.delete(it) }
        tables.forEach { bigQuery.delete(it) }
        writeClient.close()
    }

    @ParameterizedTest
    @EnumSource(DataChannelFormat::class, names = ["JSONL", "PROTOBUF"])
    fun `Avro staging and the Storage Write API load every Airbyte type as CSV staging does`(
        format: DataChannelFormat,
    ) {
        val stream = AllAirbyteTypes.stream()
        val suffix = format.name.lowercase()

        val csv = ByteArrayOutputStream()
        GZIPOutputStream(csv).use { gzip ->
            write(
                gzip,
                when (format) {
                    DataChannelFormat.PROTOBUF -> ProtoCsvWriter(stream, gzip)
                    else -> CsvWriter(stream, gzip)
                },
                stream,
                format,
            )
        }
        val csvTable = stage("csv_$suffix", "csv.gz", csv.toByteArray(), stream)

        val avro = ByteArrayOutputStream()
        write(
            avro,
            bigQueryAvroFormattingWriter(stream, AllAirbyteTypes.columnNameMapping, format, avro),
            stream,
            format,
        )
        val avroTable = stage("avro_$suffix", "avro", avro.toByteArray(), stream)

        val writeTable = table("write_$suffix", stream)
        writeThroughStorageWriteApi(
            writeTable,
            stream,
            format,
            AllAirbyteTypes.records(stream, format),
        )

        val csvRows = rows(csvTable)
        val avroRows = rows(avroTable)
        val writeRows = rows(writeTable)
        assertEquals(AllAirbyteTypes.rows.size, avroRows.size)
        assertEquals(AllAirbyteTypes.rows.size, writeRows.size)
        // The CSV null marker is data only outside CSV.
        assertEquals(null, csvRows.getValue(3L).remove("str_col"))
        assertEquals(BigQueryConsts.NULL_MARKER, avroRows.getValue(3L).remove("str_col"))
        assertEquals(BigQueryConsts.NULL_MARKER, writeRows.getValue(3L).remove("str_col"))
        for (id in csvRows.keys) {
            assertEquals(csvRows.getValue(id), avroRows.getValue(id), "Avro, row $id")
            assertEquals(csvRows.getValue(id), writeRows.getValue(id), "Storage Write API, row $id")
        }
    }

    @Test
    fun `a row too large for an append request fails the batch and leaves nothing in the table`() {
        val stream = AllAirbyteTypes.stream()
        val table = table("oversized", stream)
        val large = "x".repeat(BigQueryStorageWriteLoader.MAX_ROW_BYTES.toInt() + 1024)
        val loader = storageWriteLoader(table, stream, DataChannelFormat.JSONL)
        val error =
            assertThrows<ConfigErrorException> {
                runBlocking {
                    AllAirbyteTypes.records(stream, DataChannelFormat.JSONL).forEach {
                        loader.accept(it)
                    }
                    loader.accept(
                        AllAirbyteTypes.record(
                            stream,
                            DataChannelFormat.JSONL,
                            mapOf("id" to "5", "str_col" to Jsons.writeValueAsString(large)),
                        ),
                    )
                }
            }
        loader.close()

        assertTrue(error.message!!.contains("GCS Staging"), error.message)
        assertEquals(0, rows(table).size)
    }

    @Test
    fun `a temp table emptied at the end of a sync takes the next sync's writes`() {
        val stream = AllAirbyteTypes.stream()
        val table = table("emptied", stream)
        val records = AllAirbyteTypes.records(stream, DataChannelFormat.JSONL)
        writeThroughStorageWriteApi(table, stream, DataChannelFormat.JSONL, records)

        runBlocking {
            tableOperations(emptiesDroppedTables = true)
                .dropTable(CdkTableName(table.dataset, table.table))
        }
        assertEquals(0, rows(table).size)

        writeThroughStorageWriteApi(table, stream, DataChannelFormat.JSONL, records.take(2))
        assertEquals(setOf(1L, 2L), rows(table).keys)
    }

    @Test
    fun `a batch closed without finish leaves nothing in the table`() {
        val stream = AllAirbyteTypes.stream()
        val table = table("abandoned", stream)
        val loader = storageWriteLoader(table, stream, DataChannelFormat.JSONL)
        val megabyte = Jsons.writeValueAsString("x".repeat(1024 * 1024))
        runBlocking {
            // More than one request's worth, so rows were sent before the batch is abandoned.
            repeat(12) {
                loader.accept(
                    AllAirbyteTypes.record(
                        stream,
                        DataChannelFormat.JSONL,
                        mapOf("id" to "$it", "str_col" to megabyte),
                    ),
                )
            }
        }
        loader.close()

        assertEquals(0, rows(table).size)
    }

    private fun tableOperations(emptiesDroppedTables: Boolean) =
        BigqueryDirectLoadSqlTableOperations(
            DefaultDirectLoadTableSqlOperations(
                BigqueryDirectLoadSqlGenerator(config.projectId, config.cdcDeletionMode),
                BigQueryDatabaseHandler(
                    bigQuery,
                    bigQuery,
                    config.datasetLocation.region,
                    config.jobProjectId,
                ),
            ),
            bigQuery,
            config.jobProjectId,
            config.datasetLocation.region,
            emptiesDroppedTables,
        )

    private fun table(name: String, stream: DestinationStream): TableId {
        val table = TableId.of(config.projectId, config.datasetId, "${run}_$name")
        bigQuery.create(TableInfo.of(table, StandardTableDefinition.of(schema(stream))))
        tables += table
        return table
    }

    private fun schema(stream: DestinationStream): Schema =
        BigQueryRecordFormatter.getDirectLoadSchema(stream, AllAirbyteTypes.columnNameMapping)

    private fun stage(
        name: String,
        ext: String,
        bytes: ByteArray,
        stream: DestinationStream,
    ): TableId {
        val table = table(name, stream)
        val blob = BlobId.of(gcs.gcsBucketName, "${gcs.path.trim('/')}/$run/$name.$ext")
        objects += blob
        storage.create(BlobInfo.newBuilder(blob).build(), bytes)
        val uri = "gs://${blob.bucket}/${blob.name}"
        val job =
            bigQuery
                .create(
                    JobInfo.of(BigQueryBulkLoader.loadJobConfiguration(table, uri, schema(stream))),
                )
                .waitFor()
        check(job.status.error == null) { "load of $uri failed: ${job.status.executionErrors}" }
        return table
    }

    private fun storageWriteLoader(
        table: TableId,
        stream: DestinationStream,
        format: DataChannelFormat,
    ): BigQueryStorageWriteLoader {
        val loadRows = BigQueryLoadRows.of(stream, AllAirbyteTypes.columnNameMapping, format)
        return BigQueryStorageWriteLoader(
            writeClient,
            TableName.of(table.project, table.dataset, table.table),
            BigQueryProtoRows(loadRows),
        )
    }

    private fun writeThroughStorageWriteApi(
        table: TableId,
        stream: DestinationStream,
        format: DataChannelFormat,
        records: List<DestinationRecordRaw>,
    ) {
        storageWriteLoader(table, stream, format).use { loader ->
            runBlocking {
                records.forEach { loader.accept(it) }
                loader.finish()
            }
        }
    }

    private fun write(
        out: OutputStream,
        writer: ObjectStorageFormattingWriter,
        stream: DestinationStream,
        format: DataChannelFormat,
    ) {
        AllAirbyteTypes.records(stream, format).forEach { writer.accept(it) }
        writer.flush()
        writer.close()
        out.flush()
    }

    /** Each row as column name to the value BigQuery returns as text, by id. */
    private fun rows(table: TableId): Map<Long, MutableMap<String, String?>> {
        val result =
            bigQuery.query(
                QueryJobConfiguration.of(
                    "SELECT * FROM `${table.project}`.`${table.dataset}`.`${table.table}`",
                ),
            )
        val fields = result.schema!!.fields
        return result.iterateAll().associate { row ->
            val values =
                fields.associateTo(linkedMapOf()) { field ->
                    val value = row.get(field.name)
                    field.name to if (value.isNull) null else value.stringValue
                }
            values["id"]!!.toLong() to values
        }
    }
}
