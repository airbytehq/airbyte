/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kinesis;

import io.airbyte.protocol.models.DestinationSyncMode;

/**
 * KinesisStreamConfig class for storing configuration data for every stream.
 */
public class KinesisStreamConfig {

  private final String streamName;

  private final String namespace;

  private final DestinationSyncMode destinationSyncMode;

  public KinesisStreamConfig(String streamName, String namespace, DestinationSyncMode destinationSyncMode) {
    this.streamName = streamName;
    this.namespace = namespace;
    this.destinationSyncMode = destinationSyncMode;
  }

  public String getStreamName() {
    return streamName;
  }

  public String getNamespace() {
    return namespace;
  }

  public DestinationSyncMode getDestinationSyncMode() {
    return destinationSyncMode;
  }

  @Override
  public String toString() {
    return "KinesisStreamConfig{" +
        "streamName='" + streamName + '\'' +
        ", destinationSyncMode=" + destinationSyncMode +
        '}';
  }

}
