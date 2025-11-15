/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2

import com.mongodb.kotlin.client.coroutine.MongoClient
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.*
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.integrations.destination.mongodb_v2.config.toMongodbCompatible
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.runBlocking
import org.bson.Document
import java.time.Instant
import java.util.UUID

class MongodbDataDumper(
    private val mongoClient: MongoClient,
    private val databaseName: String,
) : DestinationDataDumper {

    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> = runBlocking {
        // Apply MongoDB name sanitization (same as FinalTableNameGenerator)
        val namespace = stream.mappedDescriptor.namespace?.toMongodbCompatible() ?: databaseName
        val tableName = stream.mappedDescriptor.name.toMongodbCompatible()

        val database = mongoClient.getDatabase(namespace)
        val collection = database.getCollection<Document>(tableName)

        val docCount = collection.countDocuments()
        println("DEBUG: Dumping records from $namespace.$tableName - found $docCount documents")

        val records = mutableListOf<OutputRecord>()

        collection.find().toList().forEach { doc ->
            val data = mutableMapOf<String, AirbyteValue>()

            doc.forEach { (key, value) ->
                if (key != "_id") {  // Skip MongoDB's internal _id
                    data[key] = toAirbyteValue(value)
                }
            }

            // Extract Airbyte metadata
            val rawId = (data["_airbyte_raw_id"] as? StringValue)?.let {
                try { UUID.fromString(it.value) } catch (e: Exception) { null }
            }

            val extractedAt = when (val value = data["_airbyte_extracted_at"]) {
                is IntegerValue -> Instant.ofEpochMilli(value.value.toLong())
                else -> Instant.EPOCH
            }

            val generationId = when (val value = data["_airbyte_generation_id"]) {
                is IntegerValue -> value.value.toLong()
                is NullValue -> null
                else -> null
            }

            println("DEBUG: Found record with generationId=$generationId, data=${data.filterKeys { !it.startsWith("_airbyte") }}")

            val meta = data["_airbyte_meta"] as? ObjectValue

            // Filter out Airbyte metadata columns for data field
            val userData = data.filterKeys { !it.startsWith("_airbyte") }

            records.add(
                OutputRecord(
                    rawId = rawId,
                    extractedAt = extractedAt,
                    loadedAt = null,  // MongoDB doesn't track loaded_at separately
                    generationId = generationId,
                    data = ObjectValue(linkedMapOf<String, AirbyteValue>().apply { putAll(userData) }),
                    airbyteMeta = parseAirbyteMeta(meta)
                )
            )
        }

        return@runBlocking records
    }

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): Map<String, String> {
        // MongoDB is not a file-based destination
        return emptyMap()
    }

    private fun toAirbyteValue(value: Any?): AirbyteValue {
        return when (value) {
            null -> NullValue
            is String -> StringValue(value)
            is Int -> IntegerValue(value.toLong())
            is Long -> IntegerValue(value)
            is Double -> NumberValue(value.toBigDecimal())
            is Boolean -> BooleanValue(value)
            is Document -> {
                val map = value.mapValues { toAirbyteValue(it.value) }
                ObjectValue(linkedMapOf<String, AirbyteValue>().apply { putAll(map) })
            }
            is List<*> -> {
                val items = value.map { toAirbyteValue(it) }
                ArrayValue(items)
            }
            else -> StringValue(value.toString())
        }
    }

    private fun parseAirbyteMeta(meta: ObjectValue?): OutputRecord.Meta {
        if (meta == null) {
            return OutputRecord.Meta(syncId = null)
        }

        val syncId = (meta.values["sync_id"] as? IntegerValue)?.value?.toLong()

        val changes = (meta.values["changes"] as? ArrayValue)?.values?.mapNotNull { changeValue ->
            if (changeValue is ObjectValue) {
                val field = (changeValue.values["field"] as? StringValue)?.value
                val change = (changeValue.values["change"] as? StringValue)?.value
                val reason = (changeValue.values["reason"] as? StringValue)?.value

                if (field != null && change != null && reason != null) {
                    try {
                        Meta.Change(
                            field = field,
                            change = Change.valueOf(change),
                            reason = Reason.valueOf(reason)
                        )
                    } catch (e: Exception) {
                        null  // Invalid change value
                    }
                } else {
                    null
                }
            } else {
                null
            }
        } ?: emptyList()

        return OutputRecord.Meta(
            changes = changes,
            syncId = syncId
        )
    }
}
