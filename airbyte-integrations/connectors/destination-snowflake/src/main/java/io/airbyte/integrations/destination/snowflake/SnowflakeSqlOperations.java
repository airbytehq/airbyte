/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.SqlOperationsUtils;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.sql.SQLException;
import java.util.List;
import java.util.StringJoiner;
import java.util.stream.Stream;
import net.snowflake.client.jdbc.SnowflakeSQLException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class SnowflakeSqlOperations extends JdbcSqlOperations implements SqlOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeSqlOperations.class);
  private static final int MAX_FILES_IN_LOADING_QUERY_LIMIT = 1000;
  protected static final String ALREADY_EXISTS_EXCEPTION_MSG = "already exists";

  @Override
  public void createTableIfNotExists(final JdbcDatabase database, final String schemaName, final String tableName) throws SQLException {
    try {
      database.execute(createTableQuery(database, schemaName, tableName));
    } catch (SnowflakeSQLException ex){
      if (ex.getMessage().contains(ALREADY_EXISTS_EXCEPTION_MSG)) {
        throw new ConfigErrorException(ex.getMessage(), ex);
      } else {
        throw ex;
      }
    }
  }

  @Override
  public String createTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    return String.format(
        "CREATE TABLE IF NOT EXISTS %s.%s ( \n"
            + "%s VARCHAR PRIMARY KEY,\n"
            + "%s VARIANT,\n"
            + "%s TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp()\n"
            + ") data_retention_time_in_days = 0;",
        schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_DATA, JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
  }

  @Override
  public boolean isSchemaExists(final JdbcDatabase database, final String outputSchema) throws Exception {
    try (final Stream<JsonNode> results = database.unsafeQuery(SHOW_SCHEMAS)) {
      return results.map(schemas -> schemas.get(NAME).asText()).anyMatch(outputSchema::equalsIgnoreCase);
    }
  }

  @Override
  public void insertRecordsInternal(final JdbcDatabase database,
                                    final List<AirbyteRecordMessage> records,
                                    final String schemaName,
                                    final String tableName)
      throws SQLException {
    LOGGER.info("actual size of batch: {}", records.size());

    // snowflake query syntax:
    // requires selecting from a set of values in order to invoke the parse_json function.
    // INSERT INTO public.users (ab_id, data, emitted_at) SELECT column1, parse_json(column2), column3
    // FROM VALUES
    // (?, ?, ?),
    // ...
    final String insertQuery = String.format(
        "INSERT INTO %s.%s (%s, %s, %s) SELECT column1, parse_json(column2), column3 FROM VALUES\n",
        schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_DATA, JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
    final String recordQuery = "(?, ?, ?),\n";
    SqlOperationsUtils.insertRawRecordsInSingleQuery(insertQuery, recordQuery, database, records);
  }

  protected String generateFilesList(final List<String> files) {
    if (0 < files.size() && files.size() < MAX_FILES_IN_LOADING_QUERY_LIMIT) {
      // see https://docs.snowflake.com/en/user-guide/data-load-considerations-load.html#lists-of-files
      final StringJoiner joiner = new StringJoiner(",");
      files.forEach(filename -> joiner.add("'" + filename.substring(filename.lastIndexOf("/") + 1) + "'"));
      return " files = (" + joiner + ")";
    } else {
      return "";
    }
  }

}
