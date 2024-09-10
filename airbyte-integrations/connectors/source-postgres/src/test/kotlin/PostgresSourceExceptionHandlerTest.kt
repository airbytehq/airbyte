/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

import io.airbyte.cdk.integrations.util.FailureType
import io.airbyte.integrations.source.postgres.PostgresSourceExceptionHandler
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.postgresql.util.PSQLException

class PostgresSourceExceptionHandlerTest {
    private var exceptionHandler: PostgresSourceExceptionHandler? = null

    @BeforeEach
    fun setUp() {
        exceptionHandler = PostgresSourceExceptionHandler()
    }

    @Test
    fun testTranslateTemporaryFileSizeExceedsLimitException() {
        val exception =
            PSQLException("ERROR: temporary file size exceeds temp_file_limit (500kB)", null)
        val externalMessage = exceptionHandler!!.getExternalMessage(exception)
        Assertions.assertTrue(exceptionHandler!!.checkErrorType(exception, FailureType.TRANSIENT))
        Assertions.assertEquals("Encountered an error while reading the database", externalMessage)
    }
}
