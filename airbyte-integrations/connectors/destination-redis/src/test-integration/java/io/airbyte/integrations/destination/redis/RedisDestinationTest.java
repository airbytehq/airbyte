/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

import static org.assertj.core.api.Assertions.assertThat;

import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class RedisDestinationTest {

  private static RedisContainerInitializr.RedisContainer redisContainer;

  private RedisDestination redisDestination;

  @BeforeAll
  static void setup() {
    redisContainer = RedisContainerInitializr.initContainer();
  }

  @BeforeEach
  void init() {
    this.redisDestination = new RedisDestination();
  }

  @Test
  void testCheckWithStatusSucceeded() {

    var jsonConfiguration = RedisDataFactory.jsonConfig(
        redisContainer.getHost(),
        redisContainer.getFirstMappedPort());

    var connectionStatus = redisDestination.check(jsonConfiguration);

    assertThat(connectionStatus.getStatus()).isEqualTo(AirbyteConnectionStatus.Status.SUCCEEDED);
  }

  @Test
  void testCheckWithStatusFailed() {

    var jsonConfiguration = RedisDataFactory.jsonConfig("192.0.2.1", 8080);

    var connectionStatus = redisDestination.check(jsonConfiguration);

    assertThat(connectionStatus.getStatus()).isEqualTo(AirbyteConnectionStatus.Status.FAILED);

  }

}
