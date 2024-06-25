/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.oceanbase;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.Lists;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage;
import io.airbyte.cdk.integrations.destination.jdbc.JdbcSqlOperations;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.SQLException;
import java.sql.Timestamp;
import java.sql.Types;
import java.time.Instant;
import java.util.List;
import java.util.Objects;
import java.util.UUID;

public class OceanBaseSqlOperations extends JdbcSqlOperations {

  private static final Logger LOG = LoggerFactory.getLogger(OceanBaseSqlOperations.class);
  private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

  @Override
  public void executeTransaction(final JdbcDatabase database, final List<String> queries) throws Exception {
    database.executeWithinTransaction(queries);
  }

  @Override
  public void insertRecordsInternal(final JdbcDatabase database,
                                    final List<PartialAirbyteMessage> records,
                                    final String schemaName,
                                    final String tmpTableName) {
    throw new UnsupportedOperationException("OceanBase requires V2");
  }

  @Override
  protected void insertRecordsInternalV2(final JdbcDatabase database,
                                         final List<PartialAirbyteMessage> records,
                                         final String schemaName,
                                         final String tableName)
          throws Exception {
    if (records.isEmpty()) {
      return;
    }
    final int MAX_BATCH_SIZE = 400;
    final String insertQueryComponent = String.format(
            "INSERT INTO %s.%s (%s, %s, %s, %s, %s) VALUES\n",
            schemaName,
            tableName,
            JavaBaseConstants.COLUMN_NAME_AB_RAW_ID,
            JavaBaseConstants.COLUMN_NAME_DATA,
            JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT,
            JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT,
            JavaBaseConstants.COLUMN_NAME_AB_META);
    final String recordQueryComponent = "(?, ?, ?, ?, ?),\n";
    final List<List<PartialAirbyteMessage>> batches = Lists.partition(records, MAX_BATCH_SIZE);
    for (List<PartialAirbyteMessage> batch : batches) {
      if (batch.isEmpty()) {
        continue;
      }
      database.execute(connection -> {
        final StringBuilder sqlStatement = new StringBuilder(insertQueryComponent);
        for (PartialAirbyteMessage ignored : batch) {
          sqlStatement.append(recordQueryComponent);
        }
        final var sql = sqlStatement.substring(0, sqlStatement.length() - 2) + ";";
        try (final var statement = connection.prepareStatement(sql)) {
          int i = 1;
          for (PartialAirbyteMessage record : batch) {
            final var id = UUID.randomUUID().toString();
            statement.setString(i++, id);
            statement.setString(i++, record.getSerialized());
            statement.setTimestamp(i++, Timestamp.from(Instant.ofEpochMilli(Objects.requireNonNull(record.getRecord()).getEmittedAt())));
            statement.setNull(i++, Types.TIMESTAMP);
            String metadata;
            if (record.getRecord().getMeta() != null) {
              try {
                metadata = OBJECT_MAPPER.writeValueAsString(record.getRecord().getMeta());
              } catch (Exception e) {
                LOG.error("Failed to serialize record metadata for record {}", id, e);
                metadata = null;
              }
            } else {
              metadata = null;
            }
            statement.setString(i++, metadata);
          }
          statement.execute();
        }
      });
    }
  }

  @Override
  public boolean isSchemaRequired() {
    return true;
  }

  @Override
  protected @NotNull String createTableQueryV2(String schemaName, String tableName) {
    return String.format(
            """
            CREATE TABLE IF NOT EXISTS %s.%s (\s
            %s VARCHAR(256) PRIMARY KEY,
            %s JSON,
            %s TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP(6),
            %s TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP(6),
            %s JSON
            );
            """,
            schemaName,
            tableName,
            JavaBaseConstants.COLUMN_NAME_AB_RAW_ID,
            JavaBaseConstants.COLUMN_NAME_DATA,
            JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT,
            JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT,
            JavaBaseConstants.COLUMN_NAME_AB_META);
  }

  // Will be used to determine whether load data local infile is supported
  private double getVersion(final JdbcDatabase database) throws SQLException {
    final List<String> versions = database.queryStrings(
            connection -> connection.createStatement().executeQuery("select version()"),
            resultSet -> resultSet.getString("version()"));
    return Double.parseDouble(versions.getFirst().substring(0, 3));
  }

  @Override
  public void createTableIfNotExists(
          JdbcDatabase database,
          String schemaName,
          String tableName)
          throws SQLException {
    super.createTableIfNotExists(database, schemaName, tableName);

    database.execute(createTableQuery(database, schemaName, tableName));
  }

  @Override
  public String insertTableQuery(final JdbcDatabase database,
                                 final String schemaName,
                                 final String sourceTableName,
                                 final String destinationTableName) {
    return String.format("INSERT INTO %s.%s SELECT * FROM %s.%s;\n", database, destinationTableName, database, sourceTableName);
  }

  @Override
  public void createSchemaIfNotExists(@Nullable JdbcDatabase database, @Nullable String schemaName) throws Exception {
      assert database != null;
      database.execute(String.format("CREATE SCHEMA IF NOT EXISTS %s;", schemaName));
  }
}
