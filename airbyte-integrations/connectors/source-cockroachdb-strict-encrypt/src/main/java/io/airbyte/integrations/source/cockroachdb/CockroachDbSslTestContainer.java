/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.cockroachdb;

import java.util.concurrent.TimeUnit;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.containers.Network;
import org.testcontainers.images.builder.ImageFromDockerfile;

public class CockroachDbSslTestContainer {

  private GenericContainer cockroachSslDbContainer;

  public void start() throws Exception {
    if (cockroachSslDbContainer != null)
      cockroachSslDbContainer.stop();

    Network network = Network.newNetwork();
    cockroachSslDbContainer = new GenericContainer(
        new ImageFromDockerfile("cockroach-test")
            .withFileFromClasspath("Dockerfile", "docker/Dockerfile")
            .withFileFromClasspath("cockroachdb_init.sh", "docker/cockroachdb_init.sh")
            .withFileFromClasspath("cockroachdb_test_user.sh", "docker/cockroachdb_test_user.sh"))
                .withNetwork(network)
                .withExposedPorts(26257);
    cockroachSslDbContainer.start();

    // Wait till test user is created
    TimeUnit.SECONDS.sleep(5);
  }

  public void close() {
    cockroachSslDbContainer.stop();
    cockroachSslDbContainer = null;
  }

  public GenericContainer getCockroachSslDbContainer() {
    return cockroachSslDbContainer;
  }

}
