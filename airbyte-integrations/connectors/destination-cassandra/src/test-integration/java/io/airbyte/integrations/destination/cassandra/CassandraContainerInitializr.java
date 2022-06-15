/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.cassandra;

import org.testcontainers.containers.CassandraContainer;

class CassandraContainerInitializr {

  private static ConfiguredCassandraContainer cassandraContainer;

  private CassandraContainerInitializr() {

  }

  public static ConfiguredCassandraContainer initContainer() {
    if (cassandraContainer == null) {
      cassandraContainer = new ConfiguredCassandraContainer();
    }
    cassandraContainer.start();
    return cassandraContainer;
  }

  public static class ConfiguredCassandraContainer extends CassandraContainer<ConfiguredCassandraContainer> {

    ConfiguredCassandraContainer() {
      // latest compatible version with the internal testcontainers datastax driver.
      super("cassandra:3.11.11");
    }

  }

}
