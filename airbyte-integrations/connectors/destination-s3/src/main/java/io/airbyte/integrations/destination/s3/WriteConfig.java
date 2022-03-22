/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import io.airbyte.protocol.models.DestinationSyncMode;
import java.util.ArrayList;
import java.util.List;

/**
 * Write configuration POJO for blob storage destinations
 */
public class WriteConfig {

  private final String namespace;
  private final String streamName;
  private final String outputNamespace;
  private final String outputBucketPath;
  private final DestinationSyncMode syncMode;
  private final List<String> storedFiles;

  public WriteConfig(final String namespace,
                     final String streamName,
                     final String outputNamespace,
                     final String outputBucketPath,
                     final DestinationSyncMode syncMode) {
    this.namespace = namespace;
    this.streamName = streamName;
    this.outputNamespace = outputNamespace;
    this.outputBucketPath = outputBucketPath;
    this.syncMode = syncMode;
    this.storedFiles = new ArrayList<>();
  }

  public String getNamespace() {
    return namespace;
  }

  public String getStreamName() {
    return streamName;
  }

  public String getOutputNamespace() {
    return outputNamespace;
  }

  public String getOutputBucketPath() {
    return outputBucketPath;
  }

  public DestinationSyncMode getSyncMode() {
    return syncMode;
  }

  public List<String> getStoredFiles() {
    return storedFiles;
  }

  public void addStoredFile(final String file) {
    storedFiles.add(file);
  }

  public void clearStoredFiles() {
    storedFiles.clear();
  }

  @Override
  public String toString() {
    return "WriteConfig{" +
        "streamName=" + streamName +
        ", namespace=" + namespace +
        ", outputNamespace=" + outputNamespace +
        ", outputBucketPath=" + outputBucketPath +
        ", syncMode=" + syncMode +
        '}';
  }

}
