/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.enums;

import io.airbyte.integrations.base.JavaBaseConstants;

/**
 * This enum determines the type for _airbyte_data_ column at _airbyte_raw_**some_table_name**
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
