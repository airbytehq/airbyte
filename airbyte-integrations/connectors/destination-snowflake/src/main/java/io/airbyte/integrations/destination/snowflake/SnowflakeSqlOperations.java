/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.TypingAndDedupingFlag;
import io.airbyte.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.SqlOperationsUtils;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.sql.SQLException;
import java.util.List;
import java.util.Optional;
import java.util.StringJoiner;
import java.util.stream.Stream;
import net.snowflake.client.jdbc.SnowflakeSQLException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class SnowflakeSqlOperations extends JdbcSqlOperations implements SqlOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeSqlOperations.class);
  private static final int MAX_FILES_IN_LOADING_QUERY_LIMIT = 1000;

  // This is an unfortunately fragile way to capture this, but Snowflake doesn't
  // provide a more specific permission exception error code
  private static final String NO_PRIVILEGES_ERROR_MESSAGE = "but current role has no privileges on it";
  private static final String IP_NOT_IN_WHITE_LIST_ERR_MSG = "not allowed to access Snowflake";

  private final boolean use1s1t;

  public SnowflakeSqlOperations() {
    this.use1s1t = TypingAndDedupingFlag.isDestinationV2();
  }

  @Override
  public String createTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    if (use1s1t) {
      return String.format(
          """
              CREATE TABLE IF NOT EXISTS %s.%s (
                "%s" VARCHAR PRIMARY KEY,
                "%s" TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp(),
                "%s" TIMESTAMP WITH TIME ZONE DEFAULT NULL,
                "%s" VARIANT
              ) data_retention_time_in_days = 0;""",
          schemaName,
          tableName,
          JavaBaseConstants.COLUMN_NAME_AB_RAW_ID,
          JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT,
          JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT,
          JavaBaseConstants.COLUMN_NAME_DATA);
    } else {
      return String.format(
          """
              CREATE TABLE IF NOT EXISTS %s.%s (
                %s VARCHAR PRIMARY KEY,
                %s VARIANT,
                %s TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp()
              ) data_retention_time_in_days = 0;""",
          schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_DATA, JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
    }
  }

  @Override
  public boolean isSchemaExists(final JdbcDatabase database, final String outputSchema) throws Exception {
    try (final Stream<JsonNode> results = database.unsafeQuery(SHOW_SCHEMAS)) {
      return results.map(schemas -> schemas.get(NAME).asText()).anyMatch(outputSchema::equalsIgnoreCase);
    } catch (Exception e) {
      throw checkForKnownConfigExceptions(e).orElseThrow(() -> e);
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
    final String insertQuery;
    if (use1s1t) {
      // Note that the column order is weird here - that's intentional, to avoid needing to change
      // SqlOperationsUtils.insertRawRecordsInSingleQuery to support a different column order.
      insertQuery = String.format(
          "INSERT INTO %s.%s (%s, %s, %s) SELECT column1, parse_json(column2), column3 FROM VALUES\n",
          schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_RAW_ID, JavaBaseConstants.COLUMN_NAME_DATA, JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT);
    } else {
      insertQuery = String.format(
          "INSERT INTO %s.%s (%s, %s, %s) SELECT column1, parse_json(column2), column3 FROM VALUES\n",
          schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_DATA, JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
    }
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

  @Override
  protected Optional<ConfigErrorException> checkForKnownConfigExceptions(Exception e) {
    if (e instanceof SnowflakeSQLException && e.getMessage().contains(NO_PRIVILEGES_ERROR_MESSAGE)) {
      return Optional.of(new ConfigErrorException(
          "Encountered Error with Snowflake Configuration: Current role does not have permissions on the target schema please verify your privileges",
          e));
    }
    if (e instanceof SnowflakeSQLException && e.getMessage().contains(IP_NOT_IN_WHITE_LIST_ERR_MSG)) {
      return Optional.of(new ConfigErrorException(
          """
              Snowflake has blocked access from Airbyte IP address. Please make sure that your Snowflake user account's
               network policy allows access from all Airbyte IP addresses. See this page for the list of Airbyte IPs:
               https://docs.airbyte.com/cloud/getting-started-with-airbyte-cloud#allowlist-ip-addresses and this page
               for documentation on Snowflake network policies: https://docs.snowflake.com/en/user-guide/network-policies
          """,
          e));
    }
    return Optional.empty();
  }

}
