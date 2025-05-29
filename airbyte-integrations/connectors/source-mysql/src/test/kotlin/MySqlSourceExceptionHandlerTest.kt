/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

import io.airbyte.cdk.integrations.util.FailureType
import io.airbyte.integrations.source.mysql.MySqlSourceExceptionHandler
import java.io.EOFException
import java.sql.SQLSyntaxErrorException
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class MySqlSourceExceptionHandlerTest {
    private var exceptionHandler: MySqlSourceExceptionHandler? = null

    @BeforeEach
    fun setUp() {
        exceptionHandler = MySqlSourceExceptionHandler()
    }

    @Test
    fun testTranslateMySQLSyntaxException() {
        val exception = SQLSyntaxErrorException("Unknown column 'xmin' in 'field list'")
        val externalMessage = exceptionHandler!!.getExternalMessage(exception)
        Assertions.assertTrue(exceptionHandler!!.checkErrorType(exception, FailureType.CONFIG))
        Assertions.assertEquals(
            "A column needed by MySQL source connector is missing in the database",
            externalMessage
        )
    }

    @Test
    fun testTranslateEOFException() {
        val exception =
            EOFException(
                "Can not read response from server. Expected to read 4 bytes, read 0 bytes before connection was unexpectedly lost."
            )
        val externalMessage = exceptionHandler!!.getExternalMessage(exception)
        Assertions.assertTrue(exceptionHandler!!.checkErrorType(exception, FailureType.TRANSIENT))
        Assertions.assertEquals("Can not read data from MySQL server", externalMessage)
    }
}
