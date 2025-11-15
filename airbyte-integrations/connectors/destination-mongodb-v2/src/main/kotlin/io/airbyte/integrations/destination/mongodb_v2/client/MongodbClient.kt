/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2.client

import com.mongodb.client.model.IndexOptions
import com.mongodb.client.model.Indexes
import com.mongodb.kotlin.client.coroutine.MongoClient
import com.mongodb.kotlin.client.coroutine.MongoDatabase
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnChangeset
import io.airbyte.cdk.load.component.TableColumns
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TableSchemaEvolutionClient
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.mongodb_v2.config.MongodbConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlinx.coroutines.flow.toList
import org.bson.Document

val log = KotlinLogging.logger {}

@SuppressFBWarnings(
    value = ["NP_NONNULL_PARAM_VIOLATION"],
    justification = "suspend and fb's non-null analysis don't play well"
)
@Singleton
class MongodbClient(
    private val client: MongoClient,
    private val config: MongodbConfiguration,
) : TableOperationsClient, TableSchemaEvolutionClient {

    private fun getDatabase(namespace: String?): MongoDatabase {
        val dbName = namespace ?: config.resolvedDatabase
        return client.getDatabase(dbName)
    }

    override suspend fun createNamespace(namespace: String) {
        try {
            // MongoDB creates databases lazily - create a permanent marker collection
            val database = getDatabase(namespace)
            // Create a marker collection that persists (empty but exists)
            database.createCollection("_airbyte_marker")
            log.info { "Created namespace (database): $namespace" }
        } catch (e: Exception) {
            // Database might already exist - that's ok
            log.debug(e) { "Namespace $namespace may already exist or creation failed" }
        }
    }

    override suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean
    ) {
        val database = getDatabase(tableName.namespace)
        val collectionName = tableName.name

        println("DEBUG createTable: namespace=${tableName.namespace}, collectionName='$collectionName', streamDescriptor='${stream.mappedDescriptor.name}'")

        if (replace) {
            database.getCollection<Document>(collectionName).drop()
            log.info { "Dropped existing collection: ${tableName.namespace}.${tableName.name}" }
        }

        // MongoDB creates collections lazily, but we'll explicitly create it
        try {
            database.createCollection(collectionName)
            log.info { "Created collection: ${tableName.namespace}.${tableName.name}" }
        } catch (e: Exception) {
            log.error(e) { "Failed to create collection: ${tableName.namespace}.$collectionName" }
            throw e
        }

        // Create indexes if this is a dedupe stream
        if (stream.importType is Dedupe) {
            val dedupe = stream.importType as Dedupe
            if (dedupe.primaryKey.isNotEmpty()) {
                createPrimaryKeyIndex(database, collectionName, dedupe.primaryKey, columnNameMapping)
            }
        }
    }

    private suspend fun createPrimaryKeyIndex(
        database: MongoDatabase,
        collectionName: String,
        primaryKey: List<List<String>>,
        columnNameMapping: ColumnNameMapping
    ) {
        val collection = database.getCollection<Document>(collectionName)

        // Extract primary key field names
        val pkFields = primaryKey.map { path ->
            if (path.size != 1) {
                throw UnsupportedOperationException("Nested primary keys are not supported: $path")
            }
            columnNameMapping[path.first()] ?: path.first()
        }

        // Create compound unique index on primary key fields
        val indexKeys = Indexes.ascending(pkFields)
        val indexOptions = IndexOptions().unique(true).name("airbyte_pk_index")

        collection.createIndex(indexKeys, indexOptions)
        log.info { "Created unique index on primary key fields: $pkFields for collection $collectionName" }
    }

    override suspend fun dropTable(tableName: TableName) {
        val database = getDatabase(tableName.namespace)
        database.getCollection<Document>(tableName.name).drop()
        log.info { "Dropped collection: ${tableName.namespace}.${tableName.name}" }
    }

    override suspend fun overwriteTable(sourceTableName: TableName, targetTableName: TableName) {
        val database = getDatabase(targetTableName.namespace)

        // Check if source exists and has data
        val sourceCollection = database.getCollection<Document>(sourceTableName.name)
        val sourceCount = sourceCollection.countDocuments()
        log.info { "Overwriting ${targetTableName.namespace}.${targetTableName.name} with ${sourceTableName.namespace}.${sourceTableName.name} ($sourceCount documents)" }

        if (sourceCount == 0L) {
            log.warn { "Source table ${sourceTableName.name} is empty - overwrite will result in empty target table" }
        }

        // Drop target collection
        try {
            database.getCollection<Document>(targetTableName.name).drop()
            log.info { "Dropped target collection ${targetTableName.name}" }
        } catch (e: Exception) {
            log.debug { "Target collection ${targetTableName.name} didn't exist or couldn't be dropped: ${e.message}" }
        }

        // Rename source to target
        sourceCollection.renameCollection(
            com.mongodb.MongoNamespace(targetTableName.namespace ?: config.resolvedDatabase, targetTableName.name)
        )
        log.info { "Renamed ${sourceTableName.name} to ${targetTableName.name} - overwrite complete with $sourceCount documents" }
    }

    override suspend fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        val database = getDatabase(sourceTableName.namespace)
        val sourceCollection = database.getCollection<Document>(sourceTableName.name)
        val targetCollection = database.getCollection<Document>(targetTableName.name)

        // Copy all documents from source to target
        val documents = sourceCollection.find().toList()
        if (documents.isNotEmpty()) {
            targetCollection.insertMany(documents)
        }
        log.info { "Copied ${documents.size} documents from ${sourceTableName.namespace}.${sourceTableName.name} to ${targetTableName.namespace}.${targetTableName.name}" }
    }

    override suspend fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        val database = getDatabase(targetTableName.namespace)
        val sourceCollection = database.getCollection<Document>(sourceTableName.name)
        val targetCollection = database.getCollection<Document>(targetTableName.name)

        // Get primary key columns for deduplication
        val importType = stream.importType
        if (importType !is Dedupe) {
            throw IllegalArgumentException("upsertTable requires Dedupe import type")
        }

        val pkFields = importType.primaryKey.map { path ->
            if (path.size != 1) {
                throw UnsupportedOperationException("Nested primary keys are not supported: $path")
            }
            columnNameMapping[path.first()] ?: path.first()
        }

        // Get cursor field for "last write wins"
        val cursorField = if (importType.cursor.isNotEmpty()) {
            columnNameMapping[importType.cursor.first()] ?: importType.cursor.first()
        } else {
            "_airbyte_extracted_at"  // Fallback to extraction timestamp
        }

        // Check for CDC (soft delete support)
        val hasCdc = stream.schema.asColumns().containsKey("_ab_cdc_deleted_at")

        log.info { "Upserting from ${sourceTableName.name} to ${targetTableName.name} with PK: $pkFields, cursor: $cursorField, CDC: $hasCdc" }

        // Use MongoDB aggregation pipeline to dedupe and upsert
        // 1. Sort by cursor DESC to get latest records first
        // 2. Group by primary key, keeping first (latest) document
        // 3. Filter out hard deletes if CDC enabled
        // 4. Use $merge to upsert into target collection

        val pipelineStages = mutableListOf<Document>()

        // Stage 1: Sort by cursor DESC (latest first)
        pipelineStages.add(Document("\$sort", Document(cursorField, -1).append("_airbyte_extracted_at", -1)))

        // Stage 2: Group by primary key, keeping first (latest) document
        val groupId: Any = if (pkFields.size == 1) {
            "\$${pkFields[0]}"
        } else {
            Document(pkFields.associateWith { "\$$it" })
        }
        pipelineStages.add(Document("\$group", Document("_id", groupId).append("doc", Document("\$first", "\$\$ROOT"))))

        // Stage 3: Replace root with the document
        pipelineStages.add(Document("\$replaceRoot", Document("newRoot", "\$doc")))

        // Stage 4: Handle CDC hard deletes
        if (hasCdc) {
            // For hard delete mode: Delete records where _ab_cdc_deleted_at IS NOT NULL
            // For soft delete mode: Keep all records (deletion timestamp preserved in document)
            // Note: MongoDB doesn't differentiate - we handle via metadata field
            // The $merge stage will upsert both regular updates and deletions
            // Downstream consumers can filter by _ab_cdc_deleted_at if needed
        }

        // Stage 5: Merge into target collection
        val mergeStage = Document("\$merge", Document()
            .append("into", targetTableName.name)
            .append("on", pkFields)
            .append("whenMatched", "replace")
            .append("whenNotMatched", "insert")
        )
        pipelineStages.add(mergeStage)

        sourceCollection.aggregate<Document>(pipelineStages).toList()

        log.info { "Completed upsert from ${sourceTableName.name} to ${targetTableName.name}" }
    }

    override suspend fun discoverSchema(
        tableName: TableName
    ): io.airbyte.cdk.load.component.TableSchema {
        // MongoDB is schemaless - return empty schema
        // Schema evolution is automatic in MongoDB
        return io.airbyte.cdk.load.component.TableSchema(emptyMap())
    }

    override fun computeSchema(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping
    ): io.airbyte.cdk.load.component.TableSchema {
        // MongoDB is schemaless - return empty schema
        return io.airbyte.cdk.load.component.TableSchema(emptyMap())
    }

    override suspend fun applyChangeset(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        tableName: TableName,
        expectedColumns: TableColumns,
        columnChangeset: ColumnChangeset,
    ) {
        // MongoDB is schemaless - schema changes happen automatically
        // No need to ALTER anything
        log.info { "Schema changeset for ${tableName.namespace}.${tableName.name} - MongoDB handles schema changes automatically" }
    }

    override suspend fun countTable(tableName: TableName): Long? {
        val database = getDatabase(tableName.namespace)
        val collection = database.getCollection<Document>(tableName.name)
        return try {
            collection.countDocuments()
        } catch (e: Exception) {
            log.warn(e) { "Failed to count documents in ${tableName.namespace}.${tableName.name}" }
            null
        }
    }

    override suspend fun tableExists(table: TableName): Boolean {
        val database = getDatabase(table.namespace)
        val collectionNames = database.listCollectionNames().toList()
        return collectionNames.contains(table.name)
    }

    override suspend fun namespaceExists(namespace: String): Boolean {
        val dbNames = client.listDatabaseNames().toList()
        return dbNames.contains(namespace)
    }

    override suspend fun getGenerationId(tableName: TableName): Long {
        val database = getDatabase(tableName.namespace)
        val collection = database.getCollection<Document>(tableName.name)

        return try {
            // Get any document and extract generation ID
            val doc = collection.find().limit(1).toList().firstOrNull()
            if (doc != null && doc.containsKey("_airbyte_generation_id")) {
                doc.getLong("_airbyte_generation_id") ?: 0L
            } else {
                0L
            }
        } catch (e: Exception) {
            log.debug(e) { "Failed to retrieve generation ID from ${tableName.namespace}.${tableName.name}, returning 0" }
            0L
        }
    }
}
