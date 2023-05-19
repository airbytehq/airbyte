package io.airbyte.integrations.source.postgres.xmin;

import static org.junit.jupiter.api.Assertions.assertNotNull;

import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.List;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class XminStateManagerTest {

  public static final String NAMESPACE = "public";
  public static final String STREAM_NAME1 = "cars";

  @Test
  void testCreationFromInvalidState() {
    final AirbyteStateMessage airbyteStateMessage = new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(new AirbyteStreamState()
            .withStreamDescriptor(new StreamDescriptor().withName(STREAM_NAME1).withNamespace(NAMESPACE))
            .withStreamState(Jsons.jsonNode("Not a state object")));

    Assertions.assertDoesNotThrow(() -> {
      final XminStateManager xminStateManager = new XminStateManager(List.of(airbyteStateMessage));
      assertNotNull(xminStateManager);
    });
  }

  @Test
  void testGetXminStates() {

  }

  @Test
  void testCreateStateMessage() {

  }
}
