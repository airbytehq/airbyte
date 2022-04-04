/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import static io.airbyte.db.jdbc.JdbcUtils.getDefaultSourceOperations;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.SqlOperationsUtils;
import io.airbyte.integrations.destination.redshift.enums.RedshiftDataTmpTableMode;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.nio.charset.StandardCharsets;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedshiftSqlOperations extends JdbcSqlOperations implements SqlOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftSqlOperations.class);
  protected static final int REDSHIFT_VARCHAR_MAX_BYTE_SIZE = 65535;

  private final RedshiftDataTmpTableMode redshiftDataTmpTableMode;
  private static final List<String> tablesWithNotSuperType = new ArrayList<>();

  public RedshiftSqlOperations(final RedshiftDataTmpTableMode redshiftDataTmpTableMode) {
    this.redshiftDataTmpTableMode = redshiftDataTmpTableMode;
  }

  @Override
  public String createTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    if (tablesWithNotSuperType.isEmpty()) {
      // we need to get the list of tables which need to be updated only once
      discoverNotSuperTables(database, schemaName);
    }
    if (tablesWithNotSuperType.contains(tableName)) {
      // To keep the previous data, we need to add next columns: _airbyte_data, _airbyte_emitted_at
      // We do such workflow because we can't directly CAST VARCHAR to SUPER column. _airbyte_emitted_at column recreated to keep
      // the COLUMN order. This order is required to INSERT the values in correct way.
      LOGGER.info("Altering table {} column _airbyte_data to SUPER.", tableName);
      return String.format("""
              ALTER TABLE %1$s.%2$s ADD COLUMN %3$s_super super;
              ALTER TABLE %1$s.%2$s ADD COLUMN %4$s_reserve TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
              UPDATE %1$s.%2$s SET %3$s_super = JSON_PARSE(%3$s);
              UPDATE %1$s.%2$s SET %4$s_reserve = %4$s;
              ALTER TABLE %1$s.%2$s DROP COLUMN %3$s;
              ALTER TABLE %1$s.%2$s DROP COLUMN %4$s;
              ALTER TABLE %1$s.%2$s RENAME %3$s_super to %3$s;
              ALTER TABLE %1$s.%2$s RENAME %4$s_reserve to %4$s;
              """,
          schemaName,
          tableName,
          JavaBaseConstants.COLUMN_NAME_DATA,
          JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
    }
    LOGGER.info("Creating new table...");
    return redshiftDataTmpTableMode.getTmpTableSqlStatement(schemaName, tableName);
  }

  @Override
  public void insertRecordsInternal(final JdbcDatabase database,
      final List<AirbyteRecordMessage> records,
      final String schemaName,
      final String tmpTableName)
      throws SQLException {
    LOGGER.info("actual size of batch: {}", records.size());

    // query syntax:
    // INSERT INTO public.users (ab_id, data, emitted_at) VALUES
    // (?, ?::jsonb, ?),
    // ...
    final String insertQueryComponent = String.format(
        "INSERT INTO %s.%s (%s, %s, %s) VALUES\n",
        schemaName,
        tmpTableName,
        JavaBaseConstants.COLUMN_NAME_AB_ID,
        JavaBaseConstants.COLUMN_NAME_DATA,
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
    final String recordQueryComponent = redshiftDataTmpTableMode.getInsertRowMode();
    SqlOperationsUtils.insertRawRecordsInSingleQuery(insertQueryComponent, recordQueryComponent, database, records);
  }

  @Override
  public boolean isValidData(final JsonNode data) {
    final String stringData = Jsons.serialize(data);
    final int dataSize = stringData.getBytes(StandardCharsets.UTF_8).length;
    return dataSize <= REDSHIFT_VARCHAR_MAX_BYTE_SIZE;
  }


  /**
   * @param database   - Database object for interacting with a JDBC connection.
   * @param schemaName - schema to update.
   */
  private void discoverNotSuperTables(final JdbcDatabase database,
      final String schemaName) {
    try {
      LOGGER.info("Selecting table types...");
      database.execute(String.format("set search_path to %s", schemaName));
      final List<JsonNode> tablesNameWithoutSuperDatatype = database.bufferedResultSetQuery(
          conn -> conn.createStatement().executeQuery(String.format("""
                  select tablename\n
                  from pg_table_def\n
                  where\n
                  schemaname = \'%s\'\n
                  and \"column\" = \'%s\'\n
                  and type <> \'super\'\n
                  and tablename like \'%%raw%%\'""",
              schemaName,
              JavaBaseConstants.COLUMN_NAME_DATA)),
          getDefaultSourceOperations()::rowToJson);
      if (tablesNameWithoutSuperDatatype.isEmpty()) {
        tablesWithNotSuperType.add("_airbyte_data in all tables is SUPER type.");
      } else {
        tablesNameWithoutSuperDatatype.forEach(e -> tablesWithNotSuperType.add(e.get("tablename").textValue()));
      }
    } catch (SQLException e) {
      LOGGER.error("Error during discoverNotSuperTables() appears: ", e);
    } catch (Exception e) {
      e.printStackTrace();
    }
  }
}

