package io.airbyte.integrations.destination.redshift;

import io.airbyte.integrations.base.JavaBaseConstants;

public enum RedshiftDataTmpTableMode {
  SUPER {
    @Override
    public String getTmpTableSqlStatement(String schemaName, String tableName) {
      return String.format(
          "CREATE TABLE IF NOT EXISTS %s.%s ( \n"
              + "%s VARCHAR PRIMARY KEY,\n"
              + "%s SUPER,\n"
              + "%s TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP\n"
              + ");\n",
          schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_DATA, JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
    }
  },
  VARCHAR {
    @Override
    public String getTmpTableSqlStatement(String schemaName, String tableName) {
      return String.format(
          "CREATE TABLE IF NOT EXISTS %s.%s ( \n"
              + "%s VARCHAR PRIMARY KEY,\n"
              + "%s VARCHAR(max),\n"
              + "%s TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP\n"
              + ");\n",
          schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_DATA, JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
    }
  };

  public abstract String getTmpTableSqlStatement(String schemaName, String tableName);
}
