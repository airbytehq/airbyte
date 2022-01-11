package io.airbyte.integrations.destination.redshift.enums;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.base.JavaBaseConstants;

/**
 * This enum determines the type for _airbyte_data_ column at _airbyte_raw_**some_table_name** SUPER type it is the special case of Amazon Redshift,
 * purpose of this to increase the performance of Normalization. We determine the behaviour of connector from UI Specification {@link
 * io.airbyte.integrations.destination.redshift.RedshiftDestination#getTypeFromConfig(JsonNode)} ()}
 */
public enum RedshiftDataTmpTableMode {
  SUPER {
    @Override
    public String getTmpTableSqlStatement(String sqlTmpTableQuery, String schemaName, String tableName) {
      return String.format(
          sqlTmpTableQuery,
          schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_ID,
          JavaBaseConstants.COLUMN_NAME_DATA,
          "SUPER",
          JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
    }
  },
  VARCHAR {
    @Override
    public String getTmpTableSqlStatement(String sqlTmpTableQuery, String schemaName, String tableName) {
      return String.format(
          sqlTmpTableQuery,
          schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_ID,
          JavaBaseConstants.COLUMN_NAME_DATA,
          "VARCHAR(MAX)",
          JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
    }
  };

  public abstract String getTmpTableSqlStatement(String sqlTmpTableQuery, String schemaName, String tableName);
}
