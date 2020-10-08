package io.airbyte.config.persistence;

import com.google.common.collect.Lists;
import io.airbyte.commons.json.JsonValidationException;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnectionSpecification;
import io.airbyte.config.SourceConnectionSpecification;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import java.io.IOException;
import java.util.ArrayList;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class ConfigRepositoryTest {

  private ConfigPersistence configPersistence = mock(ConfigPersistence.class);
  private ConfigRepository repository = new ConfigRepository(configPersistence);
  @Test
  void getSourceConnectionSpecificationFromSourceId() throws JsonValidationException, IOException, ConfigNotFoundException {
    UUID id1 = UUID.randomUUID();
    UUID id2 = UUID.randomUUID();

    SourceConnectionSpecification spec1 = new SourceConnectionSpecification().withSourceId(id1);
    SourceConnectionSpecification spec2 = new SourceConnectionSpecification().withSourceId(id2);

    ArrayList<SourceConnectionSpecification> specs = Lists.newArrayList(spec1, spec2);
    when(configPersistence.listConfigs(ConfigSchema.SOURCE_CONNECTION_SPECIFICATION, SourceConnectionSpecification.class))
        .thenReturn(specs);

    SourceConnectionSpecification actual = repository.getSourceConnectionSpecificationFromSourceId(id1);

    assertEquals(spec1, actual);
  }

  @Test
  void getDestinationConnectionSpecificationFromDestinationId() throws JsonValidationException, IOException, ConfigNotFoundException {
    UUID id1 = UUID.randomUUID();
    UUID id2 = UUID.randomUUID();

    DestinationConnectionSpecification spec1 = new DestinationConnectionSpecification().withDestinationId(id1);
    DestinationConnectionSpecification spec2 = new DestinationConnectionSpecification().withDestinationId(id2);

    ArrayList<DestinationConnectionSpecification> specs = Lists.newArrayList(spec1, spec2);
    when(configPersistence.listConfigs(ConfigSchema.DESTINATION_CONNECTION_SPECIFICATION, DestinationConnectionSpecification.class))
        .thenReturn(specs);

    DestinationConnectionSpecification actual = repository.getDestinationConnectionSpecificationFromDestinationId(id1);

    assertEquals(spec1, actual);
  }
}
