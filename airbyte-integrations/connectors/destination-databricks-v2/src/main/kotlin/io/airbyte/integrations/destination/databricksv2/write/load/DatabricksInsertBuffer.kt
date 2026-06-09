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

    /** Avro schema derived from the Databricks column types. */
    private val avroSchema: Schema = DatabricksAvroSchemaBuilder.buildAvroSchema(columnSchema)

    /** In-memory byte buffer backing the Avro output. */
    private var byteBuffer: ByteArrayOutputStream? = null
    private var avroWriter: DataFileWriter<GenericRecord>? = null
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

        val record = GenericData.Record(avroSchema)
        for (col in columns) {
            record.put(col, DatabricksAvroValueConverter.convert(recordFields[col]))
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

            val avroBytes = buffer.toByteArray()
            val stagingDir = stagingDirectory(tableName, config.database)
            val stagedFilePath = "$stagingDir/${UUID.randomUUID()}$STAGING_FILE_EXTENSION"

            logger.info {
                "Uploading $recordCount record(s) (${avroBytes.size} bytes) " +
                    "for ${tableName.namespace}.${tableName.name} to $stagedFilePath"
            }

            // Ensure staging volume and directory exist
            databricksClient.createStagingVolume(tableName, stagingDir)

            // Upload to Unity Catalog Volume
            databricksClient.uploadToVolume(
                stagedFilePath,
                ByteArrayInputStream(avroBytes),
            )

            // Execute COPY INTO
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
        byteBuffer = ByteArrayOutputStream()
        val datumWriter = GenericDatumWriter<GenericRecord>(avroSchema)
        avroWriter =
            DataFileWriter(datumWriter).apply {
                setCodec(CodecFactory.snappyCodec())
                create(avroSchema, byteBuffer!!)
            }
    }

    /** Resets all internal state for the next batch. */
    private fun resetState() {
        avroWriter = null
        byteBuffer = null
        recordCount = 0
    }

    companion object {
        private val executionDate = LocalDate.now(ZoneOffset.UTC)

        /**
         * Constructs the staging directory path within a Unity Catalog Volume. Format:
         * `/Volumes/<database>/<namespace>/<table>_staging/<date>`
         */
        fun stagingDirectory(tableName: TableName, database: String): String {
            return "$VOLUMES_BASE_PATH/$database/${tableName.namespace}/" +
                "${tableName.name}_staging/$executionDate"
        }
    }
}
