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
    private val destinationHandler =
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
        `when`(database.unsafeQuery(eq("show schemas;")))
            .thenReturn(
                listOf(
                        Jsons.deserialize(
                            showSchemasReturn,
                        ),
                    )
                    .stream(),
            )
        destinationHandler.createNamespaces(setOf(mockSchemaName))
        // verify database.execute is not called
        verify(database, times(0)).execute(anyString())
    }

    @AfterEach
    fun tearDown() {
        reset(database)
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
