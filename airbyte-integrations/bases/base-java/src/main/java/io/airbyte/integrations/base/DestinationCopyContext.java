package io.airbyte.integrations.base;

import io.airbyte.protocol.models.SyncMode;

public class DestinationCopyContext extends DestinationWriteContext {
  private final String inputTableName;

  DestinationCopyContext(String outputNamespaceName, String inputTableName, String outputTableName, SyncMode syncMode) {
    super(outputNamespaceName, outputTableName, syncMode);
    this.inputTableName = inputTableName;
  }

  public String getInputTableName() {
    return inputTableName;
  }
}
