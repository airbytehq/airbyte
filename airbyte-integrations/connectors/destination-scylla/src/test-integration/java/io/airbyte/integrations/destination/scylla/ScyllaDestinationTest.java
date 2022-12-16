/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.scylla;

import static org.assertj.core.api.Assertions.assertThat;

import io.airbyte.integrations.destination.scylla.ScyllaContainerInitializr.ScyllaContainer;
import io.airbyte.integrations.util.HostPortResolver;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class ScyllaDestinationTest {

  private ScyllaDestination scyllaDestination;

  private ScyllaContainer scyllaContainer;

  @BeforeAll
  void setup() {
    this.scyllaContainer = ScyllaContainerInitializr.initContainer();
    this.scyllaDestination = new ScyllaDestination();
  }

  @Test
  void testCheckWithStatusSucceeded() {

    var jsonConfiguration = TestDataFactory.jsonConfig(
        HostPortResolver.resolveHost(scyllaContainer),
        HostPortResolver.resolvePort(scyllaContainer));

    var connectionStatus = scyllaDestination.check(jsonConfiguration);

    assertThat(connectionStatus.getStatus()).isEqualTo(AirbyteConnectionStatus.Status.SUCCEEDED);
  }

  @Test
  void testCheckWithStatusFailed() {

    var jsonConfiguration = TestDataFactory.jsonConfig("192.0.2.1", 8080);

    var connectionStatus = scyllaDestination.check(jsonConfiguration);

    assertThat(connectionStatus.getStatus()).isEqualTo(AirbyteConnectionStatus.Status.FAILED);

  }

}
