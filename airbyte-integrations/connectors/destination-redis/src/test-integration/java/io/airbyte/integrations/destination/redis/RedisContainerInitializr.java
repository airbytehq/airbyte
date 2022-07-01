/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

import org.testcontainers.containers.GenericContainer;

class RedisContainerInitializr {

  private static RedisContainer redisContainer;

  private RedisContainerInitializr() {

  }

  static RedisContainer initContainer() {
    if (redisContainer == null) {
      redisContainer = new RedisContainer()
          .withExposedPorts(6379);
    }
    redisContainer.start();
    return redisContainer;
  }

  static class RedisContainer extends GenericContainer<RedisContainer> {

    public RedisContainer() {
      // latest docker release
      super("redis:6.0");
    }

  }

}
