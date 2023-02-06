/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kinesis;

import static org.assertj.core.api.Assertions.assertThat;

import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class KinesisDestinationTest {

  private static KinesisContainerInitializr.KinesisContainer kinesisContainer;

  private KinesisDestination kinesisDestination;

  @BeforeAll
  static void setup() {
    kinesisContainer = KinesisContainerInitializr.initContainer();
  }

  @BeforeEach
  void init() {
    this.kinesisDestination = new KinesisDestination();
  }

  @Test
  void testCheckConnectionWithSuccess() {

    var jsonConfig = KinesisDataFactory.jsonConfig(
        kinesisContainer.getEndpointOverride().toString(),
        kinesisContainer.getRegion(),
        kinesisContainer.getAccessKey(),
        kinesisContainer.getSecretKey());

    var connectionStatus = kinesisDestination.check(jsonConfig);

    assertThat(connectionStatus.getStatus()).isEqualTo(AirbyteConnectionStatus.Status.SUCCEEDED);
  }

  @Test
  void testCheckTestConnectionWithFailure() {

    var jsonConfig = KinesisDataFactory.jsonConfig(
        "127.0.0.9",
        "eu-west-1",
        "random_access_key",
        "random_secret_key");

    var connectionStatus = kinesisDestination.check(jsonConfig);

    assertThat(connectionStatus.getStatus()).isEqualTo(AirbyteConnectionStatus.Status.FAILED);

  }

}
