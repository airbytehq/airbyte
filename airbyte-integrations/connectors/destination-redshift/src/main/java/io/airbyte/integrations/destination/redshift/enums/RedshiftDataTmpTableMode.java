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
    public String getMode() {
      return "SUPER";
    }
  },
  VARCHAR {
    @Override
    public String getMode() {
      return "VARCHAR(MAX)";
    }
  };

  public abstract String getMode();

  public String getTmpTableSqlStatement(String schemaName, String tableName) {
    return String.format("""
            CREATE TABLE IF NOT EXISTS %s.%s (
            %s VARCHAR PRIMARY KEY,
            %s %s,
            %s TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP)
            """, schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_ID,
        JavaBaseConstants.COLUMN_NAME_DATA,
        getMode(),
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
  }
}
