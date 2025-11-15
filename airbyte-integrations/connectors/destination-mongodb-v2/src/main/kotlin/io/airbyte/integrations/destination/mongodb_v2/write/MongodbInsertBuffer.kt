/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2.write

import com.mongodb.client.MongoClient
import com.mongodb.client.model.InsertManyOptions
import io.airbyte.cdk.load.data.*
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.mongodb_v2.spec.MongodbConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.Date
import kotlinx.coroutines.runBlocking
import org.bson.Document

private val logger = KotlinLogging.logger {}

class MongodbInsertBuffer(
    private val tableName: TableName,
    private val mongoClient: MongoClient,
    private val config: MongodbConfiguration,
    private val flushLimit: Int = config.batchSize,
) {
    private val buffer = mutableListOf<Document>()
    private var recordCount = 0

    fun accumulate(recordFields: Map<String, AirbyteValue>) {
        val document = convertToDocument(recordFields)
        buffer.add(document)
        recordCount++

        if (recordCount >= flushLimit) {
            runBlocking { flush() }
        }
    }

    suspend fun flush() {
        if (buffer.isEmpty()) {
            logger.warn { "Buffer is empty, nothing to flush" }
            return
        }

        try {
            val collection = mongoClient.getDatabase(config.database).getCollection(tableName.name)

            logger.info { "Flushing ${buffer.size} documents to collection ${tableName.name}..." }

            // Use insertMany for efficient batch insert
            // ordered=false allows MongoDB to continue inserting even if some documents fail
            collection.insertMany(buffer, InsertManyOptions().ordered(false))

            logger.info { "Successfully flushed $recordCount documents to ${tableName.name}" }
        } catch (e: Exception) {
            logger.error(e) { "Failed to flush documents to collection ${tableName.name}" }
            throw e
        } finally {
            buffer.clear()
            recordCount = 0
        }
    }

    /**
     * Converts Airbyte value types to MongoDB BSON document. MongoDB natively supports rich types
     * like Date, embedded documents, arrays, etc.
     */
    private fun convertToDocument(fields: Map<String, AirbyteValue>): Document {
        val document = Document()

        fields.forEach { (fieldName, value) -> document[fieldName] = convertAirbyteValue(value) }

        return document
    }

    private fun convertAirbyteValue(value: AirbyteValue): Any? {
        return when (value) {
            is NullValue -> null
            is StringValue -> value.value
            is IntegerValue -> value.value.toLong() // Convert BigInteger to Long
            is NumberValue -> value.value.toDouble()
            is BooleanValue -> value.value
            is TimestampWithTimezoneValue -> Date.from(value.value.toInstant())
            is TimestampWithoutTimezoneValue -> {
                // Convert LocalDateTime to Date (assumes system default timezone)
                Date.from(value.value.atZone(java.time.ZoneId.systemDefault()).toInstant())
            }
            is DateValue -> {
                // Convert LocalDate to Date
                Date.from(value.value.atStartOfDay(java.time.ZoneId.systemDefault()).toInstant())
            }
            is TimeWithTimezoneValue -> value.value.toString() // Keep as string
            is TimeWithoutTimezoneValue -> value.value.toString() // Keep as string
            is ArrayValue -> {
                // MongoDB supports native arrays
                value.values.map { convertAirbyteValue(it) }
            }
            is ObjectValue -> {
                // MongoDB supports nested documents
                val doc = Document()
                value.values.forEach { (k, v) -> doc[k] = convertAirbyteValue(v) }
                doc
            }
        }
    }
}
