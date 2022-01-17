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
    public String getTableCreationMode() {
      return "SUPER";
    }

    @Override
    public String getInsertRowMode() {
      return "(?, JSON_PARSE(?), ?),\n";
    }
  },
  VARCHAR {
    @Override
    public String getTableCreationMode() {
      return "VARCHAR(MAX)";
    }

    @Override
    public String getInsertRowMode() {
      return "(?, ?, ?),\n";
    }
  };

  public abstract String getTableCreationMode();

  public abstract String getInsertRowMode();

  public String getTmpTableSqlStatement(String schemaName, String tableName) {
    return String.format("""
            CREATE TABLE IF NOT EXISTS %s.%s (
            %s VARCHAR PRIMARY KEY,
            %s %s,
            %s TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP)
            """, schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_ID,
        JavaBaseConstants.COLUMN_NAME_DATA,
        getTableCreationMode(),
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
  }
}
