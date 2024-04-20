/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb

import com.fasterxml.jackson.core.JsonGenerator
import com.fasterxml.jackson.databind.DeserializationFeature
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule
import com.github.javafaker.Faker
import io.github.oshai.kotlinlogging.KotlinLogging
import java.lang.System.currentTimeMillis
import kotlinx.cli.ArgParser
import kotlinx.cli.ArgType
import kotlinx.cli.default
import kotlinx.cli.required
import org.bson.BsonTimestamp
import org.bson.Document

object MongoDbInsertClient {

    private const val BATCH_SIZE = 1000

    private val logger = KotlinLogging.logger {}

    @JvmStatic
    fun main(args: Array<String>) {
        val parser = ArgParser("MongoDb Insert Client")
        val connectionString by
            parser
                .option(
                    ArgType.String,
                    fullName = "connection-string",
                    shortName = "cs",
                    description = "MongoDb Connection String"
                )
                .required()
        val databaseName by
            parser
                .option(
                    ArgType.String,
                    fullName = "database-name",
                    shortName = "d",
                    description = "Database Name"
                )
                .required()
        val collectionName by
            parser
                .option(
                    ArgType.String,
                    fullName = "collection-name",
                    shortName = "cn",
                    description = "Collection Name"
                )
                .required()
        val username by
            parser
                .option(
                    ArgType.String,
                    fullName = "username",
                    shortName = "u",
                    description = "Username"
                )
                .required()
        val numberOfDocuments by
            parser
                .option(
                    ArgType.Int,
                    fullName = "number",
                    shortName = "n",
                    description = "Number of documents to generate"
                )
                .default(10000)

        parser.parse(args)

        println("Enter password: ")
        val password = readln()

        val config =
            mapOf(
                MongoConstants.DATABASE_CONFIG_CONFIGURATION_KEY to
                    mapOf(
                        MongoConstants.DATABASE_CONFIGURATION_KEY to databaseName,
                        MongoConstants.CONNECTION_STRING_CONFIGURATION_KEY to connectionString,
                        MongoConstants.AUTH_SOURCE_CONFIGURATION_KEY to "admin",
                        MongoConstants.USERNAME_CONFIGURATION_KEY to username,
                        MongoConstants.PASSWORD_CONFIGURATION_KEY to password
                    )
            )

        val faker = Faker()

        val objectMapper = ObjectMapper().registerModule(JavaTimeModule())
        objectMapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false)
        objectMapper.configure(JsonGenerator.Feature.WRITE_BIGDECIMAL_AS_PLAIN, true)
        val roundTrippedConfig = objectMapper.readTree(objectMapper.writeValueAsBytes(config))

        MongoConnectionUtils.createMongoClient(MongoDbSourceConfig(roundTrippedConfig)).use {
            mongoClient ->
            val documents = mutableListOf<Document>()
            val batches = if (numberOfDocuments > BATCH_SIZE) numberOfDocuments / BATCH_SIZE else 1
            val batchSize = if (numberOfDocuments > BATCH_SIZE) BATCH_SIZE else numberOfDocuments
            logger.info { "Inserting $batches batch(es) of $batchSize document(s) each..." }
            for (i in 0..batches) {
                logger.info { "Inserting batch ${i}..." }
                for (j in 0..batchSize) {
                    val index = (j + 1) + ((i + 1) * batchSize)
                    documents +=
                        Document()
                            .append("name", "Document $index")
                            .append("title", "${faker.lorem().sentence(10)}")
                            .append("description", "${faker.lorem().paragraph(25)}")
                            .append("data", "${faker.lorem().paragraphs(100)}")
                            .append("paragraph", "${faker.lorem().paragraph(25)}")
                            .append("doubleField", index.toDouble())
                            .append("intField", index)
                            .append("objectField", mapOf("key" to "value"))
                            .append("timestamp", BsonTimestamp(currentTimeMillis()))
                }
                mongoClient
                    .getDatabase(databaseName)
                    .getCollection(collectionName)
                    .insertMany(documents)
                documents.clear()
            }
        }

        logger.info { "Inserted $numberOfDocuments document(s) to $databaseName.$collectionName" }
    }
}
