/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.cassandra;

import static org.assertj.core.api.Assertions.assertThat;

import io.airbyte.integrations.destination.cassandra.CassandraContainerInitializr.ConfiguredCassandraContainer;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class CassandraDestinationIT {

  private CassandraDestination cassandraDestination;

  private ConfiguredCassandraContainer cassandraContainer;

  @BeforeAll
  void setup() {
    this.cassandraContainer = CassandraContainerInitializr.initContainer();
    this.cassandraDestination = new CassandraDestination();
  }

  @Test
  void testCheckWithStatusSucceeded() {

    var jsonConfiguration = TestDataFactory.createJsonConfig(
        cassandraContainer.getUsername(),
        cassandraContainer.getPassword(),
        cassandraContainer.getHost(),
        cassandraContainer.getFirstMappedPort());

    var connectionStatus = cassandraDestination.check(jsonConfiguration);

    assertThat(connectionStatus.getStatus()).isEqualTo(AirbyteConnectionStatus.Status.SUCCEEDED);
  }

  @Test
  void testCheckWithStatusFailed() {

    var jsonConfiguration = TestDataFactory.createJsonConfig(
        "usr",
        "pw",
        "192.0.2.1",
        8080);

    var connectionStatus = cassandraDestination.check(jsonConfiguration);

    assertThat(connectionStatus.getStatus()).isEqualTo(AirbyteConnectionStatus.Status.FAILED);

  }

}
