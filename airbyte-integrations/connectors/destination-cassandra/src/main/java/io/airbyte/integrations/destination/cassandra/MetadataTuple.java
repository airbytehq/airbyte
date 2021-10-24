/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.cassandra;

import java.util.List;

class MetadataTuple {

  private final String keyspace;

  private final List<String> tables;

  public MetadataTuple(String keyspace, List<String> tables) {
    this.keyspace = keyspace;
    this.tables = tables;
  }

  public String getKeyspace() {
    return keyspace;
  }

  public List<String> getTables() {
    return tables;
  }

}
