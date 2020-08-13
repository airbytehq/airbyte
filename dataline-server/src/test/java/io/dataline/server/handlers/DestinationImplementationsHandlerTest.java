package io.dataline.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.dataline.api.model.*;
import io.dataline.config.DestinationConnectionImplementation;
import io.dataline.config.DestinationConnectionSpecification;
import io.dataline.config.persistence.ConfigPersistenceImpl;
import io.dataline.config.persistence.PersistenceConfigType;
import io.dataline.server.fixtures.DestinationSpecificationFixtures;
import java.io.File;
import java.io.IOException;
import java.util.UUID;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DestinationImplementationsHandlerTest {
  private ConfigPersistenceImpl configPersistence;
  private DestinationConnectionSpecification destinationConnectionSpecification;
  private DestinationConnectionImplementation destinationConnectionImplementation;
  private DestinationImplementationsHandler destinationImplementationsHandler;

  @BeforeEach
  void setUp() {
    configPersistence = ConfigPersistenceImpl.getTest();
    destinationConnectionSpecification =
        DestinationSpecificationFixtures.createDestinationConnectionSpecification(
            configPersistence);
    destinationConnectionImplementation =
        createDestinationImplementationMock(
            destinationConnectionSpecification.getDestinationSpecificationId());

    destinationImplementationsHandler = new DestinationImplementationsHandler(configPersistence);
  }

  @AfterEach
  void tearDown() {
    configPersistence.deleteAll();
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

  private DestinationConnectionImplementation createDestinationImplementationMock(
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

    configPersistence.writeConfig(
        PersistenceConfigType.DESTINATION_CONNECTION_IMPLEMENTATION,
        destinationImplementationId.toString(),
        destinationConnectionImplementation);

    return destinationConnectionImplementation;
  }

  @Test
  void createDestinationImplementation() {
    final DestinationImplementationCreate destinationImplementationCreate =
        new DestinationImplementationCreate();
    final UUID workspaceId = UUID.randomUUID();
    destinationImplementationCreate.setWorkspaceId(workspaceId);
    destinationImplementationCreate.setDestinationSpecificationId(
        destinationConnectionSpecification.getDestinationSpecificationId());
    destinationImplementationCreate.setConnectionConfiguration(
        getTestImplementationJson().toString());

    final UUID destinationImplementationId =
        destinationImplementationsHandler
            .createDestinationImplementation(destinationImplementationCreate)
            .getDestinationImplementationId();

    DestinationImplementationRead expectedDestinationImplementationRead =
        new DestinationImplementationRead();
    expectedDestinationImplementationRead.setDestinationSpecificationId(
        destinationConnectionSpecification.getDestinationSpecificationId());
    expectedDestinationImplementationRead.setWorkspaceId(workspaceId);
    expectedDestinationImplementationRead.setDestinationImplementationId(
        destinationImplementationId);
    expectedDestinationImplementationRead.setConnectionConfiguration(
        getTestImplementationJson().toString());

    final DestinationImplementationIdRequestBody destinationImplementationIdRequestBody =
        new DestinationImplementationIdRequestBody();
    destinationImplementationIdRequestBody.setDestinationImplementationId(
        destinationImplementationId);

    final DestinationImplementationRead actualDestinationImplementationRead =
        destinationImplementationsHandler.getDestinationImplementation(
            destinationImplementationIdRequestBody);

    assertEquals(expectedDestinationImplementationRead, actualDestinationImplementationRead);
  }

  @Test
  void updateDestinationImplementation() {
    final Object configuration = destinationConnectionImplementation.getConfiguration();
    final JsonNode newConfiguration;
    try {
      newConfiguration = new ObjectMapper().readTree(configuration.toString());
    } catch (JsonProcessingException e) {
      throw new RuntimeException(e);
    }
    ((ObjectNode) newConfiguration).put("apiKey", "987-xyz");

    final DestinationImplementationUpdate destinationImplementationUpdate =
        new DestinationImplementationUpdate();
    destinationImplementationUpdate.setDestinationImplementationId(
        destinationConnectionImplementation.getDestinationImplementationId());
    destinationImplementationUpdate.setConnectionConfiguration(newConfiguration.toString());
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

    final DestinationImplementationIdRequestBody destinationImplementationIdRequestBody =
        new DestinationImplementationIdRequestBody();
    destinationImplementationIdRequestBody.setDestinationImplementationId(
        destinationConnectionImplementation.getDestinationImplementationId());

    final DestinationImplementationRead actualDestinationImplementationRead =
        destinationImplementationsHandler.getDestinationImplementation(
            destinationImplementationIdRequestBody);

    assertEquals(expectedDestinationImplementationRead, actualDestinationImplementationRead);
  }

  @Test
  void getDestinationImplementation() {
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
  void listDestinationImplementationsForWorkspace() {
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
