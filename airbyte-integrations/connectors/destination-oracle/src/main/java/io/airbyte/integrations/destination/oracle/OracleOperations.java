/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.oracle;

import static io.airbyte.cdk.integrations.base.JavaBaseConstantsKt.upperQuoted;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage;
import io.airbyte.cdk.integrations.destination.jdbc.SqlOperations;
import java.sql.PreparedStatement;
import java.sql.Timestamp;
import java.sql.Types;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OracleOperations implements SqlOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(OracleOperations.class);
  private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

  private final String tablespace;

  public OracleOperations(final String tablespace) {
    this.tablespace = tablespace;
  }

  @Override
  public void createSchemaIfNotExists(final JdbcDatabase database, final String schemaName) throws Exception {
    if (database.queryInt("select count(*) from all_users where upper(username) = upper(?)", schemaName) == 0) {
      LOGGER.warn("Schema " + schemaName + " is not found! Trying to create a new one.");
      final String query = String.format("create user %s identified by %s quota unlimited on %s",
          schemaName, schemaName, tablespace);
      // need to grant privileges to new user / this option is not mandatory for Oracle DB 18c or higher
      final String privileges = String.format("GRANT ALL PRIVILEGES TO %s", schemaName);
      database.execute(query);
      database.execute(privileges);
    }
  }

  @Override
  public void createTableIfNotExists(final JdbcDatabase database, final String schemaName, final String tableName) throws Exception {
    try {
      if (!tableExists(database, schemaName, tableName)) {
        database.execute(createTableQuery(database, schemaName, tableName));
      }
    } catch (final Exception e) {
      LOGGER.error("Error while creating table.", e);
      throw e;
    }
  }

  @Override
  public String createTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    return String.format(
        """
          CREATE TABLE %s.%s (
          %s VARCHAR(64) PRIMARY KEY,
          %s JSON,
          %s TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
          %s TIMESTAMP WITH TIME ZONE DEFAULT NULL,
          %s JSON
          )
        """,
        schemaName, tableName,
        upperQuoted(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID),
        upperQuoted(JavaBaseConstants.COLUMN_NAME_DATA),
        upperQuoted(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT),
        upperQuoted(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT),
        upperQuoted(JavaBaseConstants.COLUMN_NAME_AB_META));
  }

  private boolean tableExists(final JdbcDatabase database, final String schemaName, final String tableName) throws Exception {
    final int count = database.queryInt("select count(*) \n from all_tables\n where upper(owner) = upper(?) and upper(table_name) = upper(?)",
        schemaName, tableName);
    return count == 1;
  }

  @Override
  public void dropTableIfExists(final JdbcDatabase database, final String schemaName, final String tableName) throws Exception {
    if (tableExists(database, schemaName, tableName)) {
      try {
        final String query = String.format("DROP TABLE %s.%s", schemaName, tableName);
        database.execute(query);
      } catch (final Exception e) {
        LOGGER.error(String.format("Error dropping table %s.%s", schemaName, tableName), e);
        throw e;
      }
    }
  }

  @Override
  public String truncateTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    return String.format("DELETE FROM %s.%s\n", schemaName, tableName);
  }

  // Adapted from SqlUtils.insertRawRecordsInSingleQuery to meet some needs specific to Oracle syntax
  private static void insertRawRecordsInSingleQuery(final String tableName,
                                                    final String columns,
                                                    final JdbcDatabase jdbcDatabase,
                                                    final List<PartialAirbyteMessage> records,
                                                    final Supplier<UUID> uuidSupplier)
      throws Exception {
    if (records.isEmpty()) {
      return;
    }

    jdbcDatabase.execute(connection -> {

      // Strategy: We want to use PreparedStatement because it handles binding values to the SQL query
      // (e.g. handling formatting timestamps). A PreparedStatement statement is created by supplying the
      // full SQL string at creation time. Then subsequently specifying which values are bound to the
      // string. Thus there will be two loops below.
      // 1) Loop over records to build the full string.
      // 2) Loop over the records and bind the appropriate values to the string.
      //
      // The "SELECT 1 FROM DUAL" at the end is a formality to satisfy the needs of the Oracle syntax.
      // (see https://stackoverflow.com/a/93724 for details)
      final StringBuilder sql = new StringBuilder("INSERT ALL ");
      records.forEach(r -> sql.append(String.format("INTO %s %s VALUES %s", tableName, columns, "(?, ?, ?, ?, ?)\n")));
      sql.append(" SELECT 1 FROM DUAL");
      final String query = sql.toString();

      try (final PreparedStatement statement = connection.prepareStatement(query)) {
        // second loop: bind values to the SQL string.
        // 1-indexed
        int i = 1;
        for (final PartialAirbyteMessage message : records) {
          final Optional<String> jsonData = Optional.ofNullable(message).map(PartialAirbyteMessage::getSerialized);
          if (jsonData.isPresent()) {
            // This is inefficient and brings me shame but it works
            final String formattedData = OBJECT_MAPPER.writeValueAsString(
                StandardNameTransformer.formatJsonPath(OBJECT_MAPPER.readTree(jsonData.get())));
            statement.setString(i++, uuidSupplier.get().toString());
            statement.setString(i++, formattedData);
            statement.setTimestamp(i++, Timestamp.from(Instant.ofEpochMilli(message.getRecord().getEmittedAt())));
            statement.setNull(i++, Types.TIMESTAMP);
            statement.setString(i++, OBJECT_MAPPER.writeValueAsString(message.getRecord().getMeta()));
          } else {
            LOGGER.warn("Record data is empty, skipping record: {}", message);
          }

        }

        statement.execute();
      } catch (JsonProcessingException e) {
        throw new RuntimeException(e);
      }
    });
  }

  @Override
  public String insertTableQuery(final JdbcDatabase database,
                                 final String schemaName,
                                 final String sourceTableName,
                                 final String destinationTableName) {
    return String.format("INSERT INTO %s.%s SELECT * FROM %s.%s\n", schemaName, destinationTableName, schemaName, sourceTableName);
  }

  @Override
  public void executeTransaction(final JdbcDatabase database, final List<String> queries) throws Exception {
    if (queries.isEmpty()) {
      return;
    }
    final String SQL = "BEGIN\n COMMIT;\n" + String.join(";\n", queries) + "; \nCOMMIT; \nEND;";
    database.execute(SQL);
  }

  @Override
  public boolean isValidData(final JsonNode data) {
    return true;
  }

  @Override
  public boolean isSchemaRequired() {
    return true;
  }

  @Override
  public boolean isSchemaExists(@Nullable final JdbcDatabase database, @Nullable final String schemaName) throws Exception {
    return SqlOperations.super.isSchemaExists(database, schemaName);
  }

  @Override
  public void insertRecords(@NotNull final JdbcDatabase database,
                            @NotNull final List<PartialAirbyteMessage> records,
                            @Nullable final String schemaName,
                            @Nullable final String tableName)
      throws Exception {
    final String formattedTableName = String.format("%s.%s", schemaName, tableName);
    final String columns = String.format("(%s, %s, %s, %s, %s)",
        upperQuoted(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID),
        upperQuoted(JavaBaseConstants.COLUMN_NAME_DATA),
        upperQuoted(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT),
        upperQuoted(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT),
        upperQuoted(JavaBaseConstants.COLUMN_NAME_AB_META));
    insertRawRecordsInSingleQuery(formattedTableName, columns, database, records, UUID::randomUUID);
  }

}
