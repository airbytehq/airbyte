/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.scylla;

import org.testcontainers.containers.GenericContainer;

class ScyllaContainerInitializr {

  private static ScyllaContainer scyllaContainer;

  private ScyllaContainerInitializr() {

  }

  public static ScyllaContainer initContainer() {
    if (scyllaContainer == null) {
      scyllaContainer = new ScyllaContainer()
          .withExposedPorts(9042)
          // single cpu core cluster
          .withCommand("--smp 1");
    }
    scyllaContainer.start();
    return scyllaContainer;
  }

  static class ScyllaContainer extends GenericContainer<ScyllaContainer> {

    public ScyllaContainer() {
      super("scylladb/scylla:4.5.0");
    }

  }

}
