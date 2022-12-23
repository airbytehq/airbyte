/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.elasticsearch;

import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.util.List;
import java.util.Objects;

public class ElasticsearchWriteConfig {

  private static final StandardNameTransformer namingResolver = new StandardNameTransformer();

  private String namespace;
  private String streamName;
  private DestinationSyncMode syncMode;
  private List<List<String>> primaryKey;
  private boolean upsert;

  public ElasticsearchWriteConfig() {}

  ElasticsearchWriteConfig(
                           String namespace,
                           String streamName,
                           DestinationSyncMode destinationSyncMode,
                           List<List<String>> primaryKey,
                           boolean upsert) {
    this.namespace = namespace;
    this.streamName = streamName;
    this.syncMode = destinationSyncMode;
    this.primaryKey = primaryKey;
    this.upsert = upsert;
  }

  public String getNamespace() {
    return namespace;
  }

  public ElasticsearchWriteConfig setNamespace(String namespace) {
    this.namespace = namespace;
    return this;
  }

  public String getStreamName() {
    return streamName;
  }

  public ElasticsearchWriteConfig setStreamName(String streamName) {
    this.streamName = streamName;
    return this;
  }

  public DestinationSyncMode getSyncMode() {
    return syncMode;
  }

  public ElasticsearchWriteConfig setSyncMode(DestinationSyncMode syncMode) {
    this.syncMode = syncMode;
    return this;
  }

  public List<List<String>> getPrimaryKey() {
    return this.primaryKey;
  }

  public ElasticsearchWriteConfig setPrimaryKey(List<List<String>> primaryKey) {
    this.primaryKey = primaryKey;
    return this;
  }

  public boolean hasPrimaryKey() {
    return Objects.nonNull(this.primaryKey) && this.primaryKey.size() > 0;
  }

  public boolean isUpsert() {
    return upsert;
  }

  public ElasticsearchWriteConfig setUpsert(boolean upsert) {
    this.upsert = upsert;
    return this;
  }

  public boolean useTempIndex() {
    return (this.syncMode == DestinationSyncMode.OVERWRITE) && !(this.upsert);
  }

  public String getIndexName() {
    String prefix = "";
    if (Objects.nonNull(namespace) && !namespace.isEmpty()) {
      prefix = String.format("%s_", namespace).toLowerCase();
    }
    return String.format("%s%s", prefix, namingResolver.getIdentifier(streamName).toLowerCase());
  }

  public String getTempIndexName() {
    return String.format("tmp_%s", getIndexName());
  }

}
