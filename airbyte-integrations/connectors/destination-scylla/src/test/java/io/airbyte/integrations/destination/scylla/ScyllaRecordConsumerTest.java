package io.airbyte.integrations.destination.scylla;


import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension

@DisplayName("ScyllaRecordConsumer")
@ExtendWith(MockitoExtension.class)
public class ScyllaRecordConsumerTest extends PerStreamStateMessageTest {
  @Mock
  private Consumer<AirbyteMessage> outputRecordCollector;

  private ScyllaMessageConsumer consumer;

  @Mock
  ScyllaConfig scyllaConfig;

  @Mock
  private ConfiguredAirbyteCatalog configuredCatalog;

  @BeforeEach
  public void init() {
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
}
