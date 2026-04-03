/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.dataflow

import de.siegmar.fastcsv.writer.CsvWriter
import de.siegmar.fastcsv.writer.LineDelimiter
import de.siegmar.fastcsv.writer.QuoteStrategies
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.data.csv.toCsvValue
import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.dataflow.aggregate.StoreKey
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.directload.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.redshift_v2.spec.RedshiftV2Configuration
import io.airbyte.integrations.destination.redshift_v2.spec.S3StagingConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.time.Clock
import java.util.UUID
import java.util.concurrent.CompletableFuture
import java.util.zip.GZIPOutputStream
import javax.sql.DataSource
import software.amazon.awssdk.core.async.BlockingOutputStreamAsyncRequestBody
import software.amazon.awssdk.services.s3.S3AsyncClient
import software.amazon.awssdk.services.s3.model.PutObjectResponse

private val log = KotlinLogging.logger {}

private val metaColumns = Meta.COLUMN_NAMES.toList()
internal const val CSV_FIELD_SEPARATOR = ','
internal const val CSV_QUOTE_CHARACTER = '"'
internal val CSV_LINE_DELIMITER = LineDelimiter.LF
private const val CSV_WRITER_BUFFER_SIZE = 1024 * 1024 // 1 MB

/**
 * Accumulates and flushes records to Redshift via S3 staging and COPY command. Uses CSV format with
 * proper quoting for staging files.
 *
 * NOT a @Singleton - created per-stream by AggregateFactory.
 */
class RedshiftStagingAggregate(
    private val tableName: TableName,
    private val dataSource: DataSource,
    private val s3Client: S3AsyncClient,
    private val s3Config: S3StagingConfiguration,
    private val clock: Clock,
    columnSchema: ColumnSchema,
) : Aggregate {
    private val columns: List<String> = metaColumns + columnSchema.finalSchema.keys.toList()
    private val s3ObjectKey = generateS3Key()

    private lateinit var responseFuture: CompletableFuture<PutObjectResponse>
    private lateinit var csvPrinter: CsvWriter

    override fun accept(record: RecordDTO) {
        if (!this::csvPrinter.isInitialized) {
            val requestBody = BlockingOutputStreamAsyncRequestBody.builder().build()
            responseFuture =
                s3Client.putObject(
                    { it.bucket(s3Config.s3BucketName).key(s3ObjectKey) },
                    requestBody,
                )
            csvPrinter =
                CsvWriter.builder()
                    .bufferSize(CSV_WRITER_BUFFER_SIZE)
                    .fieldSeparator(CSV_FIELD_SEPARATOR)
                    .quoteCharacter(CSV_QUOTE_CHARACTER)
                    .lineDelimiter(CSV_LINE_DELIMITER)
                    .quoteStrategy(QuoteStrategies.REQUIRED)
                    .build(
                        GZIPOutputStream(requestBody.outputStream()).bufferedWriter(Charsets.UTF_8)
                    )
        }
        val formattedRecord =
            columns.map { columnName -> record.fields[columnName].toCsvValue().toString() }
        csvPrinter.writeRecord(formattedRecord)
    }

    override suspend fun flush() {
        try {
            log.info { "Flushing records to S3: s3://${s3Config.s3BucketName}/$s3ObjectKey" }
            csvPrinter.close()
            responseFuture.join()
            executeCopy(columns, s3ObjectKey)
            log.info { "COPY FROM s3://${s3Config.s3BucketName}/$s3ObjectKey complete" }
        } finally {
            // Cleanup S3 file if configured to purge
            if (s3Config.purgeStagingData) {
                try {
                    s3Client.deleteObject { it.bucket(s3Config.s3BucketName).key(s3ObjectKey) }
                } catch (e: Exception) {
                    log.warn(e) { "Failed to cleanup staging file: $s3ObjectKey" }
                }
            }
        }
    }

    private fun executeCopy(columns: List<String>, s3Key: String) {
        val columnList = columns.joinToString(", ") { "\"$it\"" }
        val s3Path = getFullS3Path(s3Key)

        // no explicit NULL AS param, since it defaults to '\\N` (which is what we want).
        // See RedshiftValueCoercer#map()
        val copyQuery =
            """
            COPY "${tableName.namespace}"."${tableName.name}" ($columnList)
            FROM '$s3Path'
            CREDENTIALS 'aws_access_key_id=${s3Config.accessKeyId};aws_secret_access_key=${s3Config.secretAccessKey}'
            CSV GZIP
            REGION '${s3Config.s3BucketRegion}'
            TIMEFORMAT 'auto'
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
}

@Singleton
class RedshiftAggregateFactory(
    private val dataSource: DataSource,
    private val s3Client: S3AsyncClient,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val config: RedshiftV2Configuration,
    private val clock: Clock,
    private val catalog: DestinationCatalog,
) : AggregateFactory {
    override fun create(key: StoreKey): Aggregate {
        val tableName = streamStateStore.get(key)!!.tableName
        val stream = catalog.getStream(key)
        return RedshiftStagingAggregate(
            tableName,
            dataSource,
            s3Client,
            config.s3Config,
            clock,
            stream.tableSchema.columnSchema,
        )
    }
}
