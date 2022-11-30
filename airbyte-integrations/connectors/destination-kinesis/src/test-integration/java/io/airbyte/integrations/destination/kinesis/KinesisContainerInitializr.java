/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kinesis;

import java.net.URI;
import org.testcontainers.containers.localstack.LocalStackContainer;
import org.testcontainers.utility.DockerImageName;

public class KinesisContainerInitializr {

  private static KinesisContainer kinesisContainer;

  private KinesisContainerInitializr() {

  }

  static KinesisContainer initContainer() {
    if (kinesisContainer == null) {
      kinesisContainer = KinesisContainer.createContainer();
    }
    kinesisContainer.start();
    return kinesisContainer;
  }

  static class KinesisContainer extends LocalStackContainer {

    private KinesisContainer() {
      super(DockerImageName.parse("localstack/localstack:0.12.20"));
    }

    static KinesisContainer createContainer() {
      return (KinesisContainer) new KinesisContainer()
          .withServices(Service.KINESIS)
          // lower kinesis response latency to 200 ms to speed up tests
          .withEnv("KINESIS_LATENCY", "200")
          // increase default shard limit
          .withEnv("KINESIS_SHARD_LIMIT", "500");
    }

    URI getEndpointOverride() {
      return super.getEndpointOverride(LocalStackContainer.Service.KINESIS);
    }

  }

}
