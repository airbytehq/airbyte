/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.check

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.integrations.destination.redshift2.config.RedshiftConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.sql.SQLException
import javax.sql.DataSource

private val log = KotlinLogging.logger {}

/**
 * Redshift connection checker.
 * 
 * Performs basic connection validation by:
 * 1. Testing database connectivity
 * 2. Verifying schema access and permissions
 * 3. Ensuring the user has necessary privileges
 */
@Singleton
@SuppressFBWarnings(
    value = ["SQL_NONCONSTANT_STRING_PASSED_TO_EXECUTE"],
    justification = "Schema names are from configuration and table names are generated. SQL injection risk is minimal for connection checks."
)
class RedshiftChecker(
    private val dataSource: DataSource,
    private val configuration: RedshiftConfiguration,
) : DestinationChecker {

    override fun check() {
        try {
            // Test basic connectivity
            dataSource.connection.use { connection ->
                log.info { "Testing Redshift connection to ${configuration.host}:${configuration.port}/${configuration.database}" }
                
                // Verify we can execute queries
                connection.createStatement().use { statement ->
                    statement.executeQuery("SELECT 1").use { rs ->
                        require(rs.next()) { "Failed to execute basic query" }
                    }
                }
                
                // Check schema access
                val schema = configuration.schema
                log.info { "Verifying schema access: $schema" }
                
                connection.createStatement().use { statement ->
                    // Check if schema exists, if not try to create it
                    val schemaExists = statement.executeQuery(
                        """
                        SELECT EXISTS(
                            SELECT 1 FROM information_schema.schemata 
                            WHERE schema_name = '$schema'
                        )
                        """.trimIndent()
                    ).use { rs ->
                        rs.next() && rs.getBoolean(1)
                    }
                    
                    if (!schemaExists) {
                        log.info { "Schema $schema does not exist, attempting to create it" }
                        try {
                            statement.execute("CREATE SCHEMA IF NOT EXISTS $schema")
                            log.info { "Successfully created schema $schema" }
                        } catch (e: SQLException) {
                            throw IllegalStateException(
                                "Schema $schema does not exist and user does not have permission to create it. " +
                                "Please create the schema manually or grant CREATE privilege to the user.",
                                e
                            )
                        }
                    }
                }
                
                // Verify we can create and drop a test table
                val testTableName = "_airbyte_connection_test_${System.currentTimeMillis()}"
                log.info { "Testing table creation and deletion in schema ${configuration.schema}" }
                
                connection.createStatement().use { statement ->
                    try {
                        // Create test table
                        statement.execute(
                            """
                            CREATE TABLE ${configuration.schema}.$testTableName (
                                id INTEGER,
                                test_value VARCHAR(255)
                            )
                            """.trimIndent()
                        )
                        
                        // Insert a test row
                        statement.execute(
                            """
                            INSERT INTO ${configuration.schema}.$testTableName (id, test_value)
                            VALUES (1, 'test')
                            """.trimIndent()
                        )
                        
                        // Verify the row was inserted
                        val count = statement.executeQuery(
                            "SELECT COUNT(*) FROM ${configuration.schema}.$testTableName"
                        ).use { rs ->
                            rs.next()
                            rs.getInt(1)
                        }
                        
                        require(count == 1) {
                            "Failed to insert test row. Expected 1 row, found $count"
                        }
                        
                        log.info { "Successfully validated table operations" }
                    } finally {
                        // Clean up test table
                        try {
                            statement.execute("DROP TABLE IF EXISTS ${configuration.schema}.$testTableName")
                        } catch (e: SQLException) {
                            log.warn(e) { "Failed to clean up test table $testTableName" }
                        }
                    }
                }
                
                log.info { "Redshift connection check completed successfully" }
            }
        } catch (e: SQLException) {
            val errorMessage = buildErrorMessage(e)
            log.error(e) { "Redshift connection check failed: $errorMessage" }
            throw IllegalStateException(errorMessage, e)
        } catch (e: Exception) {
            log.error(e) { "Redshift connection check failed with unexpected error" }
            throw e
        }
    }
    
    private fun buildErrorMessage(e: SQLException): String {
        val sqlState = e.sqlState ?: "Unknown"
        val errorCode = e.errorCode
        
        return when {
            sqlState.startsWith("28") -> {
                // Authentication errors (28000, 28P01, etc.)
                "Authentication failed. Please verify your username and password. State code: $sqlState;"
            }
            sqlState.startsWith("3D") -> {
                // Database/catalog errors (3D000 = invalid catalog name)
                "Database '${configuration.database}' does not exist or is not accessible. State code: $sqlState;"
            }
            sqlState.startsWith("08") -> {
                // Connection errors (08001, 08006, etc.)
                "Failed to connect to Redshift at ${configuration.host}:${configuration.port}. " +
                "Please verify the host and port are correct and the server is reachable. State code: $sqlState;"
            }
            sqlState.startsWith("42") -> {
                // Syntax/permission errors
                "Permission denied or invalid operation. ${e.message} State code: $sqlState;"
            }
            else -> {
                "Connection check failed: ${e.message} State code: $sqlState; Error code: $errorCode"
            }
        }
    }
}
