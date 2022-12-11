/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.scylla;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.standardtest.destination.PerStreamStateMessageTest;
import io.airbyte.integrations.util.HostPortResolver;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.testcontainers.containers.GenericContainer;

@DisplayName("ScyllaRecordConsumer")
@ExtendWith(MockitoExtension.class)
public class ScyllaRecordConsumerTest extends PerStreamStateMessageTest {

  private static ScyllaContainer scyllaContainer;

  @Mock
  private Consumer<AirbyteMessage> outputRecordCollector;

  private ScyllaMessageConsumer consumer;

  @Mock
  ScyllaConfig scyllaConfig;

  @Mock
  private ConfiguredAirbyteCatalog configuredCatalog;

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

  @BeforeEach
  public void init() {
    ScyllaContainer scyllaContainer = initContainer();
    JsonNode configJson = TestDataFactory.jsonConfig(
        HostPortResolver.resolveHost(scyllaContainer),
        HostPortResolver.resolvePort(scyllaContainer));
    var scyllaConfig = new ScyllaConfig(configJson);
    consumer = new ScyllaMessageConsumer(scyllaConfig, configuredCatalog, outputRecordCollector);
  }

  @Override
  protected Consumer<AirbyteMessage> getMockedConsumer() {
    return outputRecordCollector;
  }

  @Override
  protected FailureTrackingAirbyteMessageConsumer getMessageConsumer() {
    return consumer;
  }

  static class ScyllaContainer extends GenericContainer<ScyllaContainer> {

    public ScyllaContainer() {
      super("scylladb/scylla:4.5.0");
    }

  }

}
