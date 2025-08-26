/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.typing_deduping

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import java.util.stream.Stream
import net.snowflake.client.jdbc.SnowflakeSQLException
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.function.Executable
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource
import org.mockito.Mockito.any
import org.mockito.Mockito.anyString
import org.mockito.Mockito.doThrow
import org.mockito.Mockito.mock
import org.mockito.Mockito.reset
import org.mockito.Mockito.times
import org.mockito.Mockito.verify
import org.mockito.Mockito.`when`
import org.mockito.kotlin.eq

class SnowflakeDestinationHandlerTest {

    private val database = mock(JdbcDatabase::class.java)
    private val metadataDatabase = mock(JdbcDatabase::class.java)
    private val destinationHandler =
        SnowflakeDestinationHandler("mock-database-name", database, "mock-schema", metadataDatabase)
    private val destinationHandlerWithSingleConnection =
        SnowflakeDestinationHandler("mock-database-name", database, "mock-schema")

    @ParameterizedTest
    @MethodSource("argumentsForExceptionThrownWithExecute")
    fun verifyExecuteKnownExceptionsAreReportedAsConfigError(
        message: String,
        isConfigErrorException: Boolean
    ) {
        doThrow(SnowflakeSQLException(message)).`when`(database).execute(any(String::class.java))
        executeAndAssertThrowable(
            isConfigErrorException,
        ) {
            destinationHandler.execute(Sql.of("Mock SQL statement"))
        }
    }
    private fun executeAndAssertThrowable(isConfigErrorException: Boolean, executable: Executable) {
        if (isConfigErrorException) {
            assertThrows(ConfigErrorException::class.java, executable)
        } else {
            assertThrows(RuntimeException::class.java, executable)
        }
    }
    @Test
    fun verifyCreateNamespaceChecksForSchemaExistence() {
        val mockSchemaName = "mockSchema"
        val showSchemasReturn = """
            {"name":"$mockSchemaName"}
        """.trimIndent()
        // Mock the metadata database for schema checks
        `when`(metadataDatabase.unsafeQuery(eq("show schemas;")))
            .thenReturn(
                listOf(
                        Jsons.deserialize(
                            showSchemasReturn,
                        ),
                    )
                    .stream(),
            )
        destinationHandler.createNamespaces(setOf(mockSchemaName))
        // verify database.execute is not called (schema exists)
        verify(database, times(0)).execute(anyString())
    }

    @Test
    fun verifyMetadataQueriesUseMetadataConnection() {
        // Given: A handler with separate metadata connection
        val mockSchemaName = "mockSchema"
        val showSchemasReturn = """
            {"name":"$mockSchemaName"}
        """.trimIndent()

        // When checking if schema exists (metadata query)
        `when`(metadataDatabase.unsafeQuery(eq("show schemas;")))
            .thenReturn(listOf(Jsons.deserialize(showSchemasReturn)).stream())

        // Then: Metadata database should be used, not regular database
        destinationHandler.createNamespaces(setOf(mockSchemaName))

        // Verify metadata connection was used for SHOW SCHEMAS
        verify(metadataDatabase, times(1)).unsafeQuery(eq("show schemas;"))
        // Verify regular database was NOT used for metadata query
        verify(database, times(0)).unsafeQuery(anyString())
        // Schema exists, so no CREATE SCHEMA should be executed
        verify(database, times(0)).execute(anyString())
    }

    @Test
    fun verifyDataOperationsUseRegularConnection() {
        // Given: A SQL statement for data manipulation
        val dataSql = Sql.of("INSERT INTO table VALUES (1, 2, 3)")

        // When: Executing a data operation
        destinationHandler.execute(dataSql)

        // Then: Regular database connection should be used
        verify(database, times(1)).execute(anyString())
        // Metadata connection should NOT be used for data operations
        verify(metadataDatabase, times(0)).execute(anyString())
    }

    @Test
    fun verifySchemaCreationUsesRegularConnection() {
        // Given: A schema that doesn't exist
        val newSchemaName = "newSchema"
        `when`(metadataDatabase.unsafeQuery(eq("show schemas;")))
            .thenReturn(Stream.empty()) // No schemas exist

        // When: Creating a new schema
        destinationHandler.createNamespaces(setOf(newSchemaName))

        // Then: Metadata connection used for checking existence
        verify(metadataDatabase, times(1)).unsafeQuery(eq("show schemas;"))
        // Regular connection used for CREATE SCHEMA (data operation)
        verify(database, times(1)).execute(eq("CREATE SCHEMA IF NOT EXISTS \"$newSchemaName\";"))
        // Metadata connection should NOT execute CREATE statements
        verify(metadataDatabase, times(0)).execute(anyString())
    }

    @Test
    fun verifyBackwardCompatibilityWithSingleConnection() {
        // Given: A handler with only one connection (backward compatibility)
        val mockSchemaName = "mockSchema"
        `when`(database.unsafeQuery(eq("show schemas;"))).thenReturn(Stream.empty())

        // When: Using handler with single connection
        destinationHandlerWithSingleConnection.createNamespaces(setOf(mockSchemaName))

        // Then: The single database connection handles both metadata and data operations
        verify(database, times(1)).unsafeQuery(eq("show schemas;"))
        verify(database, times(1)).execute(eq("CREATE SCHEMA IF NOT EXISTS \"$mockSchemaName\";"))
        // Metadata database should not be involved (it's the same as database)
        verify(metadataDatabase, times(0)).unsafeQuery(anyString())
        verify(metadataDatabase, times(0)).execute(anyString())
    }

    @AfterEach
    fun tearDown() {
        reset(database)
        reset(metadataDatabase)
    }

    companion object {
        private const val UNKNOWN_EXCEPTION_MESSAGE = "Unknown Exception"
        private const val PERMISSION_EXCEPTION_PARTIAL_MSG =
            "but current role has no privileges on it"
        private const val IP_NOT_IN_WHITE_LIST_EXCEPTION_PARTIAL_MSG =
            "not allowed to access Snowflake"
        @JvmStatic
        fun argumentsForExceptionThrownWithExecute(): Stream<Arguments> {
            return Stream.of(
                Arguments.of(UNKNOWN_EXCEPTION_MESSAGE, false),
                Arguments.of(PERMISSION_EXCEPTION_PARTIAL_MSG, true),
                Arguments.of(IP_NOT_IN_WHITE_LIST_EXCEPTION_PARTIAL_MSG, true)
            )
        }
    }
}
