/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc;

import io.airbyte.protocol.models.DestinationSyncMode;

/**
 * Write configuration POJO for all destinations extending {@link AbstractJdbcDestination}.
 */
public class WriteConfig {

  private final String streamName;

  private final String namespace;

  private final String outputSchemaName;
  private final String tmpTableName;
  private final String outputTableName;
  private final DestinationSyncMode syncMode;

  public WriteConfig(String streamName,
                     String namespace,
                     String outputSchemaName,
                     String tmpTableName,
                     String outputTableName,
                     DestinationSyncMode syncMode) {
    this.streamName = streamName;
    this.namespace = namespace;
    this.outputSchemaName = outputSchemaName;
    this.tmpTableName = tmpTableName;
    this.outputTableName = outputTableName;
    this.syncMode = syncMode;
  }

  public String getStreamName() {
    return streamName;
  }

  public String getNamespace() {
    return namespace;
  }

  public String getTmpTableName() {
    return tmpTableName;
  }

  public String getOutputSchemaName() {
    return outputSchemaName;
  }

  public String getOutputTableName() {
    return outputTableName;
  }

  public DestinationSyncMode getSyncMode() {
    return syncMode;
  }

  @Override
  public String toString() {
    return "WriteConfig{" +
        "streamName=" + streamName +
        ", namespace=" + namespace +
        ", outputSchemaName=" + outputSchemaName +
        ", tmpTableName=" + tmpTableName +
        ", outputTableName=" + outputTableName +
        ", syncMode=" + syncMode +
        '}';
  }

}
