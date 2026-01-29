/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.write.storage_write_api

import com.google.cloud.bigquery.storage.v1.AppendRowsResponse
import com.google.cloud.bigquery.storage.v1.JsonStreamWriter
import com.google.cloud.bigquery.storage.v1.TableName
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.integrations.destination.bigquery.spec.StorageWriteApiConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import org.json.JSONArray
import org.json.JSONObject
import java.util.concurrent.TimeUnit

private val logger = KotlinLogging.logger {}

/**
 * DirectLoader implementation using BigQuery Storage Write API.
 *
 * Uses JsonStreamWriter with default stream to write records directly to BigQuery.
 * Data is written to __UNPARTITIONED__ buffer first, then BigQuery internally
 * repartitions without consuming partition modification quota.
 */
class BigqueryStorageWriteApiLoader(
    private val tableName: TableName,
    private val streamWriter: JsonStreamWriter,
    private val recordFormatter: BigqueryStorageWriteRecordFormatter,
    private val config: StorageWriteApiConfiguration,
) : DirectLoader {

    // Buffer for batching records before appending
    private val jsonBuffer = JSONArray()
    private var bufferSizeBytes: Long = 0
    private var recordCount: Long = 0

    override suspend fun accept(record: DestinationRecordRaw): DirectLoader.DirectLoadResult {
        try {
            // Format record to JSON
            val jsonObject: JSONObject = recordFormatter.formatRecordToJson(record)

            // Add to buffer
            jsonBuffer.put(jsonObject)
            bufferSizeBytes += estimateJsonSize(jsonObject)
            recordCount++

            // Flush if batch size or byte limit reached
            if (shouldFlush()) {
                flushBuffer()
            }

            return DirectLoader.Incomplete
        } catch (e: Exception) {
            logger.error(e) {
                "Error accepting record for table ${tableName.project}.${tableName.dataset}.${tableName.table}"
            }
            throw e
        }
    }

    override suspend fun finish() {
        try {
            // Flush any remaining buffered records
            if (jsonBuffer.length() > 0) {
                flushBuffer()
            }

            logger.info {
                "Finished loading $recordCount records into table ${tableName.project}.${tableName.dataset}.${tableName.table}"
            }
        } catch (e: Exception) {
            logger.error(e) {
                "Error finishing load for table ${tableName.project}.${tableName.dataset}.${tableName.table}"
            }
            throw e
        }
    }

    override fun close() {
        try {
            streamWriter.close()
            logger.info { "Closed stream writer for table ${tableName.project}.${tableName.dataset}.${tableName.table}" }
        } catch (e: Exception) {
            logger.error(e) { "Error closing stream writer" }
            // Don't throw on close to avoid masking other exceptions
        }
    }

    private fun shouldFlush(): Boolean {
        return jsonBuffer.length() >= config.batchSize ||
               bufferSizeBytes >= config.maxInflightBytes
    }

    private suspend fun flushBuffer() {
        if (jsonBuffer.length() == 0) {
            return
        }

        try {
            logger.debug {
                "Flushing ${jsonBuffer.length()} records (${bufferSizeBytes} bytes) to table ${tableName.project}.${tableName.dataset}.${tableName.table}"
            }

            // Append to BigQuery using Storage Write API
            val appendFuture = streamWriter.append(jsonBuffer)

            // Wait for acknowledgment (with timeout)
            val response: AppendRowsResponse = appendFuture.get(60, TimeUnit.SECONDS)

            // Check for errors
            if (response.hasError()) {
                val error = response.error
                throw RuntimeException(
                    "Append failed for table ${tableName.project}.${tableName.dataset}.${tableName.table}: " +
                    "${error.code} - ${error.message}"
                )
            }

            logger.debug {
                "Successfully appended ${jsonBuffer.length()} records. Offset: ${response.appendResult.offset.value}"
            }

            // Clear buffer
            resetBuffer()
        } catch (e: Exception) {
            logger.error(e) {
                "Error flushing buffer to table ${tableName.project}.${tableName.dataset}.${tableName.table}"
            }
            throw e
        }
    }

    private fun resetBuffer() {
        // Create new JSONArray to clear buffer
        while (jsonBuffer.length() > 0) {
            jsonBuffer.remove(0)
        }
        bufferSizeBytes = 0
    }

    private fun estimateJsonSize(jsonObject: JSONObject): Long {
        // Rough estimate: JSON string length in bytes
        return jsonObject.toString().toByteArray(Charsets.UTF_8).size.toLong()
    }
}
