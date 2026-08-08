/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb

import com.mongodb.client.MongoClient
import com.mongodb.client.MongoCollection
import com.mongodb.client.MongoCursor
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.data.BooleanCodec
import io.airbyte.cdk.data.DoubleCodec
import io.airbyte.cdk.data.JsonStringCodec
import io.airbyte.cdk.data.NullCodec
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamRecordConsumer
import io.github.oshai.kotlinlogging.KotlinLogging
import org.bson.Document
import org.bson.types.ObjectId
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference

private val log = KotlinLogging.logger {}

/**
 * Reads documents from a MongoDB collection and emits them as Airbyte records.
 *
 * For full refresh with a primary key (`_id`), reads are resumable:
 * documents are sorted by `_id` and the last `_id` value is checkpointed.
 * If interrupted, the next read resumes from that checkpoint.
 *
 * For full refresh without a primary key (shouldn't happen for MongoDB since
 * `_id` always exists), reads are non-resumable.
 */
class MongoDbPartitionReader(
    private val mongoClient: MongoClient,
    private val config: MongoDbSourceConfiguration,
    private val stream: Stream,
    private val streamRecordConsumer: StreamRecordConsumer,
    private val lowerBound: String?,
    private val isComplete: Boolean,
) : PartitionReader {

    private val numRecords = AtomicLong(0L)
    private val lastIdValue = AtomicReference<String?>(null)
    private val runComplete = AtomicBoolean(false)

    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus {
        return PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN
    }

    override suspend fun run() {
        if (isComplete) {
            runComplete.set(true)
            return
        }

        val database = mongoClient.getDatabase(config.database)
        val collectionName = stream.name
        val collection: MongoCollection<Document> = database.getCollection(collectionName)

        log.info {
            "Starting full refresh read for collection: $collectionName" +
                if (lowerBound != null) " (resuming from _id > $lowerBound)" else ""
        }

        // Build the query filter
        val filter = if (lowerBound != null) {
            // Resume from the last _id checkpoint.
            // Try to parse as ObjectId first; if that fails, use the raw string.
            val lowerBoundValue: Any = try {
                ObjectId(lowerBound)
            } catch (_: IllegalArgumentException) {
                lowerBound
            }
            Document("_id", Document("\$gt", lowerBoundValue))
        } else {
            Document()
        }

        // Sort by _id for deterministic ordering and resumability
        val sort = Document("_id", 1)

        val cursor: MongoCursor<Document> = collection.find(filter)
            .sort(sort)
            .batchSize(1000)
            .cursor()

        try {
            cursor.use {
                while (it.hasNext()) {
                    val doc = it.next()
                    val record = documentToRecord(doc, stream.fields)
                    streamRecordConsumer.accept(record, null)

                    // Track the last _id for checkpointing
                    val rawId = doc.get("_id")
                    val idValue = when (rawId) {
                        is ObjectId -> rawId.toHexString()
                        else -> rawId?.toString()
                    }
                    if (idValue != null) {
                        lastIdValue.set(idValue)
                    }

                    numRecords.incrementAndGet()
                }
            }
            runComplete.set(true)
        } catch (e: Exception) {
            log.warn { "Error reading collection $collectionName: ${e.message}" }
            // Even on error, we may have read some records - checkpoint what we have
            if (numRecords.get() == 0L) {
                throw e
            }
        }
    }

    override fun checkpoint(): PartitionReadCheckpoint {
        val stateValue: OpaqueStateValue = if (runComplete.get()) {
            MongoDbStreamState.snapshotCompleted
        } else {
            val lastId = lastIdValue.get()
            if (lastId != null) {
                MongoDbStreamState.snapshotCheckpoint(lastId)
            } else {
                // No records read yet - return empty state to signal cold start
                MongoDbStreamState.snapshotCompleted
            }
        }

        return PartitionReadCheckpoint(
            opaqueStateValue = stateValue,
            numRecords = numRecords.get(),
        )
    }

    override fun releaseResources() {
        // MongoClient lifecycle is managed by the PartitionsCreator
    }

    /**
     * Converts a MongoDB [Document] to a [NativeRecordPayload].
     *
     * For each field defined in the stream schema, extracts the value from the document
     * and wraps it with the appropriate encoder based on the field's [MongoDbFieldType].
     */
    private fun documentToRecord(
        doc: Document,
        fields: List<Field>,
    ): NativeRecordPayload {
        val record: NativeRecordPayload = mutableMapOf()
        for (field in fields) {
            val value = doc.get(field.id)
            record[field.id] = encodeFieldValue(field, value)
        }
        return record
    }

    /**
     * Encodes a BSON value to a [FieldValueEncoder] based on the field type.
     *
     * MongoDB stores all values as BSON. We need to convert them to JVM types
     * that match the [MongoDbFieldType]'s encoder expectations:
     * - BOOLEAN -> Boolean via BooleanCodec
     * - NUMBER -> Double via DoubleCodec
     * - STRING, ARRAY, OBJECT -> String via TextCodec or JsonStringCodec
     * - NULL -> null via NullCodec
     */
    private fun encodeFieldValue(
        field: Field,
        value: Any?,
    ): FieldValueEncoder<*> {
        if (value == null) {
            return FieldValueEncoder(null, NullCodec)
        }

        return when (field.type) {
            MongoDbFieldType.BOOLEAN -> {
                val boolValue = when (value) {
                    is Boolean -> value
                    else -> value.toString().toBoolean()
                }
                FieldValueEncoder(boolValue, BooleanCodec)
            }
            MongoDbFieldType.NUMBER -> {
                val doubleValue = when (value) {
                    is Number -> value.toDouble()
                    is org.bson.types.Decimal128 -> value.bigDecimalValue().toDouble()
                    else -> value.toString().toDoubleOrNull() ?: 0.0
                }
                FieldValueEncoder(doubleValue, DoubleCodec)
            }
            MongoDbFieldType.ARRAY -> {
                // Serialize array to JSON string
                val jsonString = when (value) {
                    is List<*> -> Document("a", value).toJson().let { json ->
                        // Extract the array portion from the wrapping document
                        json.substringAfter("\"a\": ").trimEnd('}').trim()
                    }
                    else -> value.toString()
                }
                FieldValueEncoder(jsonString, JsonStringCodec)
            }
            MongoDbFieldType.OBJECT -> {
                // Serialize object to JSON string
                val jsonString = when (value) {
                    is Document -> value.toJson()
                    is org.bson.BsonDocument -> value.toJson()
                    else -> value.toString()
                }
                FieldValueEncoder(jsonString, JsonStringCodec)
            }
            MongoDbFieldType.NULL -> {
                FieldValueEncoder(null, NullCodec)
            }
            MongoDbFieldType.STRING -> {
                val stringValue = bsonValueToString(value)
                FieldValueEncoder(stringValue, TextCodec)
            }
            else -> {
                // Fallback: stringify
                FieldValueEncoder(value.toString(), TextCodec)
            }
        }
    }

    /**
     * Converts a BSON value to its string representation.
     * Handles ObjectId, dates, timestamps, and other BSON types.
     */
    private fun bsonValueToString(value: Any): String {
        return when (value) {
            is ObjectId -> value.toHexString()
            is org.bson.types.Decimal128 -> value.bigDecimalValue().toPlainString()
            is java.util.Date -> value.toInstant().toString()
            is org.bson.BsonTimestamp -> java.time.Instant.ofEpochSecond(
                value.time.toLong()
            ).toString()
            is org.bson.types.Binary -> java.util.Base64.getEncoder()
                .encodeToString(value.data)
            else -> value.toString()
        }
    }
}
