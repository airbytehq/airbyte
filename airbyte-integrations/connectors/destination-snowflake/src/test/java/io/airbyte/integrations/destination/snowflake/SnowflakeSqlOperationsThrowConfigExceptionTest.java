/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;

import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.DestinationConfig;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import java.sql.SQLException;
import java.util.List;
import java.util.stream.Stream;
import net.snowflake.client.jdbc.SnowflakeSQLException;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.mockito.Mockito;

/**
 * This class contains tests to make sure we catch some Snowflake's exceptions and convert them to
 * Airbyte Config Exception (Ex. User has no required permission, User's IP is not in Whitelist,
 * etc)
 */
class SnowflakeSqlOperationsThrowConfigExceptionTest {

  private static final String SCHEMA_NAME = "dummySchemaName";
  private static final String STAGE_NAME = "dummyStageName";
  private static final String TABLE_NAME = "dummyTableName";
  private static final String STAGE_PATH = "stagePath/2022/";
  private static final List<String> FILE_PATH = List.of("filepath/filename");

  private static final String TEST_NO_CONFIG_EXCEPTION_CATCHED = "TEST";
  private static final String TEST_PERMISSION_EXCEPTION_CATCHED = "but current role has no privileges on it";
  private static final String TEST_IP_NOT_IN_WHITE_LIST_EXCEPTION_CATCHED = "not allowed to access Snowflake";

  private static SnowflakeInternalStagingSqlOperations snowflakeStagingSqlOperations;

  private static SnowflakeSqlOperations snowflakeSqlOperations;

  private static final JdbcDatabase dbForExecuteQuery = Mockito.mock(JdbcDatabase.class);
  private static final JdbcDatabase dbForRunUnsafeQuery = Mockito.mock(JdbcDatabase.class);

  private static Executable createStageIfNotExists;
  private static Executable dropStageIfExists;
  private static Executable copyIntoTableFromStage;

  private static Executable createSchemaIfNotExists;
  private static Executable isSchemaExists;
  private static Executable createTableIfNotExists;
  private static Executable dropTableIfExists;

  @BeforeAll
  public static void setup() {
    DestinationConfig.initialize(Jsons.emptyObject());

    snowflakeStagingSqlOperations = new SnowflakeInternalStagingSqlOperations(new SnowflakeSQLNameTransformer());
    snowflakeSqlOperations = new SnowflakeSqlOperations();

    createStageIfNotExists = () -> snowflakeStagingSqlOperations.createStageIfNotExists(dbForExecuteQuery, STAGE_NAME);
    dropStageIfExists = () -> snowflakeStagingSqlOperations.dropStageIfExists(dbForExecuteQuery, STAGE_NAME, null);
    copyIntoTableFromStage =
        () -> snowflakeStagingSqlOperations.copyIntoTableFromStage(dbForExecuteQuery, STAGE_NAME, STAGE_PATH, FILE_PATH, TABLE_NAME, SCHEMA_NAME);

    createSchemaIfNotExists = () -> snowflakeSqlOperations.createSchemaIfNotExists(dbForExecuteQuery, SCHEMA_NAME);
    isSchemaExists = () -> snowflakeSqlOperations.isSchemaExists(dbForRunUnsafeQuery, SCHEMA_NAME);
    createTableIfNotExists = () -> snowflakeSqlOperations.createTableIfNotExists(dbForExecuteQuery, SCHEMA_NAME, TABLE_NAME);
    dropTableIfExists = () -> snowflakeSqlOperations.dropTableIfExists(dbForExecuteQuery, SCHEMA_NAME, TABLE_NAME);
  }

  private static Stream<Arguments> testArgumentsForDbExecute() {
    return Stream.of(
        Arguments.of(TEST_NO_CONFIG_EXCEPTION_CATCHED, false, createStageIfNotExists),
        Arguments.of(TEST_PERMISSION_EXCEPTION_CATCHED, true, createStageIfNotExists),
        Arguments.of(TEST_IP_NOT_IN_WHITE_LIST_EXCEPTION_CATCHED, true, createStageIfNotExists),
        Arguments.of(TEST_NO_CONFIG_EXCEPTION_CATCHED, false, dropStageIfExists),
        Arguments.of(TEST_PERMISSION_EXCEPTION_CATCHED, true, dropStageIfExists),
        Arguments.of(TEST_IP_NOT_IN_WHITE_LIST_EXCEPTION_CATCHED, true, dropStageIfExists),
        Arguments.of(TEST_NO_CONFIG_EXCEPTION_CATCHED, false, copyIntoTableFromStage),
        Arguments.of(TEST_PERMISSION_EXCEPTION_CATCHED, true, copyIntoTableFromStage),
        Arguments.of(TEST_IP_NOT_IN_WHITE_LIST_EXCEPTION_CATCHED, true, copyIntoTableFromStage),
        Arguments.of(TEST_NO_CONFIG_EXCEPTION_CATCHED, false, createSchemaIfNotExists),
        Arguments.of(TEST_PERMISSION_EXCEPTION_CATCHED, true, createSchemaIfNotExists),
        Arguments.of(TEST_IP_NOT_IN_WHITE_LIST_EXCEPTION_CATCHED, true, createSchemaIfNotExists),
        Arguments.of(TEST_NO_CONFIG_EXCEPTION_CATCHED, false, createTableIfNotExists),
        Arguments.of(TEST_PERMISSION_EXCEPTION_CATCHED, true, createTableIfNotExists),
        Arguments.of(TEST_IP_NOT_IN_WHITE_LIST_EXCEPTION_CATCHED, true, createTableIfNotExists),
        Arguments.of(TEST_NO_CONFIG_EXCEPTION_CATCHED, false, dropTableIfExists),
        Arguments.of(TEST_PERMISSION_EXCEPTION_CATCHED, true, dropTableIfExists),
        Arguments.of(TEST_IP_NOT_IN_WHITE_LIST_EXCEPTION_CATCHED, true, dropTableIfExists));
  }

  @ParameterizedTest
  @MethodSource("testArgumentsForDbExecute")
  public void testCatchNoPermissionOnExecuteException(final String message, final boolean shouldCapture, final Executable executable) {
    try {
      Mockito.doThrow(new SnowflakeSQLException(message)).when(dbForExecuteQuery).execute(Mockito.anyString());
    } catch (SQLException e) {
      // This would not be expected, but the `execute` method above will flag as an unhandled exception
      assert false;
    }
    executeTest(message, shouldCapture, executable);
  }

  private static Stream<Arguments> testArgumentsForDbUnsafeQuery() {
    return Stream.of(
        Arguments.of(TEST_NO_CONFIG_EXCEPTION_CATCHED, false, isSchemaExists),
        Arguments.of(TEST_PERMISSION_EXCEPTION_CATCHED, true, isSchemaExists),
        Arguments.of(TEST_IP_NOT_IN_WHITE_LIST_EXCEPTION_CATCHED, true, isSchemaExists));
  }

  @ParameterizedTest
  @MethodSource("testArgumentsForDbUnsafeQuery")
  public void testCatchNoPermissionOnUnsafeQueryException(final String message, final boolean shouldCapture, final Executable executable) {
    try {
      Mockito.doThrow(new SnowflakeSQLException(message)).when(dbForRunUnsafeQuery).unsafeQuery(Mockito.anyString());
    } catch (SQLException e) {
      // This would not be expected, but the `execute` method above will flag as an unhandled exception
      assert false;
    }
    executeTest(message, shouldCapture, executable);
  }

  private void executeTest(final String message, final boolean shouldCapture, final Executable executable) {
    final Exception exception = Assertions.assertThrows(Exception.class, executable);
    if (shouldCapture) {
      assertInstanceOf(ConfigErrorException.class, exception);
    } else {
      assertInstanceOf(SnowflakeSQLException.class, exception);
      assertEquals(exception.getMessage(), message);
    }
  }

}
