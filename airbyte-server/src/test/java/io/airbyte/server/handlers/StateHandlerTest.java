package io.airbyte.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.when;

import com.google.common.collect.ImmutableMap;
import io.airbyte.api.model.generated.CheckConnectionRead;
import io.airbyte.api.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.model.generated.ConnectionState;
import io.airbyte.api.model.generated.ConnectionStateType;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.State;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.scheduler.client.EventRunner;
import io.airbyte.scheduler.client.SynchronousResponse;
import io.airbyte.scheduler.client.SynchronousSchedulerClient;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobStatus;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.server.converters.ConfigurationUpdate;
import io.airbyte.server.converters.JobConverter;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.io.IOException;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.EnumSource;

public class StateHandlerTest {
  private StateHandler stateHandler;
  private ConfigRepository configRepository;

  @BeforeEach
  void setup() {
    configRepository = mock(ConfigRepository.class);
    stateHandler = new StateHandler(configRepository);
  }


  @Test
  void testGetCurrentState() throws IOException {
    final UUID connectionId = UUID.randomUUID();
    final State state = new State().withState(Jsons.jsonNode(ImmutableMap.of("checkpoint", 1)));
    when(configRepository.getConnectionState(connectionId)).thenReturn(Optional.of(state));

    final ConnectionState connectionState = stateHandler.getState(new ConnectionIdRequestBody().connectionId(connectionId));
    assertEquals(new ConnectionState().connectionId(connectionId).state(state.getState()), connectionState);
  }

  @Test
  void testGetCurrentStateEmpty() throws IOException {
    final UUID connectionId = UUID.randomUUID();
    when(configRepository.getConnectionState(connectionId)).thenReturn(Optional.empty());

    final ConnectionState connectionState = stateHandler.getState(new ConnectionIdRequestBody().connectionId(connectionId));
    assertEquals(new ConnectionState().connectionId(connectionId), connectionState);
  }

  @ParameterizedTest
  @EnumSource(AirbyteStateMessage.AirbyteStateType.class)
  void testGetStateType(final AirbyteStateMessage.AirbyteStateType stateType) {
    when(configRepository.getConnectionState(configRepository)).thenReturn()
  }

  @Test
  void testEnumConversion() {
    assertTrue(Enums.isCompatible(AirbyteStateMessage.AirbyteStateType.class, ConnectionStateType.class));
  }
}
