/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata;

import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.jdbc.JdbcSqlOperations;
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
  public void insertRecordsInternal(JdbcDatabase database,
                                    List<AirbyteRecordMessage> records,
                                    String schemaName,
                                    String tableName)
      throws SQLException {
    if (records.isEmpty()) {
      return;
    }
    final String insertQueryComponent = String.format("INSERT INTO %s.%s (%s, %s, %s) VALUES (?, ?, ?)", schemaName, tableName,
        JavaBaseConstants.COLUMN_NAME_AB_ID,
        JavaBaseConstants.COLUMN_NAME_DATA,
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
    database.execute(con -> {
      try {

        PreparedStatement pstmt = con.prepareStatement(insertQueryComponent);

        for (final AirbyteRecordMessage record : records) {

          final String uuid = UUID.randomUUID().toString();
          final String jsonData = Jsons.serialize(formatData(record.getData()));
          final Timestamp emittedAt = Timestamp.from(Instant.ofEpochMilli(record.getEmittedAt()));
          LOGGER.info("uuid: " + uuid);
          LOGGER.info("jsonData: " + jsonData);
          LOGGER.info("emittedAt: " + emittedAt);
          pstmt.setString(1, uuid);
          pstmt.setString(2, jsonData);
          pstmt.setTimestamp(3, emittedAt);
          pstmt.addBatch();

        }

        pstmt.executeBatch();

      } catch (final SQLException se) {
        for (SQLException ex = se; ex != null; ex = ex.getNextException()) {
          LOGGER.info(ex.getMessage());
        }
        AirbyteTraceMessageUtility.emitSystemErrorTrace(se,
            "Connector failed while inserting records to staging table");
        throw new RuntimeException(se);
      } catch (Exception e) {
        AirbyteTraceMessageUtility.emitSystemErrorTrace(e,
            "Connector failed while inserting records to staging table");
        throw new RuntimeException(e);
      }

    });
  }

  @Override
  public void createSchemaIfNotExists(final JdbcDatabase database, final String schemaName) throws Exception {
    try {
      database.execute(String.format("CREATE DATABASE \"%s\" AS PERMANENT = 120e6, SPOOL = 120e6;", schemaName));
    } catch (SQLException e) {
      if (e.getMessage().contains("already exists")) {
        LOGGER.warn("Database " + schemaName + " already exists.");
      } else {
        AirbyteTraceMessageUtility.emitSystemErrorTrace(e, "Connector failed while creating schema ");
        throw new RuntimeException(e);
      }
    }

  }

  @Override
  public void createTableIfNotExists(final JdbcDatabase database, final String schemaName, final String tableName)
      throws SQLException {
    try {
      database.execute(createTableQuery(database, schemaName, tableName));
    } catch (SQLException e) {
      if (e.getMessage().contains("already exists")) {
        LOGGER.warn("Table " + schemaName + "." + tableName + " already exists.");
      } else {
        AirbyteTraceMessageUtility.emitSystemErrorTrace(e, "Connector failed while creating table ");
        throw new RuntimeException(e);
      }
    }
  }

  @Override
  public String createTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    return String.format(
        "CREATE SET TABLE %s.%s, FALLBACK ( \n" + "%s VARCHAR(256), \n" + "%s JSON, \n" + "%s TIMESTAMP(6) \n"
            + ");\n",
        schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_DATA,
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
  }

  @Override
  public void dropTableIfExists(final JdbcDatabase database, final String schemaName, final String tableName)
      throws SQLException {
    try {
      database.execute(dropTableIfExistsQuery(schemaName, tableName));
    } catch (SQLException e) {
      AirbyteTraceMessageUtility.emitSystemErrorTrace(e,
          "Connector failed while dropping table " + schemaName + "." + tableName);
    }
  }

  @Override
  public String truncateTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    try {
      return String.format("DELETE %s.%s ALL;\n", schemaName, tableName);
    } catch (Exception e) {
      AirbyteTraceMessageUtility.emitSystemErrorTrace(e,
          "Connector failed while truncating table " + schemaName + "." + tableName);
    }
    return "";
  }

  private String dropTableIfExistsQuery(final String schemaName, final String tableName) {
    try {
      return String.format("DROP TABLE  %s.%s;\n", schemaName, tableName);
    } catch (Exception e) {
      AirbyteTraceMessageUtility.emitSystemErrorTrace(e,
          "Connector failed while dropping table " + schemaName + "." + tableName);
    }
    return "";
  }

  @Override
  public void executeTransaction(final JdbcDatabase database, final List<String> queries) throws Exception {
    final StringBuilder appendedQueries = new StringBuilder();
    try {
      for (final String query : queries) {
        appendedQueries.append(query);
      }
      database.execute(appendedQueries.toString());
    } catch (SQLException e) {
      AirbyteTraceMessageUtility.emitSystemErrorTrace(e,
          "Connector failed while executing queries : " + appendedQueries.toString());
    }
  }

}
