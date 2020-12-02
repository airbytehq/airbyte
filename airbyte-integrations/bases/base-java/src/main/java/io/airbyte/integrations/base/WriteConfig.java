package io.airbyte.integrations.base;

import io.airbyte.protocol.models.SyncMode;

public class WriteConfig {
  private final String schemaName;
  private final String tableName;
  private final String tmpTableName;
  private final SyncMode syncMode;

  public WriteConfig(String schemaName, String tableName, String tmpTableName, SyncMode syncMode) {
    this.schemaName = schemaName;
    this.tableName = tableName;
    this.tmpTableName = tmpTableName;
    this.syncMode = syncMode;
  }

  public String getSchemaName() {
    return schemaName;
  }

  public String getTableName() {
    return tableName;
  }

  public String getTmpTableName() {
    return tmpTableName;
  }

  public SyncMode getSyncMode() {
    return syncMode;
  }
}
