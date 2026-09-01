/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.dataflow

import com.amazonaws.auth.AWSStaticCredentialsProvider
import com.amazonaws.auth.BasicAWSCredentials
import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.AmazonS3ClientBuilder
import com.amazonaws.services.s3.model.ObjectMetadata
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.csv.toCsvValue
import io.airbyte.cdk.load.data.json.toJson
import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.integrations.destination.redshift_v2.spec.S3StagingConfiguration
import io.airbyte.integrations.destination.redshift_v2.sql.RedshiftDataType
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.OutputStreamWriter
import java.nio.charset.StandardCharsets
import java.time.Clock
import java.util.UUID
import java.util.zip.GZIPOutputStream
import javax.sql.DataSource

private val log = KotlinLogging.logger {}

/**
 * Accumulates and flushes records to Redshift via S3 staging and COPY command. Uses CSV format with
 * proper quoting for staging files.
 *
 * NOT a @Singleton - created per-stream by AggregateFactory.
 */
class RedshiftStagingAggregate(
    private val tableName: TableName,
    private val dataSource: DataSource,
    private val s3Config: S3StagingConfiguration,
    private val clock: Clock,
    private val finalSchema: Map<String, ColumnType>,
) : Aggregate {

    // Columns that are SUPER type need JSON serialization for all values (including primitives)
    private val superColumns: Set<String> by lazy {
        finalSchema.filter { it.value.type == RedshiftDataType.SUPER.typeName }.keys
    }

    private val buffer = mutableListOf<Map<String, AirbyteValue>>()
    private var columnOrder: List<String>? = null
    private val s3Client: AmazonS3 by lazy { createS3Client() }

    override fun accept(record: RecordDTO) {
        if (columnOrder == null) {
            columnOrder = record.fields.keys.toList()
        }
        buffer.add(record.fields)
    }

    override suspend fun flush() {
        if (buffer.isEmpty()) return

        val columns = columnOrder ?: return
        val s3Key = generateS3Key()

        try {
            log.info {
                "Flushing ${buffer.size} records to S3: s3://${s3Config.s3BucketName}/$s3Key"
            }

            // Write records to gzipped CSV format
            val csvData = writeToCsv(columns)

            // Upload to S3 as binary (gzipped data)
            val metadata =
                ObjectMetadata().apply {
                    contentLength = csvData.size.toLong()
                    contentType = "application/gzip"
                }
            s3Client.putObject(
                s3Config.s3BucketName,
                s3Key,
                ByteArrayInputStream(csvData),
                metadata
            )

            // Execute COPY command
            executeCopy(columns, s3Key)

            log.info { "Successfully loaded ${buffer.size} records via COPY" }
        } finally {
            // Cleanup S3 file if configured to purge
            if (s3Config.purgeStagingData) {
                try {
                    s3Client.deleteObject(s3Config.s3BucketName, s3Key)
                } catch (e: Exception) {
                    log.warn(e) { "Failed to cleanup staging file: $s3Key" }
                }
            }
            buffer.clear()
        }
    }

    /**
     * Writes records to CSV format, gzipped. Uses the CDK's toCsvValue() for proper type
     * conversion. For SUPER columns, uses JSON serialization for ALL values (including primitives).
     */
    private fun writeToCsv(columns: List<String>): ByteArray {
        val baos = ByteArrayOutputStream()
        GZIPOutputStream(baos).use { gzip ->
            OutputStreamWriter(gzip, StandardCharsets.UTF_8).use { writer ->
                // Write header
                writer.write(columns.joinToString(",") { "\"$it\"" })
                writer.write("\n")

                // Write data rows
                buffer.forEach { record ->
                    val row =
                        columns.map { col ->
                            val value = record[col]
                            // For SUPER columns, JSON-serialize ALL values (including primitives
                            // like strings)
                            // This ensures that a StringValue("foo") becomes "\"foo\"" in the CSV,
                            // which Redshift's SUPER type can parse as valid JSON.
                            if (col in superColumns && value != null) {
                                formatCsvField(value.toJson().serializeToString())
                            } else {
                                formatCsvField(value.toCsvValue())
                            }
                        }
                    writer.write(row.joinToString(","))
                    writer.write("\n")
                }
            }
        }
        return baos.toByteArray()
    }

    /** Formats a value for CSV output with proper quoting and escaping. */
    private fun formatCsvField(value: Any): String {
        val stringValue = value.toString()
        // Always quote strings, escape internal quotes by doubling them
        val escaped = stringValue.replace("\"", "\"\"").replace("\u0000", " ")
        return "\"$escaped\""
    }

    private fun executeCopy(columns: List<String>, s3Key: String) {
        val columnList = columns.joinToString(", ") { "\"$it\"" }
        val s3Path = getFullS3Path(s3Key)

        val copyQuery =
            """
            COPY "${tableName.namespace}"."${tableName.name}" ($columnList)
            FROM '$s3Path'
            CREDENTIALS 'aws_access_key_id=${s3Config.accessKeyId};aws_secret_access_key=${s3Config.secretAccessKey}'
            CSV GZIP
            IGNOREHEADER 1
            REGION '${s3Config.s3BucketRegion.ifEmpty { "us-east-1" }}'
            TIMEFORMAT 'auto'
            EMPTYASNULL
            STATUPDATE OFF
        """.trimIndent()

        dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                log.debug {
                    "Executing COPY command for table ${tableName.namespace}.${tableName.name}"
                }
                statement.execute(copyQuery)
            }
        }
    }

    private fun generateS3Key(): String {
        val basePath = s3Config.s3BucketPath?.trimEnd('/') ?: ""
        val timestamp = clock.millis()
        val uuid = UUID.randomUUID()
        val filename =
            "airbyte_staging_${tableName.namespace}_${tableName.name}_${timestamp}_$uuid.csv.gz"

        return if (basePath.isNotEmpty()) {
            "$basePath/$filename"
        } else {
            filename
        }
    }

    private fun getFullS3Path(s3Key: String): String {
        return "s3://${s3Config.s3BucketName}/$s3Key"
    }

    private fun createS3Client(): AmazonS3 {
        return AmazonS3ClientBuilder.standard()
            .withCredentials(
                AWSStaticCredentialsProvider(
                    BasicAWSCredentials(s3Config.accessKeyId, s3Config.secretAccessKey)
                )
            )
            .withRegion(s3Config.s3BucketRegion.ifEmpty { "us-east-1" })
            .build()
    }
}
