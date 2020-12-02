package io.airbyte.integrations.base;

import io.airbyte.protocol.models.SyncMode;

public class DestinationWriteContext {
  private final String outputNamespaceName;
  private final String outputTableName;
  private final SyncMode syncMode;

  DestinationWriteContext(String outputNamespaceName, String outputTableName, SyncMode syncMode) {
    this.outputNamespaceName = outputNamespaceName;
    this.outputTableName = outputTableName;
    this.syncMode = syncMode;
  }

  public String getOutputNamespaceName() {
    return outputNamespaceName;
  }

  public String getOutputTableName() {
    return outputTableName;
  }

  public SyncMode getSyncMode() {
    return syncMode;
  }
}
