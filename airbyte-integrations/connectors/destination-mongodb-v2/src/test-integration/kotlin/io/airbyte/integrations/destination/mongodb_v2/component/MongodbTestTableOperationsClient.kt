/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2.component

import com.mongodb.kotlin.client.coroutine.MongoClient
import io.airbyte.cdk.load.component.TestTableOperationsClient
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.mongodb_v2.config.MongodbConfiguration
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import kotlinx.coroutines.flow.toList
import org.bson.Document

@Requires(env = ["component"])
@Singleton
class MongodbTestTableOperationsClient(
    private val mongoClient: MongoClient,
    private val config: MongodbConfiguration,
) : TestTableOperationsClient {

    override suspend fun ping() {
        // Simple ping - list databases
        mongoClient.listDatabaseNames().toList()
    }

    override suspend fun dropNamespace(namespace: String) {
        val database = mongoClient.getDatabase(namespace)
        database.drop()
    }

    override suspend fun insertRecords(
        table: TableName,
        records: List<Map<String, AirbyteValue>>
    ) {
        if (records.isEmpty()) return

        val database = mongoClient.getDatabase(table.namespace ?: config.resolvedDatabase)
        val collection = database.getCollection<Document>(table.name)

        val documents = records.map { record ->
            val doc = Document()
            record.forEach { (key, value) ->
                doc[key] = toMongoValue(value)
            }
            doc
        }

        collection.insertMany(documents)
    }

    override suspend fun readTable(table: TableName): List<Map<String, Any>> {
        val database = mongoClient.getDatabase(table.namespace ?: config.resolvedDatabase)
        val collection = database.getCollection<Document>(table.name)

        return collection.find().toList().map { doc ->
            doc.filterKeys { it != "_id" }  // Filter out MongoDB's auto-generated _id
                .mapValues { (_, value) -> value ?: "null" }
        }
    }

    private fun toMongoValue(abValue: AirbyteValue): Any? {
        return when (abValue) {
            is NullValue -> null
            is StringValue -> abValue.value
            is IntegerValue -> abValue.value.toLong()
            else -> abValue.toString()
        }
    }
}
