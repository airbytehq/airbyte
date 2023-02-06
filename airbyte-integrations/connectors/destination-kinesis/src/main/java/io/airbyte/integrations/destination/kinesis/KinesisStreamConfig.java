/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kinesis;

import io.airbyte.protocol.models.v0.DestinationSyncMode;

/**
 * KinesisStreamConfig class for storing configuration data for every stream.
 */
public class KinesisStreamConfig {

  private final String streamName;

  private final DestinationSyncMode destinationSyncMode;

  public KinesisStreamConfig(String streamName, DestinationSyncMode destinationSyncMode) {
    this.streamName = streamName;
    this.destinationSyncMode = destinationSyncMode;
  }

  public String getStreamName() {
    return streamName;
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
