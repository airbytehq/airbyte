/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricksv2.write.load

import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.integrations.destination.databricksv2.client.DatabricksAirbyteClient
import io.airbyte.integrations.destination.databricksv2.spec.DatabricksV2Configuration
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.time.LocalDate
import java.time.ZoneOffset
import java.util.*
import org.apache.avro.Schema
import org.apache.avro.file.CodecFactory
import org.apache.avro.file.DataFileWriter
import org.apache.avro.generic.GenericData
import org.apache.avro.generic.GenericDatumWriter
import org.apache.avro.generic.GenericRecord

private val logger = KotlinLogging.logger {}

private const val STAGING_FILE_EXTENSION = ".avro"
private const val VOLUMES_BASE_PATH = "/Volumes"

/** Initial buffer size (4 MB) to reduce array-doubling GC churn for large batches. */
private const val INITIAL_BUFFER_SIZE = 4 * 1024 * 1024

/**
 * Buffers records into an in-memory Avro file and flushes them to Databricks via Unity Catalog
 * Volume staging.
 *
 * The loading pipeline works as follows:
 * 1. Records are accumulated into an in-memory Avro buffer with Snappy compression
 * 2. On [flush], the buffer is uploaded to a Unity Catalog Volume as an `.avro` file
 * 3. A Databricks `COPY INTO` command loads the data from the Volume into the target table
 * 4. The staging file is optionally deleted (based on [DatabricksV2Configuration.purgeStagingData])
 */
class DatabricksInsertBuffer(
    private val tableName: TableName,
    val columns: List<String>,
    private val columnSchema: Map<String, ColumnType>,
    private val databricksClient: DatabricksAirbyteClient,
    private val config: DatabricksV2Configuration,
) {

    /** In-memory byte buffer backing the Avro output. */
    private var byteBuffer: NoAllocByteArrayOutputStream? = null
    private var avroWriter: DataFileWriter<GenericRecord>? = null

    private var reusableRecord: GenericData.Record? = null
    private val avroSchema: Schema = DatabricksAvroSchemaBuilder.buildAvroSchema(columnSchema)
    internal var recordCount = 0

    /**
     * Adds a record to the current Avro batch.
     *
     * On the first call, initializes the Avro writer with Snappy compression. Subsequent calls
     * convert the record fields to Avro values and append a [GenericRecord].
     */
    fun accumulate(recordFields: Map<String, AirbyteValue>) {
        if (byteBuffer == null) {
            initializeBuffer()
        }

        val record = reusableRecord!!
        for (i in columns.indices) {
            record.put(i, DatabricksAvroValueConverter.convert(recordFields[columns[i]]))
        }
        avroWriter!!.append(record)
        recordCount++
    }

    /** Flushes the buffered Avro data to Databricks via Unity Catalog Volume staging. */
    suspend fun flush() {
        val buffer = byteBuffer
        if (buffer == null) {
            logger.warn { "No data to flush for ${tableName.namespace}.${tableName.name}" }
            return
        }

        try {
            // Finalize the Avro file
            avroWriter?.close()

            val stagingDir = stagingDirectory(tableName, config.database)
            val stagedFilePath = "$stagingDir/${UUID.randomUUID()}$STAGING_FILE_EXTENSION"

            logger.info {
                "Uploading $recordCount record(s) (${buffer.size()} bytes) " +
                    "for ${tableName.namespace}.${tableName.name} to $stagedFilePath"
            }

            databricksClient.createStagingVolume(tableName, stagingDir)
            databricksClient.uploadToVolume(stagedFilePath, buffer.toInputStream())
            databricksClient.copyFromVolume(tableName, stagedFilePath)

            logger.info {
                "Loaded $recordCount row(s) into ${tableName.namespace}.${tableName.name}"
            }

            // Cleanup staging file
            if (config.purgeStagingData) {
                databricksClient.deleteStagedFile(stagedFilePath)
                logger.debug { "Purged staging file: $stagedFilePath" }
            }
        } catch (e: Exception) {
            logger.error(e) {
                "Failed to flush $recordCount record(s) for " +
                    "${tableName.namespace}.${tableName.name}"
            }
            throw e
        } finally {
            resetState()
        }
    }

    /** Initializes the in-memory Avro writer with Snappy compression. */
    private fun initializeBuffer() {
        byteBuffer = NoAllocByteArrayOutputStream(INITIAL_BUFFER_SIZE)
        val datumWriter = GenericDatumWriter<GenericRecord>(avroSchema)
        avroWriter =
            DataFileWriter(datumWriter).apply {
                setCodec(CodecFactory.snappyCodec())
                create(avroSchema, byteBuffer!!)
            }
        reusableRecord = GenericData.Record(avroSchema)
    }

    /** Resets all internal state for the next batch. */
    private fun resetState() {
        avroWriter = null
        byteBuffer = null
        reusableRecord = null
        recordCount = 0
    }

    companion object {
        private val executionDate = LocalDate.now(ZoneOffset.UTC)

        /** Format: `/Volumes/<database>/<namespace>/<table>_staging/<date>` */
        fun stagingDirectory(tableName: TableName, database: String): String {
            return "$VOLUMES_BASE_PATH/$database/${tableName.namespace}/" +
                "${tableName.name}_staging/$executionDate"
        }
    }
}

/** Returns an [java.io.InputStream] that reads directly from the internal buffer. No copy. */
private class NoAllocByteArrayOutputStream(size: Int) : ByteArrayOutputStream(size) {
    fun toInputStream(): ByteArrayInputStream = ByteArrayInputStream(buf, 0, count)
}
