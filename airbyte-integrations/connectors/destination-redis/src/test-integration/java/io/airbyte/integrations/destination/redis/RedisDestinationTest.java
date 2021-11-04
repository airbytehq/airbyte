/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

import static org.assertj.core.api.Assertions.assertThat;

import io.airbyte.protocol.models.AirbyteConnectionStatus;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class RedisDestinationTest {

  private RedisDestination redisDestination;

  private RedisContainerInitializr.RedisContainer redisContainer;

  @BeforeAll
  void setup() {
    this.redisContainer = RedisContainerInitializr.initContainer();
    this.redisDestination = new RedisDestination();
  }

  @Test
  void testCheckWithStatusSucceeded() {

    var jsonConfiguration = TestDataFactory.jsonConfig(
        redisContainer.getHost(),
        redisContainer.getFirstMappedPort());

    var connectionStatus = redisDestination.check(jsonConfiguration);

    assertThat(connectionStatus.getStatus()).isEqualTo(AirbyteConnectionStatus.Status.SUCCEEDED);
  }

  @Test
  void testCheckWithStatusFailed() {

    var jsonConfiguration = TestDataFactory.jsonConfig("192.0.2.1", 8080);

    var connectionStatus = redisDestination.check(jsonConfiguration);

    assertThat(connectionStatus.getStatus()).isEqualTo(AirbyteConnectionStatus.Status.FAILED);

  }

}
