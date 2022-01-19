/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import io.airbyte.integrations.destination.ExtendedNameTransformer;

public class SnowflakeSQLNameTransformer extends ExtendedNameTransformer {

  @Override
  protected String applyDefaultCase(final String input) {
    return input.toUpperCase();
  }

  public String getStageName(String schemaName, String outputTableName) {
    return schemaName.concat(outputTableName).replaceAll("-", "_").toUpperCase();
  }

  public String getStagingPath(String schemaName, String tableName, String currentSyncPath) {
    return (getStageName(schemaName, tableName) + "/staged/" + currentSyncPath).toUpperCase();
  }

}
