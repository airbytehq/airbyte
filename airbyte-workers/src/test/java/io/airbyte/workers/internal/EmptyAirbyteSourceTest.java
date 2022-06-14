package io.airbyte.workers.internal;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ResetSourceConfiguration;
import io.airbyte.config.WorkerSourceConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import java.util.ArrayList;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class EmptyAirbyteSourceTest {
  private EmptyAirbyteSource emptyAirbyteSource;
  private final AirbyteMessage EMPTY_MESSAGE =
      new AirbyteMessage().withType(Type.STATE).withState(new AirbyteStateMessage().withStateType(AirbyteStateType.LEGACY).withData(Jsons.emptyObject()));

  @BeforeEach
  public void init() {
    emptyAirbyteSource = new EmptyAirbyteSource();
  }

  @Test
  public void testLegacy() throws Exception {
    emptyAirbyteSource.start(new WorkerSourceConfig(), null);

    legacyStateResult();
  }

  @Test
  public void testEmptyListOfStreams() throws Exception {
    ResetSourceConfiguration resetSourceConfiguration = new ResetSourceConfiguration()
        .withStreamsToReset(new ArrayList<>());
    WorkerSourceConfig workerSourceConfig = new WorkerSourceConfig()
        .withSourceConnectionConfiguration(Jsons.jsonNode(resetSourceConfiguration));

    emptyAirbyteSource.start(workerSourceConfig, null);

    legacyStateResult();
  }

  @Test
  public void nonStartedSource() {
    Assertions.assertThatThrownBy()
  }

  private void legacyStateResult() {
    Assertions.assertThat(emptyAirbyteSource.attemptRead())
        .isNotEmpty()
        .contains(EMPTY_MESSAGE);

    Assertions.assertThat(emptyAirbyteSource.attemptRead())
        .isEmpty();
  }
}
