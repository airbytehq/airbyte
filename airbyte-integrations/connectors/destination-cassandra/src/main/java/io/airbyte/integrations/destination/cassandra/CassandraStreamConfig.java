/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.cassandra;

import io.airbyte.protocol.models.v0.DestinationSyncMode;

/*
 * Immutable configuration class for storing destination stream config.
 */
class CassandraStreamConfig {

  private final String keyspace;

  private final String tableName;

  private final String tempTableName;

  private final DestinationSyncMode destinationSyncMode;

  public CassandraStreamConfig(String keyspace,
                               String tableName,
                               String tempTableName,
                               DestinationSyncMode destinationSyncMode) {
    this.keyspace = keyspace;
    this.tableName = tableName;
    this.tempTableName = tempTableName;
    this.destinationSyncMode = destinationSyncMode;
  }

  public String getKeyspace() {
    return keyspace;
  }

  public String getTableName() {
    return tableName;
  }

  public String getTempTableName() {
    return tempTableName;
  }

  public DestinationSyncMode getDestinationSyncMode() {
    return destinationSyncMode;
  }

  @Override
  public String toString() {
    return "CassandraStreamConfig{" +
        "keyspace='" + keyspace + '\'' +
        ", tableName='" + tableName + '\'' +
        ", tempTableName='" + tempTableName + '\'' +
        ", destinationSyncMode=" + destinationSyncMode +
        '}';
  }

}
