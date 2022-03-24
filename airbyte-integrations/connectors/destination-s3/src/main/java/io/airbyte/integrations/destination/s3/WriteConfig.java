/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import io.airbyte.protocol.models.DestinationSyncMode;
import java.util.ArrayList;
import java.util.List;
import org.joda.time.DateTime;
import org.joda.time.DateTimeZone;

/**
 * Write configuration POJO for blob storage destinations
 */
public class WriteConfig {

  private final String streamName;

  private final String namespace;

  private final String outputNamespace;
  private final String outputBucket;
  private final DestinationSyncMode syncMode;
  private final DateTime writeDatetime;
  private final List<String> storedFiles;

  public WriteConfig(final String streamName,
                     final String namespace,
                     final String outputNamespace,
                     final String outputBucket,
                     final DestinationSyncMode syncMode) {
    this(streamName, namespace, outputNamespace, outputBucket, syncMode, DateTime.now(DateTimeZone.UTC));
  }

  public WriteConfig(final String streamName,
                     final String namespace,
                     final String outputNamespace,
                     final String outputBucket,
                     final DestinationSyncMode syncMode,
                     final DateTime writeDatetime) {
    this.streamName = streamName;
    this.namespace = namespace;
    this.outputNamespace = outputNamespace;
    this.outputBucket = outputBucket;
    this.syncMode = syncMode;
    this.storedFiles = new ArrayList<>();
    this.writeDatetime = writeDatetime;
  }

  public String getStreamName() {
    return streamName;
  }

  public String getNamespace() {
    return namespace;
  }

  public String getOutputNamespace() {
    return outputNamespace;
  }

  public String getOutputBucket() {
    return outputBucket;
  }

  public DestinationSyncMode getSyncMode() {
    return syncMode;
  }

  public DateTime getWriteDatetime() {
    return writeDatetime;
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
        ", outputBucket=" + outputBucket +
        ", syncMode=" + syncMode +
        '}';
  }

}
