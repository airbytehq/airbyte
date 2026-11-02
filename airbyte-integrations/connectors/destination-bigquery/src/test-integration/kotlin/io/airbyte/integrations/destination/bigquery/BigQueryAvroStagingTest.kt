/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import com.google.auth.oauth2.GoogleCredentials
import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryOptions
import com.google.cloud.bigquery.JobInfo
import com.google.cloud.bigquery.QueryJobConfiguration
import com.google.cloud.bigquery.Schema
import com.google.cloud.bigquery.StandardTableDefinition
import com.google.cloud.bigquery.TableId
import com.google.cloud.bigquery.TableInfo
import com.google.cloud.storage.BlobId
import com.google.cloud.storage.BlobInfo
import com.google.cloud.storage.Storage
import com.google.cloud.storage.StorageOptions
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.file.object_storage.ObjectStorageFormattingWriter
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.integrations.destination.bigquery.BigQueryDestinationTestUtils.GCS_STAGING_CONFIG
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfigurationFactory
import io.airbyte.integrations.destination.bigquery.spec.BigquerySpecification
import io.airbyte.integrations.destination.bigquery.spec.GcsStagingConfiguration
import io.airbyte.integrations.destination.bigquery.write.bulk_loader.AllAirbyteTypes
import io.airbyte.integrations.destination.bigquery.write.bulk_loader.BigQueryBulkLoader
import io.airbyte.integrations.destination.bigquery.write.bulk_loader.BigQueryObjectStorageFormattingWriter as CsvWriter
import io.airbyte.integrations.destination.bigquery.write.bulk_loader.ProtoToBigQueryObjectStorageFormattingWriter as ProtoCsvWriter
import io.airbyte.integrations.destination.bigquery.write.bulk_loader.bigQueryAvroFormattingWriter
import java.io.ByteArrayOutputStream
import java.io.OutputStream
import java.nio.file.Files
import java.nio.file.Path
import java.util.UUID
import java.util.zip.GZIPOutputStream
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.EnumSource

/**
 * Every Airbyte type lands in BigQuery the same from an Avro staging file as from a gzipped CSV
 * one: the destination's own writers and load job configurations, against the dataset and bucket of
 * the GCS staging test config. Without credentials_json in it, the test runs as the application
 * default credentials.
 */
class BigQueryAvroStagingTest {
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
    private val gcs = (config.loadingMethod as GcsStagingConfiguration).gcsClientConfig

    @ParameterizedTest
    @EnumSource(DataChannelFormat::class, names = ["JSONL", "PROTOBUF"])
    fun `Avro and CSV staging load every Airbyte type to the same rows`(format: DataChannelFormat) {
        val stream = AllAirbyteTypes.stream()
        val schema =
            BigQueryRecordFormatter.getDirectLoadSchema(stream, AllAirbyteTypes.columnNameMapping)
        val run =
            "avro_staging_test_${format.name.lowercase()}_${UUID.randomUUID().toString().take(8)}"
        val csvTable = TableId.of(config.projectId, config.datasetId, "${run}_csv")
        val avroTable = TableId.of(config.projectId, config.datasetId, "${run}_avro")
        val objects = mutableListOf<BlobId>()
        try {
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
            val avro = ByteArrayOutputStream()
            write(
                avro,
                bigQueryAvroFormattingWriter(
                    stream,
                    AllAirbyteTypes.columnNameMapping,
                    format,
                    avro,
                ),
                stream,
                format,
            )

            for ((table, ext, bytes) in
                listOf(
                    Triple(csvTable, "csv.gz", csv.toByteArray()),
                    Triple(avroTable, "avro", avro.toByteArray()),
                )) {
                bigQuery.create(TableInfo.of(table, StandardTableDefinition.of(schema)))
                val blob = BlobId.of(gcs.gcsBucketName, "${gcs.path.trim('/')}/$run/part.$ext")
                objects += blob
                storage.create(BlobInfo.newBuilder(blob).build(), bytes)
                load(table, "gs://${blob.bucket}/${blob.name}", schema)
            }

            val csvRows = rows(csvTable)
            val avroRows = rows(avroTable)
            assertEquals(AllAirbyteTypes.rows.size, avroRows.size)
            // The CSV null marker is data only in Avro.
            assertEquals(null, csvRows.getValue(3L).remove("str_col"))
            assertEquals(BigQueryConsts.NULL_MARKER, avroRows.getValue(3L).remove("str_col"))
            for (id in csvRows.keys) {
                assertEquals(csvRows.getValue(id), avroRows.getValue(id), "row $id")
            }
        } finally {
            objects.forEach { storage.delete(it) }
            bigQuery.delete(csvTable)
            bigQuery.delete(avroTable)
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

    private fun load(table: TableId, uri: String, schema: Schema) {
        val job =
            bigQuery
                .create(JobInfo.of(BigQueryBulkLoader.loadJobConfiguration(table, uri, schema)))
                .waitFor()
        check(job.status.error == null) { "load of $uri failed: ${job.status.executionErrors}" }
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
