package io.airbyte.integrations.destination.databricks.jdbc

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.jdbc.SqlOperations

class DatabricksSqlOperations(override val isSchemaRequired: Boolean) : SqlOperations {
    override fun createSchemaIfNotExists(database: JdbcDatabase?, schemaName: String?) {
        TODO("Not yet implemented")
    }

    override fun createTableIfNotExists(
        database: JdbcDatabase,
        schemaName: String?,
        tableName: String?
    ) {
        TODO("Not yet implemented")
    }

    override fun createTableQuery(
        database: JdbcDatabase?,
        schemaName: String?,
        tableName: String?
    ): String? {
        throw UnsupportedOperationException("Use createTableIfNotExists")
    }

    override fun dropTableIfExists(
        database: JdbcDatabase,
        schemaName: String?,
        tableName: String?
    ) {
        TODO("Not yet implemented")
    }

    override fun truncateTableQuery(
        database: JdbcDatabase?,
        schemaName: String?,
        tableName: String?
    ): String {
        TODO("Not yet implemented")
    }

    override fun insertRecords(
        database: JdbcDatabase,
        records: List<PartialAirbyteMessage>,
        schemaName: String?,
        tableName: String?
    ) {
        throw UnsupportedOperationException("Databricks connector doesn't support standard inserts")
    }

    override fun insertTableQuery(
        database: JdbcDatabase?,
        schemaName: String?,
        sourceTableName: String?,
        destinationTableName: String?
    ): String? {
        TODO("Not implemented, seems to be used in GCSStreamCopier path")
    }

    override fun executeTransaction(database: JdbcDatabase, queries: List<String>) {
        throw UnsupportedOperationException("Use DestinationHandler#execute(Sql)")
    }

    override fun isValidData(data: JsonNode?): Boolean {
        throw UnsupportedOperationException("Data validation shouldn't be executed here")
    }
}
