/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.util

import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.exceptions.ConnectionErrorException
import java.sql.SQLException
import java.sql.SQLSyntaxErrorException
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class ConnectorExceptionUtilTest {
    @get:Test
    val isConfigErrorForConfigException: Unit
        get() {
            val configErrorException = ConfigErrorException(CONFIG_EXCEPTION_MESSAGE)
            Assertions.assertTrue(ConnectorExceptionUtil.isConfigError(configErrorException))
        }

    @get:Test
    val isConfigErrorForConnectionException: Unit
        get() {
            val connectionErrorException = ConnectionErrorException(CONFIG_EXCEPTION_MESSAGE)
            Assertions.assertTrue(ConnectorExceptionUtil.isConfigError(connectionErrorException))
        }

    @get:Test
    val isConfigErrorForRecoveryPSQLException: Unit
        get() {
            val recoveryPSQLException = SQLException(RECOVERY_EXCEPTION_MESSAGE)
            Assertions.assertTrue(ConnectorExceptionUtil.isConfigError(recoveryPSQLException))
        }

    @get:Test
    val isConfigErrorForUnknownColumnSQLSyntaxErrorException: Unit
        get() {
            val unknownColumnSQLSyntaxErrorException =
                SQLSyntaxErrorException(UNKNOWN_COLUMN_SQL_EXCEPTION_MESSAGE)
            Assertions.assertTrue(
                ConnectorExceptionUtil.isConfigError(unknownColumnSQLSyntaxErrorException)
            )
        }

    @get:Test
    val isConfigErrorForCommonSQLException: Unit
        get() {
            val recoveryPSQLException = SQLException(COMMON_EXCEPTION_MESSAGE)
            Assertions.assertFalse(ConnectorExceptionUtil.isConfigError(recoveryPSQLException))
        }

    @get:Test
    val isConfigErrorForCommonException: Unit
        get() {
            Assertions.assertFalse(ConnectorExceptionUtil.isConfigError(Exception()))
        }

    @get:Test
    val displayMessageForConfigException: Unit
        get() {
            val configErrorException = ConfigErrorException(CONFIG_EXCEPTION_MESSAGE)
            val actualDisplayMessage =
                ConnectorExceptionUtil.getDisplayMessage(configErrorException)
            Assertions.assertEquals(CONFIG_EXCEPTION_MESSAGE, actualDisplayMessage)
        }

    @get:Test
    val displayMessageForConnectionError: Unit
        get() {
            val testCode = "test code"
            val errorCode = -1
            val connectionErrorException =
                ConnectionErrorException(testCode, errorCode, CONFIG_EXCEPTION_MESSAGE, Exception())
            val actualDisplayMessage =
                ConnectorExceptionUtil.getDisplayMessage(connectionErrorException)
            Assertions.assertEquals(
                String.format(
                    CONNECTION_ERROR_MESSAGE_TEMPLATE,
                    testCode,
                    errorCode,
                    CONFIG_EXCEPTION_MESSAGE
                ),
                actualDisplayMessage
            )
        }

    @get:Test
    val displayMessageForRecoveryException: Unit
        get() {
            val recoveryException = SQLException(RECOVERY_EXCEPTION_MESSAGE)
            val actualDisplayMessage = ConnectorExceptionUtil.getDisplayMessage(recoveryException)
            Assertions.assertEquals(
                ConnectorExceptionUtil.RECOVERY_CONNECTION_ERROR_MESSAGE,
                actualDisplayMessage
            )
        }

    @get:Test
    val displayMessageForUnknownSQLErrorException: Unit
        get() {
            val unknownColumnSQLSyntaxErrorException =
                SQLSyntaxErrorException(UNKNOWN_COLUMN_SQL_EXCEPTION_MESSAGE)
            val actualDisplayMessage =
                ConnectorExceptionUtil.getDisplayMessage(unknownColumnSQLSyntaxErrorException)
            Assertions.assertEquals(UNKNOWN_COLUMN_SQL_EXCEPTION_MESSAGE, actualDisplayMessage)
        }

    @get:Test
    val displayMessageForCommonException: Unit
        get() {
            val exception: Exception = SQLException(COMMON_EXCEPTION_MESSAGE)
            val actualDisplayMessage = ConnectorExceptionUtil.getDisplayMessage(exception)
            Assertions.assertEquals(
                String.format(
                    ConnectorExceptionUtil.COMMON_EXCEPTION_MESSAGE_TEMPLATE,
                    COMMON_EXCEPTION_MESSAGE
                ),
                actualDisplayMessage
            )
        }

    @get:Test
    val rootConfigErrorFromConfigException: Unit
        get() {
            val configErrorException = ConfigErrorException(CONFIG_EXCEPTION_MESSAGE)
            val exception = Exception(COMMON_EXCEPTION_MESSAGE, configErrorException)

            val actualRootConfigError = ConnectorExceptionUtil.getRootConfigError(exception)
            Assertions.assertEquals(configErrorException, actualRootConfigError)
        }

    @get:Test
    val rootConfigErrorFromRecoverySQLException: Unit
        get() {
            val recoveryException = SQLException(RECOVERY_EXCEPTION_MESSAGE)
            val runtimeException = RuntimeException(COMMON_EXCEPTION_MESSAGE, recoveryException)
            val exception = Exception(runtimeException)

            val actualRootConfigError = ConnectorExceptionUtil.getRootConfigError(exception)
            Assertions.assertEquals(recoveryException, actualRootConfigError)
        }

    @get:Test
    val rootConfigErrorFromUnknownSQLErrorException: Unit
        get() {
            val unknownSQLErrorException: SQLException =
                SQLSyntaxErrorException(UNKNOWN_COLUMN_SQL_EXCEPTION_MESSAGE)
            val runtimeException =
                RuntimeException(COMMON_EXCEPTION_MESSAGE, unknownSQLErrorException)
            val exception = Exception(runtimeException)

            val actualRootConfigError = ConnectorExceptionUtil.getRootConfigError(exception)
            Assertions.assertEquals(unknownSQLErrorException, actualRootConfigError)
        }

    @get:Test
    val rootConfigErrorFromNonConfigException: Unit
        get() {
            val configErrorException = SQLException(CONFIG_EXCEPTION_MESSAGE)
            val exception = Exception(COMMON_EXCEPTION_MESSAGE, configErrorException)

            val actualRootConfigError = ConnectorExceptionUtil.getRootConfigError(exception)
            Assertions.assertEquals(exception, actualRootConfigError)
        }

    companion object {
        const val CONFIG_EXCEPTION_MESSAGE: String = "test message"
        const val RECOVERY_EXCEPTION_MESSAGE: String =
            "FATAL: terminating connection due to conflict with recovery"
        const val COMMON_EXCEPTION_MESSAGE: String = "something happens with connection"
        const val CONNECTION_ERROR_MESSAGE_TEMPLATE: String =
            "State code: %s; Error code: %s; Message: %s"
        const val UNKNOWN_COLUMN_SQL_EXCEPTION_MESSAGE: String =
            "Unknown column 'table.column' in 'field list'"
    }
}
