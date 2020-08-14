package io.dataline.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.Sets;
import io.dataline.api.model.*;
import io.dataline.config.DestinationConnectionImplementation;
import io.dataline.config.DestinationConnectionSpecification;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.config.persistence.PersistenceConfigType;
import io.dataline.server.helpers.DestinationSpecificationHelpers;
import io.dataline.server.validation.IntegrationSchemaValidation;
import java.io.File;
import java.io.IOException;
import java.util.UUID;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DestinationImplementationsHandlerTest {
  private ConfigPersistence configPersistence;
  private DestinationConnectionSpecification destinationConnectionSpecification;
  private DestinationConnectionImplementation destinationConnectionImplementation;
  private DestinationImplementationsHandler destinationImplementationsHandler;
  private IntegrationSchemaValidation validator;
  private Supplier<UUID> uuidGenerator;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setUp() {
    configPersistence = mock(ConfigPersistence.class);
    validator = mock(IntegrationSchemaValidation.class);
    uuidGenerator = mock(Supplier.class);

    destinationConnectionSpecification =
        DestinationSpecificationHelpers.generateDestinationSpecification();
    destinationConnectionImplementation =
        generateDestinationImplementation(
            destinationConnectionSpecification.getDestinationSpecificationId());

    destinationImplementationsHandler =
        new DestinationImplementationsHandler(configPersistence, validator, uuidGenerator);
  }

  private JsonNode getTestImplementationJson() {
    final File implementationFile =
        new File("../dataline-server/src/test/resources/json/TestImplementation.json");

    try {
      return new ObjectMapper().readTree(implementationFile);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  private DestinationConnectionImplementation generateDestinationImplementation(
      UUID destinationSpecificationId) {
    final UUID workspaceId = UUID.randomUUID();
    final UUID destinationImplementationId = UUID.randomUUID();

    JsonNode implementationJson = getTestImplementationJson();

    final DestinationConnectionImplementation destinationConnectionImplementation =
        new DestinationConnectionImplementation();
    destinationConnectionImplementation.setWorkspaceId(workspaceId);
    destinationConnectionImplementation.setDestinationSpecificationId(destinationSpecificationId);
    destinationConnectionImplementation.setDestinationImplementationId(destinationImplementationId);
    destinationConnectionImplementation.setConfiguration(implementationJson.toString());

    return destinationConnectionImplementation;
  }

  @Test
  void testCreateDestinationImplementation()
      throws JsonValidationException, ConfigNotFoundException {
    when(uuidGenerator.get())
        .thenReturn(destinationConnectionImplementation.getDestinationImplementationId());

    when(configPersistence.getConfig(
            PersistenceConfigType.DESTINATION_CONNECTION_IMPLEMENTATION,
            destinationConnectionImplementation.getDestinationImplementationId().toString(),
            DestinationConnectionImplementation.class))
        .thenReturn(destinationConnectionImplementation);

    final DestinationImplementationCreate destinationImplementationCreate =
        new DestinationImplementationCreate();
    destinationImplementationCreate.setWorkspaceId(
        destinationConnectionImplementation.getWorkspaceId());
    destinationImplementationCreate.setDestinationSpecificationId(
        destinationConnectionSpecification.getDestinationSpecificationId());
    destinationImplementationCreate.setConnectionConfiguration(
        getTestImplementationJson().toString());

    final DestinationImplementationRead actualDestinationImplementationRead =
        destinationImplementationsHandler.createDestinationImplementation(
            destinationImplementationCreate);

    DestinationImplementationRead expectedDestinationImplementationRead =
        new DestinationImplementationRead();
    expectedDestinationImplementationRead.setDestinationSpecificationId(
        destinationConnectionSpecification.getDestinationSpecificationId());
    expectedDestinationImplementationRead.setWorkspaceId(
        destinationConnectionImplementation.getWorkspaceId());
    expectedDestinationImplementationRead.setDestinationImplementationId(
        destinationConnectionImplementation.getDestinationImplementationId());
    expectedDestinationImplementationRead.setConnectionConfiguration(
        getTestImplementationJson().toString());

    assertEquals(expectedDestinationImplementationRead, actualDestinationImplementationRead);

    verify(validator)
        .validateDestinationConnectionConfiguration(
            destinationConnectionSpecification.getDestinationSpecificationId(),
            destinationConnectionImplementation.getConfiguration());

    verify(configPersistence)
        .writeConfig(
            PersistenceConfigType.DESTINATION_CONNECTION_IMPLEMENTATION,
            destinationConnectionImplementation.getDestinationImplementationId().toString(),
            destinationConnectionImplementation);
  }

  @Test
  void testUpdateDestinationImplementation()
      throws JsonValidationException, ConfigNotFoundException {
    final Object configuration = destinationConnectionImplementation.getConfiguration();
    final JsonNode newConfiguration;
    try {
      newConfiguration = new ObjectMapper().readTree(configuration.toString());
    } catch (JsonProcessingException e) {
      throw new RuntimeException(e);
    }
    ((ObjectNode) newConfiguration).put("apiKey", "987-xyz");

    final DestinationConnectionImplementation expectedDestinationConnectionImplementation =
        new DestinationConnectionImplementation();
    expectedDestinationConnectionImplementation.setWorkspaceId(
        destinationConnectionImplementation.getWorkspaceId());
    expectedDestinationConnectionImplementation.setDestinationSpecificationId(
        destinationConnectionImplementation.getDestinationSpecificationId());
    expectedDestinationConnectionImplementation.setDestinationImplementationId(
        destinationConnectionImplementation.getDestinationImplementationId());
    expectedDestinationConnectionImplementation.setConfiguration(newConfiguration.toString());

    when(configPersistence.getConfig(
            PersistenceConfigType.DESTINATION_CONNECTION_IMPLEMENTATION,
            destinationConnectionImplementation.getDestinationImplementationId().toString(),
            DestinationConnectionImplementation.class))
        .thenReturn(destinationConnectionImplementation)
        .thenReturn(expectedDestinationConnectionImplementation);

    final DestinationImplementationUpdate destinationImplementationUpdate =
        new DestinationImplementationUpdate();
    destinationImplementationUpdate.setDestinationImplementationId(
        destinationConnectionImplementation.getDestinationImplementationId());
    destinationImplementationUpdate.setConnectionConfiguration(newConfiguration.toString());
    final DestinationImplementationRead actualDestinationImplementationRead =
        destinationImplementationsHandler.updateDestinationImplementation(
            destinationImplementationUpdate);

    DestinationImplementationRead expectedDestinationImplementationRead =
        new DestinationImplementationRead();
    expectedDestinationImplementationRead.setDestinationSpecificationId(
        destinationConnectionSpecification.getDestinationSpecificationId());
    expectedDestinationImplementationRead.setWorkspaceId(
        destinationConnectionImplementation.getWorkspaceId());
    expectedDestinationImplementationRead.setDestinationImplementationId(
        destinationConnectionImplementation.getDestinationImplementationId());
    expectedDestinationImplementationRead.setConnectionConfiguration(newConfiguration.toString());

    assertEquals(expectedDestinationImplementationRead, actualDestinationImplementationRead);

    verify(configPersistence)
        .writeConfig(
            PersistenceConfigType.DESTINATION_CONNECTION_IMPLEMENTATION,
            destinationConnectionImplementation.getDestinationImplementationId().toString(),
            expectedDestinationConnectionImplementation);
  }

  @Test
  void testGetDestinationImplementation() throws JsonValidationException, ConfigNotFoundException {
    when(configPersistence.getConfig(
            PersistenceConfigType.DESTINATION_CONNECTION_IMPLEMENTATION,
            destinationConnectionImplementation.getDestinationImplementationId().toString(),
            DestinationConnectionImplementation.class))
        .thenReturn(destinationConnectionImplementation);

    DestinationImplementationRead expectedDestinationImplementationRead =
        new DestinationImplementationRead();
    expectedDestinationImplementationRead.setDestinationSpecificationId(
        destinationConnectionImplementation.getDestinationSpecificationId());
    expectedDestinationImplementationRead.setWorkspaceId(
        destinationConnectionImplementation.getWorkspaceId());
    expectedDestinationImplementationRead.setDestinationImplementationId(
        destinationConnectionImplementation.getDestinationImplementationId());
    expectedDestinationImplementationRead.setConnectionConfiguration(
        destinationConnectionImplementation.getConfiguration());

    final DestinationImplementationIdRequestBody destinationImplementationIdRequestBody =
        new DestinationImplementationIdRequestBody();
    destinationImplementationIdRequestBody.setDestinationImplementationId(
        expectedDestinationImplementationRead.getDestinationImplementationId());

    final DestinationImplementationRead actualDestinationImplementationRead =
        destinationImplementationsHandler.getDestinationImplementation(
            destinationImplementationIdRequestBody);

    assertEquals(expectedDestinationImplementationRead, actualDestinationImplementationRead);
  }

  @Test
  void testListDestinationImplementationsForWorkspace() throws JsonValidationException {
    when(configPersistence.getConfigs(
            PersistenceConfigType.DESTINATION_CONNECTION_IMPLEMENTATION,
            DestinationConnectionImplementation.class))
        .thenReturn(Sets.newHashSet(destinationConnectionImplementation));

    DestinationImplementationRead expectedDestinationImplementationRead =
        new DestinationImplementationRead();
    expectedDestinationImplementationRead.setDestinationSpecificationId(
        destinationConnectionImplementation.getDestinationSpecificationId());
    expectedDestinationImplementationRead.setWorkspaceId(
        destinationConnectionImplementation.getWorkspaceId());
    expectedDestinationImplementationRead.setDestinationImplementationId(
        destinationConnectionImplementation.getDestinationImplementationId());
    expectedDestinationImplementationRead.setConnectionConfiguration(
        destinationConnectionImplementation.getConfiguration());

    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody();
    workspaceIdRequestBody.setWorkspaceId(destinationConnectionImplementation.getWorkspaceId());

    final DestinationImplementationReadList actualDestinationImplementationRead =
        destinationImplementationsHandler.listDestinationImplementationsForWorkspace(
            workspaceIdRequestBody);

    assertEquals(
        expectedDestinationImplementationRead,
        actualDestinationImplementationRead.getDestinations().get(0));
  }
}
