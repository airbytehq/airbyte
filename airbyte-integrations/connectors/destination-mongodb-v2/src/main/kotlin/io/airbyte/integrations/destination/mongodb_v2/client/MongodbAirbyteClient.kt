/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2.client

import com.mongodb.client.MongoClient
import com.mongodb.client.MongoDatabase
import com.mongodb.client.model.Filters
import com.mongodb.client.model.ReplaceOptions
import com.mongodb.client.model.Sorts
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnChangeset
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TableSchema
import io.airbyte.cdk.load.component.TableSchemaEvolutionClient
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAMES
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.mongodb_v2.spec.MongodbConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import org.bson.Document

private val log = KotlinLogging.logger {}

@Singleton
class MongodbAirbyteClient(
    private val mongoClient: MongoClient,
    private val config: MongodbConfiguration,
) : TableOperationsClient, TableSchemaEvolutionClient {

    private val database: MongoDatabase
        get() = mongoClient.getDatabase(config.database)

    override suspend fun createNamespace(namespace: String) {
        // In MongoDB, databases/namespaces are created implicitly when first collection is created
        // We just validate the namespace name
        require(namespace.isNotBlank()) {
            "Namespace (database) name cannot be blank"
        }
        log.info { "Namespace '$namespace' will be created implicitly on first collection creation" }
    }

    override suspend fun namespaceExists(namespace: String): Boolean {
        return mongoClient.listDatabaseNames().contains(namespace)
    }

    override suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean
    ) {
        val collectionName = tableName.name

        if (replace) {
            database.getCollection(collectionName).drop()
            log.info { "Dropped existing collection: $collectionName" }
        }

        // Create collection if it doesn't exist
        if (!database.listCollectionNames().contains(collectionName)) {
            database.createCollection(collectionName)
            log.info { "Created collection: $collectionName" }
        }

        // Create indexes for better performance
        val collection = database.getCollection(collectionName)

        // Index on _airbyte_extracted_at for time-based queries
        collection.createIndex(Document(COLUMN_NAME_AB_EXTRACTED_AT, 1))
        log.info { "Created index on $COLUMN_NAME_AB_EXTRACTED_AT" }

        // If dedupe mode, create compound index on PK + cursor
        if (stream.importType is Dedupe) {
            val dedupe = stream.importType as Dedupe
            // primaryKey is List<List<String>>, flatten to get the field names
            val pkFields = dedupe.primaryKey.map { it.first() }.map { columnNameMapping[it]!! }

            val indexDoc = Document()
            pkFields.forEach { field -> indexDoc[field] = 1 }
            indexDoc[COLUMN_NAME_AB_EXTRACTED_AT] = -1 // Descending for latest first

            collection.createIndex(indexDoc)
            log.info { "Created dedupe index on ${pkFields.joinToString(", ")} + $COLUMN_NAME_AB_EXTRACTED_AT" }
        }
    }

    override suspend fun tableExists(tableName: TableName): Boolean {
        return database.listCollectionNames().contains(tableName.name)
    }

    override suspend fun dropTable(tableName: TableName) {
        database.getCollection(tableName.name).drop()
        log.info { "Dropped collection: ${tableName.name}" }
    }

    override suspend fun countTable(tableName: TableName): Long? {
        return try {
            database.getCollection(tableName.name).countDocuments()
        } catch (e: Exception) {
            log.debug(e) { "Collection ${tableName.name} does not exist. Returning null." }
            null
        }
    }

    override suspend fun getGenerationId(tableName: TableName): Long {
        val collection = database.getCollection(tableName.name)
        val doc = collection.find().limit(1).first()

        return doc?.getLong(COLUMN_NAME_AB_GENERATION_ID) ?: 0L
    }

    override suspend fun overwriteTable(sourceTableName: TableName, targetTableName: TableName) {
        // MongoDB doesn't have SWAP/EXCHANGE - we do: copy source to target, drop source
        val sourceCollection = database.getCollection(sourceTableName.name)
        val targetCollection = database.getCollection(targetTableName.name)

        // Drop target if exists
        if (tableExists(targetTableName)) {
            dropTable(targetTableName)
        }

        // Rename source to target (atomic operation)
        sourceCollection.renameCollection(com.mongodb.MongoNamespace(config.database, targetTableName.name))

        log.info { "Renamed collection ${sourceTableName.name} to ${targetTableName.name}" }
    }

    override suspend fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        val sourceCollection = database.getCollection(sourceTableName.name)
        val targetCollection = database.getCollection(targetTableName.name)

        // Copy all documents from source to target
        val documents = sourceCollection.find().into(mutableListOf())

        if (documents.isNotEmpty()) {
            targetCollection.insertMany(documents)
            log.info { "Copied ${documents.size} documents from ${sourceTableName.name} to ${targetTableName.name}" }
        }
    }

    override suspend fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        val dedupe = stream.importType as? Dedupe
            ?: throw SystemErrorException("upsertTable called for non-dedupe stream")

        // primaryKey is List<List<String>>, flatten to get the field names
        val pkFields = dedupe.primaryKey.map { it.first() }.map { columnNameMapping[it]!! }
        val cursorField = if (dedupe.cursor.isNotEmpty()) {
            columnNameMapping[dedupe.cursor.first()]!!
        } else {
            COLUMN_NAME_AB_EXTRACTED_AT
        }

        log.info { "Upserting from ${sourceTableName.name} to ${targetTableName.name} with PK: $pkFields, cursor: $cursorField" }

        upsertWithAggregationPipeline(sourceTableName, targetTableName, pkFields, cursorField)
    }

    /**
     * Implements deduplication using MongoDB aggregation pipeline.
     * This is the NoSQL equivalent of SQL window functions.
     */
    private suspend fun upsertWithAggregationPipeline(
        sourceTableName: TableName,
        targetTableName: TableName,
        pkFields: List<String>,
        cursorField: String
    ) {
        val sourceCollection = database.getCollection(sourceTableName.name)
        val targetCollection = database.getCollection(targetTableName.name)

        // Step 1: Deduplicate source using aggregation pipeline
        val groupId = Document()
        pkFields.forEach { groupId[it] = "\$$it" }

        val pipeline = listOf(
            // Sort by cursor descending to get latest first
            Document("\$sort", Document(cursorField, -1)),
            // Group by PK, taking first (latest) document
            Document("\$group", Document("_id", groupId).append("doc", Document("\$first", "\$\$ROOT"))),
            // Replace root with the document
            Document("\$replaceRoot", Document("newRoot", "\$doc"))
        )

        val dedupedDocuments = sourceCollection.aggregate(pipeline).into(mutableListOf())

        log.info { "Deduped ${dedupedDocuments.size} documents from ${sourceCollection.namespace.collectionName}" }

        // Step 2: Upsert each deduped document into target
        dedupedDocuments.forEach { doc ->
            val filter = Document()
            pkFields.forEach { pkField ->
                filter[pkField] = doc[pkField]
            }

            // Upsert: replace if exists and cursor is newer, insert if not exists
            val existingDoc = targetCollection.find(filter).first()

            val shouldUpsert = if (existingDoc != null) {
                // Compare cursors - only update if source is newer
                val sourceCursor = doc.get(cursorField)
                val targetCursor = existingDoc.get(cursorField)
                compareCursors(sourceCursor, targetCursor) > 0
            } else {
                true // Document doesn't exist, insert it
            }

            if (shouldUpsert) {
                targetCollection.replaceOne(filter, doc, ReplaceOptions().upsert(true))
            }
        }

        log.info { "Upserted ${dedupedDocuments.size} documents into ${targetCollection.namespace.collectionName}" }
    }

    private fun compareCursors(source: Any?, target: Any?): Int {
        return when {
            source == null && target == null -> 0
            source == null -> -1
            target == null -> 1
            source is Comparable<*> && target is Comparable<*> -> {
                @Suppress("UNCHECKED_CAST")
                (source as Comparable<Any>).compareTo(target)
            }
            else -> source.toString().compareTo(target.toString())
        }
    }

    // Schema evolution methods - MongoDB is schemaless, so these are mostly no-ops
    override suspend fun discoverSchema(tableName: TableName): TableSchema {
        val collection = database.getCollection(tableName.name)

        // Verify collection has Airbyte columns
        val sampleDoc = collection.find().limit(1).first()
            ?: return TableSchema(emptyMap())

        val hasAllAirbyteColumns = COLUMN_NAMES.all { sampleDoc.containsKey(it) }

        if (!hasAllAirbyteColumns) {
            throw ConfigErrorException(
                "Collection '$tableName' exists but does not contain Airbyte's internal columns. " +
                "Airbyte can only sync to Airbyte-controlled collections."
            )
        }

        // MongoDB is schemaless - we infer schema from a sample document
        // For schema evolution, we return empty map since any field can be added
        return TableSchema(emptyMap())
    }

    override fun computeSchema(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping
    ): TableSchema {
        // MongoDB is schemaless - no schema to compute
        // All columns are implicitly supported
        return TableSchema(emptyMap())
    }

    override suspend fun ensureSchemaMatches(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping
    ) {
        // MongoDB is schemaless - no schema enforcement needed
        // Just verify the collection exists and has Airbyte columns
        if (!tableExists(tableName)) {
            throw SystemErrorException("Collection ${tableName.name} does not exist")
        }

        discoverSchema(tableName) // This will throw if Airbyte columns are missing
    }

    override suspend fun applyChangeset(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        tableName: TableName,
        expectedColumns: Map<String, ColumnType>,
        changeset: ColumnChangeset
    ) {
        // MongoDB is schemaless - no DDL changes needed
        // New columns are added implicitly when documents with those fields are inserted
        log.info { "Schema changeset ignored for MongoDB (schemaless): ${changeset.columnsToAdd.keys}" }
    }
}
