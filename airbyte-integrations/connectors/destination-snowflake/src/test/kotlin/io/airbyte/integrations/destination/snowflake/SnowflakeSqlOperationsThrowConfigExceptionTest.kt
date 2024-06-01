/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.DestinationConfig
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.json.Jsons.emptyObject
import io.airbyte.integrations.destination.snowflake.operation.SnowflakeStagingClient
import java.sql.SQLException
import java.util.stream.Stream
import net.snowflake.client.jdbc.SnowflakeSQLException
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.function.Executable
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource
import org.mockito.Mockito

/**
 * This class contains tests to make sure we catch some Snowflake's exceptions and convert them to
 * Airbyte Config Exception (Ex. User has no required permission, User's IP is not in Whitelist,
 * etc)
 */
internal class SnowflakeSqlOperationsThrowConfigExceptionTest {
    @ParameterizedTest
    @MethodSource("testArgumentsForDbExecute")
    fun testCatchNoPermissionOnExecuteException(
        message: String,
        shouldCapture: Boolean,
        executable: Executable
    ) {
        try {
            Mockito.doThrow(SnowflakeSQLException(message))
                .`when`(dbForExecuteQuery)
                .execute(Mockito.anyString())
        } catch (e: SQLException) {
            // This would not be expected, but the `execute` method above will flag as an unhandled
            // exception
            assert(false)
        }
        executeTest(message, shouldCapture, executable)
    }

    @ParameterizedTest
    @MethodSource("testArgumentsForDbUnsafeQuery")
    fun testCatchNoPermissionOnUnsafeQueryException(
        message: String,
        shouldCapture: Boolean,
        executable: Executable
    ) {
        try {
            Mockito.doThrow(SnowflakeSQLException(message))
                .`when`(dbForRunUnsafeQuery)
                .unsafeQuery(Mockito.anyString())
        } catch (e: SQLException) {
            // This would not be expected, but the `execute` method above will flag as an unhandled
            // exception
            assert(false)
        }
        executeTest(message, shouldCapture, executable)
    }

    private fun executeTest(message: String, shouldCapture: Boolean, executable: Executable) {
        val exception = Assertions.assertThrows(Exception::class.java, executable)
        if (shouldCapture) {
            Assertions.assertInstanceOf(ConfigErrorException::class.java, exception)
        } else {
            Assertions.assertInstanceOf(SnowflakeSQLException::class.java, exception)
            Assertions.assertEquals(exception.message, message)
        }
    }

    companion object {
        private const val SCHEMA_NAME = "dummySchemaName"
        private const val STAGE_NAME = "dummyStageName"
        private const val TABLE_NAME = "dummyTableName"
        private const val STAGE_PATH = "stagePath/2022/"
        private val FILE_PATH = listOf("filepath/filename")

        private const val TEST_NO_CONFIG_EXCEPTION_CATCHED = "TEST"
        private const val TEST_PERMISSION_EXCEPTION_CATCHED =
            "but current role has no privileges on it"
        private const val TEST_IP_NOT_IN_WHITE_LIST_EXCEPTION_CATCHED =
            "not allowed to access Snowflake"

        private var snowflakeStagingSqlOperations: SnowflakeStagingClient? = null

        private var snowflakeSqlOperations: SnowflakeSqlOperations? = null
        private var jdbcOperations: SnowflakeDestination.SnowflakeOperations? = null

        private val dbForExecuteQuery: JdbcDatabase = Mockito.mock(JdbcDatabase::class.java)
        private val dbForRunUnsafeQuery: JdbcDatabase = Mockito.mock(JdbcDatabase::class.java)

        private var createStageIfNotExists: Executable? = null
        private var dropStageIfExists: Executable? = null
        private var copyIntoTableFromStage: Executable? = null

        private var createSchemaIfNotExists: Executable? = null
        private var isSchemaExists: Executable? = null
        private var createTableIfNotExists: Executable? = null
        private var dropTableIfExists: Executable? = null

        @JvmStatic
        @BeforeAll
        fun setup(): Unit {
            DestinationConfig.initialize(emptyObject())

            snowflakeStagingSqlOperations = SnowflakeStagingClient(SnowflakeSQLNameTransformer())
            snowflakeSqlOperations = SnowflakeSqlOperations()
            jdbcOperations =
                SnowflakeDestination.SnowflakeOperations(snowflakeStagingSqlOperations!!)

            createStageIfNotExists = Executable {
                snowflakeStagingSqlOperations!!.createStageIfNotExists(
                    dbForExecuteQuery,
                    STAGE_NAME
                )
            }
            dropStageIfExists = Executable {
                snowflakeStagingSqlOperations!!.dropStageIfExists(dbForExecuteQuery, STAGE_NAME)
            }
            copyIntoTableFromStage = Executable {
                snowflakeStagingSqlOperations!!.copyIntoTableFromStage(
                    dbForExecuteQuery,
                    STAGE_NAME,
                    STAGE_PATH,
                    FILE_PATH,
                    TABLE_NAME,
                    SCHEMA_NAME
                )
            }

            createSchemaIfNotExists = Executable {
                snowflakeSqlOperations!!.createSchemaIfNotExists(dbForExecuteQuery, SCHEMA_NAME)
            }
            isSchemaExists = Executable {
                snowflakeSqlOperations!!.isSchemaExists(dbForRunUnsafeQuery, SCHEMA_NAME)
            }
            createTableIfNotExists = Executable {
                jdbcOperations!!.createTableIfNotExists(dbForExecuteQuery, SCHEMA_NAME, TABLE_NAME)
            }
            dropTableIfExists = Executable {
                jdbcOperations!!.dropTableIfExists(dbForExecuteQuery, SCHEMA_NAME, TABLE_NAME)
            }
        }

        @JvmStatic
        private fun testArgumentsForDbExecute(): Stream<Arguments> {
            return Stream.of(
                Arguments.of(TEST_NO_CONFIG_EXCEPTION_CATCHED, false, createStageIfNotExists),
                Arguments.of(TEST_PERMISSION_EXCEPTION_CATCHED, true, createStageIfNotExists),
                Arguments.of(
                    TEST_IP_NOT_IN_WHITE_LIST_EXCEPTION_CATCHED,
                    true,
                    createStageIfNotExists
                ),
                Arguments.of(TEST_NO_CONFIG_EXCEPTION_CATCHED, false, dropStageIfExists),
                Arguments.of(TEST_PERMISSION_EXCEPTION_CATCHED, true, dropStageIfExists),
                Arguments.of(TEST_IP_NOT_IN_WHITE_LIST_EXCEPTION_CATCHED, true, dropStageIfExists),
                Arguments.of(TEST_NO_CONFIG_EXCEPTION_CATCHED, false, copyIntoTableFromStage),
                Arguments.of(TEST_PERMISSION_EXCEPTION_CATCHED, true, copyIntoTableFromStage),
                Arguments.of(
                    TEST_IP_NOT_IN_WHITE_LIST_EXCEPTION_CATCHED,
                    true,
                    copyIntoTableFromStage
                ),
                Arguments.of(TEST_NO_CONFIG_EXCEPTION_CATCHED, false, createSchemaIfNotExists),
                Arguments.of(TEST_PERMISSION_EXCEPTION_CATCHED, true, createSchemaIfNotExists),
                Arguments.of(
                    TEST_IP_NOT_IN_WHITE_LIST_EXCEPTION_CATCHED,
                    true,
                    createSchemaIfNotExists
                ),
                Arguments.of(TEST_NO_CONFIG_EXCEPTION_CATCHED, false, createTableIfNotExists),
                Arguments.of(TEST_PERMISSION_EXCEPTION_CATCHED, true, createTableIfNotExists),
                Arguments.of(
                    TEST_IP_NOT_IN_WHITE_LIST_EXCEPTION_CATCHED,
                    true,
                    createTableIfNotExists
                ),
                Arguments.of(TEST_NO_CONFIG_EXCEPTION_CATCHED, false, dropTableIfExists),
                Arguments.of(TEST_PERMISSION_EXCEPTION_CATCHED, true, dropTableIfExists),
                Arguments.of(TEST_IP_NOT_IN_WHITE_LIST_EXCEPTION_CATCHED, true, dropTableIfExists)
            )
        }

        @JvmStatic
        private fun testArgumentsForDbUnsafeQuery(): Stream<Arguments> {
            return Stream.of(
                Arguments.of(TEST_NO_CONFIG_EXCEPTION_CATCHED, false, isSchemaExists),
                Arguments.of(TEST_PERMISSION_EXCEPTION_CATCHED, true, isSchemaExists),
                Arguments.of(TEST_IP_NOT_IN_WHITE_LIST_EXCEPTION_CATCHED, true, isSchemaExists)
            )
        }
    }
}
