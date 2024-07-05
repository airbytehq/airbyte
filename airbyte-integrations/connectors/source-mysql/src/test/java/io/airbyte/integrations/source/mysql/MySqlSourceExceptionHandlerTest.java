/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.mysql;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.io.EOFException;
import java.sql.SQLSyntaxErrorException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class MySqlSourceExceptionHandlerTest {

  private MySqlSourceExceptionHandler exceptionHandler;

  @BeforeEach
  void setUp() {
    exceptionHandler = new MySqlSourceExceptionHandler();
    exceptionHandler.initializeErrorDictionary();
  }

  @Test
  void testTranslateMySQLSyntaxException() {
    SQLSyntaxErrorException exception = new SQLSyntaxErrorException("Unknown column 'xmin' in 'field list'");
    String external_message = exceptionHandler.getExternalMessage(exception);
    assertEquals("A column needed by MySQL source connector is missing in the database", external_message);
  }

  @Test
  void testTranslateEOFException() {
    EOFException exception =
        new EOFException("Can not read response from server. Expected to read 4 bytes, read 0 bytes before connection was unexpectedly lost.");
    String external_message = exceptionHandler.getExternalMessage(exception);
    assertEquals("Can not read data from MySQL server", external_message);
  }

}
