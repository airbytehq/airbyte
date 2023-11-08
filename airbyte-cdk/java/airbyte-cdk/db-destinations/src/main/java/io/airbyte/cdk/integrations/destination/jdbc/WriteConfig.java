/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc;

import io.airbyte.protocol.models.v0.DestinationSyncMode;
import org.joda.time.DateTime;
import org.joda.time.DateTimeZone;

/**
 * Write configuration POJO (plain old java object) for all destinations extending
 * {@link AbstractJdbcDestination}.
 */
public class WriteConfig {

  private final String streamName;
  private final String namespace;
  private final String outputSchemaName;
  private final String tmpTableName;
  private final String outputTableName;
  private final DestinationSyncMode syncMode;
  private final DateTime writeDatetime;

  public WriteConfig(final String streamName,
                     final String namespace,
                     final String outputSchemaName,
                     final String tmpTableName,
                     final String outputTableName,
                     final DestinationSyncMode syncMode) {
    this(streamName, namespace, outputSchemaName, tmpTableName, outputTableName, syncMode, DateTime.now(DateTimeZone.UTC));
  }

  public WriteConfig(final String streamName,
                     final String namespace,
                     final String outputSchemaName,
                     final String tmpTableName,
                     final String outputTableName,
                     final DestinationSyncMode syncMode,
                     final DateTime writeDatetime) {
    this.streamName = streamName;
    this.namespace = namespace;
    this.outputSchemaName = outputSchemaName;
    this.tmpTableName = tmpTableName;
    this.outputTableName = outputTableName;
    this.syncMode = syncMode;
    this.writeDatetime = writeDatetime;
  }

  public String getStreamName() {
    return streamName;
  }

  /**
   * This is used in {@link JdbcBufferedConsumerFactory} to verify that record is from expected
   * streams
   *
   * @return
   */
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

  public DateTime getWriteDatetime() {
    return writeDatetime;
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
