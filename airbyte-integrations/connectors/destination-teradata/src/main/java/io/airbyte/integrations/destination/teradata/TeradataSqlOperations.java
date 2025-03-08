/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata;

import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.teradata.util.JSONStruct;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TeradataSqlOperations extends JdbcSqlOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(TeradataSqlOperations.class);

  @Override
  public void insertRecordsInternal(final JdbcDatabase database,
                                    final List<AirbyteRecordMessage> records,
                                    final String schemaName,
                                    final String tableName)
      throws SQLException {
    if (records.isEmpty()) {
      return;
    }
    final String insertQueryComponent = String.format("INSERT INTO %s.%s (%s, %s, %s) VALUES (?, ?, ?)", schemaName, tableName,
        JavaBaseConstants.COLUMN_NAME_AB_ID,
        JavaBaseConstants.COLUMN_NAME_DATA,
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
    database.execute(con -> {
      final PreparedStatement pstmt = con.prepareStatement(insertQueryComponent);
      for (final AirbyteRecordMessage record : records) {
        final String uuid = UUID.randomUUID().toString();
        final String jsonData = Jsons.serialize(formatData(record.getData()));
        final Timestamp emittedAt = Timestamp.from(Instant.ofEpochMilli(record.getEmittedAt()));
        pstmt.setString(1, uuid);
        pstmt.setObject(2, new JSONStruct("JSON", new Object[] {jsonData}));
        pstmt.setTimestamp(3, emittedAt);
        pstmt.addBatch();
      }
      pstmt.executeBatch();
    });
  }

  @Override
  public void createSchemaIfNotExists(final JdbcDatabase database, final String schemaName) throws Exception {
    try {
      database.execute(String.format("CREATE DATABASE \"%s\" AS PERMANENT = 120e6, SPOOL = 120e6;", schemaName));
    } catch (final SQLException e) {
      if (e.getMessage().contains("already exists")) {
        LOGGER.warn("Database " + schemaName + " already exists.");
      } else {
        throw new RuntimeException(e);
      }
    }

  }

  @Override
  public void createTableIfNotExists(final JdbcDatabase database, final String schemaName, final String tableName)
      throws SQLException {
    try {
      database.execute(createTableQuery(database, schemaName, tableName));
    } catch (final SQLException e) {
      if (e.getMessage().contains("already exists")) {
        LOGGER.warn("Table " + schemaName + "." + tableName + " already exists.");
      } else {
        throw new RuntimeException(e);
      }
    }
  }

  @Override
  public String createTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    return String.format(
        "CREATE SET TABLE %s.%s, FALLBACK ( %s VARCHAR(256), %s JSON, %s TIMESTAMP(6)) " +
            " UNIQUE PRIMARY INDEX (%s) ",
        schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_DATA,
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT, JavaBaseConstants.COLUMN_NAME_AB_ID);
  }

  @Override
  public void dropTableIfExists(final JdbcDatabase database, final String schemaName, final String tableName)
      throws SQLException {
    database.execute(dropTableIfExistsQueryInternal(schemaName, tableName));
  }

  @Override
  public String truncateTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    return String.format("DELETE %s.%s ALL;\n", schemaName, tableName);
  }

  private String dropTableIfExistsQueryInternal(final String schemaName, final String tableName) {
    return String.format("DROP TABLE %s.%s;\n", schemaName, tableName);
  }

  @Override
  public void executeTransaction(final JdbcDatabase database, final List<String> queries) throws Exception {
    final StringBuilder appendedQueries = new StringBuilder();
    for (final String query : queries) {
      appendedQueries.append(query);
    }
    database.execute(appendedQueries.toString());
  }

}
