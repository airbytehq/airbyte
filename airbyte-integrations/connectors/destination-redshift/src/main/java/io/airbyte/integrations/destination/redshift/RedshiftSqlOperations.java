/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import static io.airbyte.db.jdbc.JdbcUtils.getDefaultSourceOperations;
import static java.util.stream.Collectors.toSet;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.SqlOperationsUtils;
import io.airbyte.integrations.destination.jdbc.WriteConfig;
import io.airbyte.integrations.destination.redshift.enums.RedshiftDataTmpTableMode;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.nio.charset.StandardCharsets;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedshiftSqlOperations extends JdbcSqlOperations implements SqlOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftSqlOperations.class);
  protected static final int REDSHIFT_VARCHAR_MAX_BYTE_SIZE = 65535;
  private static final String SELECT_ALL_TABLES_WITH_NOT_SUPER_TYPE_SQL_STATEMENT = """
      select tablename, schemaname
      from pg_table_def
      where
      schemaname = '%s'
      and "column" = '%s'
      and type <> 'super'
      and tablename like '%%raw%%'""";
  private static final String ALTER_TMP_TABLES_WITH_NOT_SUPER_TYPE_TO_SUPER_TYPE = """
      ALTER TABLE %1$s ADD COLUMN %2$s_super super;
      ALTER TABLE %1$s ADD COLUMN %3$s_reserve TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
      UPDATE %1$s SET %2$s_super = JSON_PARSE(%2$s);
      UPDATE %1$s SET %3$s_reserve = %3$s;
      ALTER TABLE %1$s DROP COLUMN %2$s;
      ALTER TABLE %1$s DROP COLUMN %3$s;
      ALTER TABLE %1$s RENAME %2$s_super to %2$s;
      ALTER TABLE %1$s RENAME %3$s_reserve to %3$s;
      """;

  private final RedshiftDataTmpTableMode redshiftDataTmpTableMode;

  public RedshiftSqlOperations(final RedshiftDataTmpTableMode redshiftDataTmpTableMode) {
    this.redshiftDataTmpTableMode = redshiftDataTmpTableMode;
  }

  @Override
  public String createTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
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
  private List<String> discoverNotSuperTables(final JdbcDatabase database,
      final String schemaName) {
    List<String> schemaAndTableWithNotSuperType = new ArrayList<>();
    try {
      LOGGER.info("Selecting table types...");
      database.execute(String.format("set search_path to %s", schemaName));
      final List<JsonNode> tablesNameWithoutSuperDatatype = database.bufferedResultSetQuery(
          conn -> conn.createStatement().executeQuery(String.format(SELECT_ALL_TABLES_WITH_NOT_SUPER_TYPE_SQL_STATEMENT,
              schemaName,
              JavaBaseConstants.COLUMN_NAME_DATA)),
          getDefaultSourceOperations()::rowToJson);
      if (tablesNameWithoutSuperDatatype.isEmpty()) {
        return Collections.emptyList();
      } else {
        tablesNameWithoutSuperDatatype.forEach(e -> 
            schemaAndTableWithNotSuperType.add(e.get("schemaname").textValue()  + "." + e.get("tablename").textValue()));
        return schemaAndTableWithNotSuperType;
      }
    } catch (SQLException e) {
      LOGGER.error("Error during discoverNotSuperTables() appears: ", e);
    } catch (Exception e) {
      e.printStackTrace();
    }
    return Collections.emptyList();
  }

  /**
   * In case of redshift we need to discover all tables with not super type and update them after to SUPER type.
   * This would be done once.
   * @param database - Database object for interacting with a JDBC connection.
   * @param writeConfigsList - list of write configs.
   */
  @Override
  public void executeSpecificLogicForDBEngine(JdbcDatabase database, List<WriteConfig> writeConfigsList) {
    LOGGER.info("Executing specific logic for Redshift Destination DB engine...");
    List<String> schemaAndTableWithNotSuperType = new ArrayList<>();
    Set<String> schemas = writeConfigsList.stream().map(WriteConfig::getOutputSchemaName).collect(toSet());
    for (String schemaName : schemas) {
      schemaAndTableWithNotSuperType.addAll(discoverNotSuperTables(database, schemaName));
    }
    if (!schemaAndTableWithNotSuperType.isEmpty()) {
      updateJSONDataColumnToSuperDataColumn(database, schemaAndTableWithNotSuperType);
    }
  }

  /**
   * We prepare one query for all tables with not super type for updating.
   *
   * @param database - Database object for interacting with a JDBC connection.
   * @param schemaAndTableWithNotSuperType - list of tables with not super type.
   */
  private void updateJSONDataColumnToSuperDataColumn(JdbcDatabase database, List <String> schemaAndTableWithNotSuperType) {
    LOGGER.info("Updating JSON data column to super...");
    StringBuilder finalSqlStatement = new StringBuilder();
    // To keep the previous data, we need to add next columns: _airbyte_data, _airbyte_emitted_at
    // We do such workflow because we can't directly CAST VARCHAR to SUPER column. _airbyte_emitted_at column recreated to keep
    // the COLUMN order. This order is required to INSERT the values in correct way.
    schemaAndTableWithNotSuperType.forEach(schemaAndTable -> {
      LOGGER.info("Altering table {} column _airbyte_data to SUPER.", schemaAndTable);
      finalSqlStatement.append(String.format(ALTER_TMP_TABLES_WITH_NOT_SUPER_TYPE_TO_SUPER_TYPE,
          schemaAndTable,
          JavaBaseConstants.COLUMN_NAME_DATA,
          JavaBaseConstants.COLUMN_NAME_EMITTED_AT));
    });
    try {
      database.execute(finalSqlStatement.toString());
    } catch (SQLException e) {
      LOGGER.error("Error during updateJSONDataColumnToSuperDataColumn() appears: ", e);
    }
  }
}

