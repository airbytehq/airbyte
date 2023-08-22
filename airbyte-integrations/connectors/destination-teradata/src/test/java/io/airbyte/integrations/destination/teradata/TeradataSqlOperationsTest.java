/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.sql.SQLException;
import java.util.Collections;
import java.util.List;

import org.junit.jupiter.api.Test;

class TeradataSqlOperationsTest {

    public static final String SCHEMA_NAME = "schemaName";
    public static final String TABLE_NAME = "tableName";

    private final TeradataSqlOperations teradataSqlOperations = new TeradataSqlOperations();
    private JdbcDatabase db = mock(JdbcDatabase.class);

    @Test
    void testInsertRecordsSuccessValidRecords() throws Exception {
        teradataSqlOperations.insertRecords(db, List.of(new AirbyteRecordMessage()), SCHEMA_NAME, TABLE_NAME);
        verify(db, times(1)).execute(any(CheckedConsumer.class));
    }

    @Test
    void testInsertRecordsInternalSuccessValidRecords() throws SQLException {
        teradataSqlOperations.insertRecordsInternal(db, List.of(new AirbyteRecordMessage()), SCHEMA_NAME, TABLE_NAME);
        verify(db, times(1)).execute(any(CheckedConsumer.class));
    }

    @Test
    void testInsertRecordsInternalSuccessEmptyRecords() throws SQLException {
        teradataSqlOperations.insertRecordsInternal(db, Collections.emptyList(), SCHEMA_NAME, TABLE_NAME);
        verify(db, times(0)).execute(any(CheckedConsumer.class));
    }

    @Test
    void testInsertRecordsInternalFailException() throws SQLException {
        doThrow(SQLException.class).when(db).execute(any(CheckedConsumer.class));
        assertThrows(SQLException.class, () -> teradataSqlOperations.insertRecordsInternal(
                db, List.of(new AirbyteRecordMessage()), SCHEMA_NAME, TABLE_NAME));
        verify(db, times(1)).execute(any(CheckedConsumer.class));
    }

    @Test
    void testCreateSchemaIfNotExistsSuccess() throws Exception {
        teradataSqlOperations.createSchemaIfNotExists(db, SCHEMA_NAME);
        verify(db, times(1)).execute(any(String.class));
    }

    @Test
    void testCreateSchemaIfNotExistsFailSQLExceptionSchemaExists() throws Exception {
        String exceptionMessage = String.format("Database %s already exists.", SCHEMA_NAME);
        doThrow(new SQLException(exceptionMessage)).when(db).execute(any(String.class));
        teradataSqlOperations.createSchemaIfNotExists(db, SCHEMA_NAME);
        verify(db, times(1)).execute(any(String.class));
    }

    @Test
    void testCreateSchemaIfNotExistsFailSQLExceptionOtherError() throws Exception {
        String exceptionMessage = "Connector failed while creating schema";
        doThrow(new SQLException(exceptionMessage)).when(db).execute(any(String.class));
        Throwable exception = assertThrows(RuntimeException.class, () -> teradataSqlOperations.createSchemaIfNotExists(
                db, SCHEMA_NAME));
        assertTrue(exception.getMessage().contains(exceptionMessage));
        verify(db, times(1)).execute(any(String.class));
    }


    @Test
    void testCreateTableIfNotExistsSuccess() throws SQLException {
        teradataSqlOperations.createTableIfNotExists(db, SCHEMA_NAME, TABLE_NAME);
        verify(db, times(1)).execute(any(String.class));
    }

    @Test
    void testCreateTableIfNotExistsFailSQLExceptionTableExists() throws SQLException {
        String exceptionMessage = String.format("Table %s.%s already exists.", SCHEMA_NAME, TABLE_NAME);
        doThrow(new SQLException(exceptionMessage)).when(db).execute(any(String.class));
        teradataSqlOperations.createTableIfNotExists(db, SCHEMA_NAME, TABLE_NAME);
        verify(db, times(1)).execute(any(String.class));
    }

    @Test
    void testCreateTableIfNotExistsFailSQLExceptionOtherError() throws SQLException {
        String exceptionMessage = "Connector failed while creating table";
        doThrow(new SQLException(exceptionMessage)).when(db).execute(any(String.class));
        Throwable exception = assertThrows(RuntimeException.class, () -> teradataSqlOperations.createTableIfNotExists(
                db, SCHEMA_NAME, TABLE_NAME));
        assertTrue(exception.getMessage().contains(exceptionMessage));
        verify(db, times(1)).execute(any(String.class));
    }

    @Test
    void testCreateTableQuery() {
        String expectedQueryMessage = String.format("CREATE SET TABLE %s.%s", SCHEMA_NAME, TABLE_NAME);
        String actualQueryMessage = teradataSqlOperations.createTableQuery(db, SCHEMA_NAME, TABLE_NAME);
        assertTrue(actualQueryMessage.startsWith(expectedQueryMessage));
    }

    @Test
    void testDropTableIfExistsSuccess() throws SQLException {
        teradataSqlOperations.dropTableIfExists(db, SCHEMA_NAME, TABLE_NAME);
        verify(db, times(1)).execute(any(String.class));
    }

    @Test
    void testDropTableIfExistsFailSQLException() throws SQLException {
        doThrow(SQLException.class).when(db).execute(any(String.class));
        teradataSqlOperations.dropTableIfExists(db, SCHEMA_NAME, TABLE_NAME);
        verify(db, times(1)).execute(any(String.class));
    }

    @Test
    void testTruncateTableQuery() {
        String expectedQueryMessage = String.format("DELETE %s.%s ALL", SCHEMA_NAME, TABLE_NAME);
        String actualQueryMessage = teradataSqlOperations.truncateTableQuery(db, SCHEMA_NAME, TABLE_NAME);
        assertTrue(actualQueryMessage.startsWith(expectedQueryMessage));
    }

    @Test
    void testExecuteTransactionSuccess() throws Exception {
        teradataSqlOperations.executeTransaction(db, List.of("Dummy SQL Query"));
        verify(db, times(1)).execute(any(String.class));
    }

    @Test
    void testExecuteTransactionFailSQLException() throws Exception {
        doThrow(SQLException.class).when(db).execute(any(String.class));
        teradataSqlOperations.executeTransaction(db, List.of("Dummy SQL Query"));
        verify(db, times(1)).execute(any(String.class));
    }
}

