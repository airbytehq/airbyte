package io.airbyte.integrations.source.mongodb.internal

import io.airbyte.commons.json.Jsons
import kotlinx.cli.ArgParser
import kotlinx.cli.ArgType
import kotlinx.cli.default
import kotlinx.cli.required
import org.bson.BsonTimestamp
import org.bson.Document
import java.lang.System.currentTimeMillis

object MongoDbInsertClient {

    @JvmStatic
    fun main(args: Array<String>) {
        val parser = ArgParser("MongoDb Insert Client")
        val connectionString by parser.option(ArgType.String, fullName = "connection-string", shortName = "cs", description = "MongoDb Connection String").required()
        val databaseName by parser.option(ArgType.String, fullName = "database-name", shortName = "d", description = "Database Name").required()
        val collectionName by parser.option(ArgType.String, fullName = "collection-name", shortName = "cn", description = "Collection Name").required()
        val replicaSet by parser.option(ArgType.String, fullName = "replica-set", shortName = "r", description = "Replica Set").required()
        val username by parser.option(ArgType.String, fullName = "username", shortName = "u", description = "Username").required()
        val numberOfDocuments by parser.option(ArgType.Int, fullName = "number", shortName = "n", description = "Number of documents to generate").default(10000)

        parser.parse(args)

        println("Enter password: ")
        val password = readln()

        var config = mapOf(MongoConstants.DATABASE_CONFIGURATION_KEY to databaseName,
                MongoConstants.CONNECTION_STRING_CONFIGURATION_KEY to connectionString,
                MongoConstants.AUTH_SOURCE_CONFIGURATION_KEY to "admin",
                MongoConstants.REPLICA_SET_CONFIGURATION_KEY to replicaSet,
                MongoConstants.USER_CONFIGURATION_KEY to username,
                MongoConstants.PASSWORD_CONFIGURATION_KEY to password)

        MongoConnectionUtils.createMongoClient(Jsons.deserialize(Jsons.serialize(config))).use { mongoClient ->
            val documents = mutableListOf<Document>()
            for (i in 0..numberOfDocuments) {
                documents += Document().append("name", "Document $i")
                        .append("description", "This is document #$i")
                        .append("doubleField", i.toDouble())
                        .append("intField", i)
                        .append("objectField", mapOf("key" to "value"))
                        .append("timestamp", BsonTimestamp(currentTimeMillis()))
            }

            mongoClient.getDatabase(databaseName).getCollection(collectionName).insertMany(documents)
        }

        println("Inserted $numberOfDocuments document(s) to $databaseName.$collectionName")
    }
}