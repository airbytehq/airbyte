/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2.write.load

import com.google.common.annotations.VisibleForTesting
import com.mongodb.kotlin.client.coroutine.MongoClient
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.table.TableName
import io.airbyte.cdk.load.util.serializeToString
import io.github.oshai.kotlinlogging.KotlinLogging
import org.bson.BsonDateTime
import org.bson.BsonDocument
import org.bson.BsonInt32
import org.bson.BsonInt64
import org.bson.BsonNull
import org.bson.BsonString
import org.bson.BsonBoolean
import org.bson.BsonDouble
import org.bson.Document
import java.time.format.DateTimeFormatter

private val log = KotlinLogging.logger {}

@SuppressFBWarnings(
    value = ["NP_NONNULL_PARAM_VIOLATION"],
    justification = "suspend and fb's non-null analysis don't play well"
)
class MongodbInsertBuffer(
    val tableName: TableName,
    private val mongoClient: MongoClient,
    private val databaseName: String,
) {
    @VisibleForTesting
    internal val buffer = mutableListOf<Document>()

    fun accumulate(recordFields: Map<String, AirbyteValue>) {
        val doc = Document()
        recordFields.forEach { (key, value) ->
            doc[key] = toMongoValue(value)
        }
        buffer.add(doc)
    }

    suspend fun flush() {
        if (buffer.isEmpty()) {
            log.info { "Buffer is empty, skipping flush for ${tableName.name}" }
            return
        }

        val recordCount = buffer.size
        val startTime = System.currentTimeMillis()

        try {
            log.info { "Beginning insert of $recordCount documents into ${tableName.name}" }
            println("DEBUG InsertBuffer.flush: databaseName='$databaseName', tableName.name='${tableName.name}', tableName.namespace='${tableName.namespace}'")

            val database = mongoClient.getDatabase(databaseName)
            val collection = database.getCollection<Document>(tableName.name)

            collection.insertMany(buffer)

            val duration = System.currentTimeMillis() - startTime
            val recordsPerSec = if (duration > 0) (recordCount * 1000 / duration) else recordCount
            log.info { "Finished insert of $recordCount documents into ${tableName.name} in ${duration}ms ($recordsPerSec records/sec)" }
        } catch (e: Exception) {
            log.error(e) { "Failed to insert $recordCount documents into ${tableName.name}" }
            throw e
        } finally {
            buffer.clear()
        }
    }

    private fun toMongoValue(abValue: AirbyteValue): Any? {
        return when (abValue) {
            is NullValue -> null
            is BooleanValue -> abValue.value
            is IntegerValue -> abValue.value.toLong()
            is NumberValue -> abValue.value.toDouble()
            is StringValue -> abValue.value
            is DateValue -> {
                // Store as ISO date string
                abValue.value.format(DateTimeFormatter.ISO_LOCAL_DATE)
            }
            is TimestampWithTimezoneValue -> {
                // Convert to MongoDB Date (milliseconds since epoch)
                abValue.value.toInstant().toEpochMilli()
            }
            is TimestampWithoutTimezoneValue -> {
                // Store as ISO string since we don't have timezone info
                abValue.value.format(DateTimeFormatter.ISO_LOCAL_DATE_TIME)
            }
            is TimeWithTimezoneValue -> {
                // Store as ISO string
                abValue.value.format(DateTimeFormatter.ISO_TIME)
            }
            is TimeWithoutTimezoneValue -> {
                // Store as ISO string
                abValue.value.format(DateTimeFormatter.ISO_LOCAL_TIME)
            }
            is ObjectValue -> {
                // Convert nested object to Document
                Document.parse(abValue.values.serializeToString())
            }
            is ArrayValue -> {
                // Convert array to List
                abValue.values.map { toMongoValue(it) }
            }
        }
    }
}
