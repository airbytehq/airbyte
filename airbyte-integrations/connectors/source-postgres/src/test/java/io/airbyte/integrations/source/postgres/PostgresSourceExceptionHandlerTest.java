/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.postgres;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.postgresql.util.PSQLException;

public class PostgresSourceExceptionHandlerTest {

  private PostgresSourceExceptionHandler exceptionHandler;

  @BeforeEach
  void setUp() {
    exceptionHandler = new PostgresSourceExceptionHandler();
    exceptionHandler.initializeErrorDictionary();
  }

  @Test
  void testTranslateTemporaryFileSizeExceedsLimitException() {
    PSQLException exception = new PSQLException("ERROR: temporary file size exceeds temp_file_limit (500kB)", null);
    String external_message = exceptionHandler.getExternalMessage(exception);
    assertEquals(exceptionHandler.DATABASE_READ_ERROR, external_message);
  }

}
