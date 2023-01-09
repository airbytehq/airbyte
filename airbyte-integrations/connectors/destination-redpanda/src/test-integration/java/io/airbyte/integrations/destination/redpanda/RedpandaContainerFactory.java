/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redpanda;

import org.testcontainers.redpanda.RedpandaContainer;

class RedpandaContainerFactory {

  private RedpandaContainerFactory() {

  }

  public static RedpandaContainer createRedpandaContainer() {
    return new RedpandaContainer("docker.redpanda.com/vectorized/redpanda:v22.2.7");
  }

}
