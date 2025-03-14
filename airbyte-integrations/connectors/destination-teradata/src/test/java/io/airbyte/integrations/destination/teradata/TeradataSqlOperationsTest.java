/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;
import static org.mockito.Mockito.times;

import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.*;

public class TeradataSqlOperationsTest {

  @Mock
  private JdbcDatabase database;

  @InjectMocks
  private TeradataSqlOperations teradataSqlOperations;

  @Mock
  Connection mockConnection;

  @Mock
  PreparedStatement mockPreparedStatement;

  @Captor
  private ArgumentCaptor<String> stringCaptor;

  @BeforeEach
  void setUp() throws SQLException {
    MockitoAnnotations.openMocks(this);
  }

  @Test
  void testInsertRecordsInternal() throws SQLException {
    // Arrange
    AirbyteRecordMessage record1 = mock(AirbyteRecordMessage.class);
    when(record1.getEmittedAt()).thenReturn(System.currentTimeMillis());

    List<AirbyteRecordMessage> records = List.of(record1);
    String schemaName = "test_schema";
    String tableName = "test_table";
    teradataSqlOperations.insertRecordsInternal(database, records, schemaName, tableName);
  }

  @Test
  void testCreateSchemaIfNotExists() throws Exception {
    // Test case where schema does not exist
    doNothing().when(database).execute(anyString());

    teradataSqlOperations.createSchemaIfNotExists(database, "schema");

    verify(database, times(1)).execute(stringCaptor.capture());
    assertTrue(stringCaptor.getValue().contains("CREATE DATABASE \"schema\""));

    // Test case where schema already exists
    doThrow(new SQLException("Database already exists")).when(database).execute(anyString());
    teradataSqlOperations.createSchemaIfNotExists(database, "schema");

    verify(database, times(2)).execute(stringCaptor.capture());
    assertTrue(stringCaptor.getValue().contains("CREATE DATABASE \"schema\""));
  }

  @Test
  void testCreateTableIfNotExists() throws SQLException {
    // Test case where table does not exist
    doNothing().when(database).execute(anyString());

    teradataSqlOperations.createTableIfNotExists(database, "schema", "table");

    verify(database, times(1)).execute(stringCaptor.capture());
    assertTrue(stringCaptor.getValue().contains("CREATE SET TABLE schema.table"));

    // Test case where table already exists
    doThrow(new SQLException("Table already exists")).when(database).execute(anyString());

    teradataSqlOperations.createTableIfNotExists(database, "schema", "table");

    verify(database, times(2)).execute(stringCaptor.capture());
    assertTrue(stringCaptor.getValue().contains("CREATE SET TABLE schema.table"));
  }

  @Test
  void testCreateTableQuery() {
    String query = teradataSqlOperations.createTableQuery(database, "schema", "table");
    assertEquals(
        "CREATE SET TABLE schema.table, FALLBACK ( _airbyte_ab_id VARCHAR(256), _airbyte_data JSON, _airbyte_emitted_at TIMESTAMP(6))  UNIQUE PRIMARY INDEX (_airbyte_ab_id) ",
        query);
  }

  @Test
  void testDropTableIfExists() throws SQLException {
    doNothing().when(database).execute(anyString());

    teradataSqlOperations.dropTableIfExists(database, "schema", "table");

    verify(database, times(1)).execute(stringCaptor.capture());
    assertTrue(stringCaptor.getValue().contains("DROP TABLE schema.table"));
  }

  @Test
  void testTruncateTableQuery() {
    String query = teradataSqlOperations.truncateTableQuery(database, "schema", "table");
    assertEquals("DELETE schema.table ALL;\n", query);
  }

  @Test
  void testExecuteTransaction() throws Exception {
    List<String> queries = List.of("query1;", "query2;");

    // Test case where transaction executes successfully
    doNothing().when(database).execute(anyString());

    teradataSqlOperations.executeTransaction(database, queries);

    verify(database, times(1)).execute(stringCaptor.capture());
    assertEquals("query1;query2;", stringCaptor.getValue());

    // Test case where transaction fails
    doThrow(new SQLException("Execution failed")).when(database).execute(anyString());

  }

}
