package io.dataline.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.dataline.api.model.*;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.SourceConnectionSpecification;
import io.dataline.config.persistence.ConfigPersistenceImpl;
import io.dataline.config.persistence.PersistenceConfigType;
import io.dataline.server.fixtures.SourceSpecificationFixtures;
import java.io.File;
import java.io.IOException;
import java.util.UUID;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SourceImplementationsHandlerTest {
  private ConfigPersistenceImpl configPersistence;
  private SourceConnectionSpecification sourceConnectionSpecification;
  private SourceConnectionImplementation sourceConnectionImplementation;
  private SourceImplementationsHandler sourceImplementationsHandler;

  @BeforeEach
  void setUp() {
    configPersistence = ConfigPersistenceImpl.getTest();
    sourceConnectionSpecification =
        SourceSpecificationFixtures.createSourceConnectionSpecification(configPersistence);
    sourceConnectionImplementation =
        createSourceImplementationMock(sourceConnectionSpecification.getSourceSpecificationId());

    sourceImplementationsHandler = new SourceImplementationsHandler(configPersistence);
  }

  @AfterEach
  void tearDown() {
    configPersistence.deleteAll();
  }

  private JsonNode getTestImplementationJson() {
    final File implementationFile =
        new File("../dataline-server/src/test/resources/json/TestImplementation.json");

    JsonNode implementationJson;
    try {
      return new ObjectMapper().readTree(implementationFile);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  private SourceConnectionImplementation createSourceImplementationMock(
      UUID sourceSpecificationId) {
    final UUID workspaceId = UUID.randomUUID();
    final UUID sourceImplementationId = UUID.randomUUID();

    JsonNode implementationJson = getTestImplementationJson();

    final SourceConnectionImplementation sourceConnectionImplementation =
        new SourceConnectionImplementation();
    sourceConnectionImplementation.setWorkspaceId(workspaceId);
    sourceConnectionImplementation.setSourceSpecificationId(sourceSpecificationId);
    sourceConnectionImplementation.setSourceImplementationId(sourceImplementationId);
    sourceConnectionImplementation.setConfiguration(implementationJson.toString());

    configPersistence.writeConfig(
        PersistenceConfigType.SOURCE_CONNECTION_IMPLEMENTATION,
        sourceImplementationId.toString(),
        sourceConnectionImplementation);

    return sourceConnectionImplementation;
  }

  @Test
  void createSourceImplementation() {
    final SourceImplementationCreate sourceImplementationCreate = new SourceImplementationCreate();
    final UUID workspaceId = UUID.randomUUID();
    sourceImplementationCreate.setWorkspaceId(workspaceId);
    sourceImplementationCreate.setSourceSpecificationId(
        sourceConnectionSpecification.getSourceSpecificationId());
    sourceImplementationCreate.setConnectionConfiguration(getTestImplementationJson().toString());

    final UUID sourceImplementationId =
        sourceImplementationsHandler
            .createSourceImplementation(sourceImplementationCreate)
            .getSourceImplementationId();

    SourceImplementationRead expectedSourceImplementationRead = new SourceImplementationRead();
    expectedSourceImplementationRead.setSourceSpecificationId(
        sourceConnectionSpecification.getSourceSpecificationId());
    expectedSourceImplementationRead.setWorkspaceId(workspaceId);
    expectedSourceImplementationRead.setSourceImplementationId(sourceImplementationId);
    expectedSourceImplementationRead.setConnectionConfiguration(
        getTestImplementationJson().toString());

    final SourceImplementationIdRequestBody sourceImplementationIdRequestBody =
        new SourceImplementationIdRequestBody();
    sourceImplementationIdRequestBody.setSourceImplementationId(sourceImplementationId);

    final SourceImplementationRead actualSourceImplementationRead =
        sourceImplementationsHandler.getSourceImplementation(sourceImplementationIdRequestBody);

    assertEquals(expectedSourceImplementationRead, actualSourceImplementationRead);
  }

  @Test
  void updateSourceImplementation() {
    final Object configuration = sourceConnectionImplementation.getConfiguration();
    final JsonNode newConfiguration;
    try {
      newConfiguration = new ObjectMapper().readTree(configuration.toString());
    } catch (JsonProcessingException e) {
      throw new RuntimeException(e);
    }
    ((ObjectNode) newConfiguration).put("apiKey", "987-xyz");

    final SourceImplementationUpdate sourceImplementationUpdate = new SourceImplementationUpdate();
    sourceImplementationUpdate.setSourceImplementationId(
        sourceConnectionImplementation.getSourceImplementationId());
    sourceImplementationUpdate.setConnectionConfiguration(newConfiguration.toString());
    sourceImplementationsHandler.updateSourceImplementation(sourceImplementationUpdate);

    SourceImplementationRead expectedSourceImplementationRead = new SourceImplementationRead();
    expectedSourceImplementationRead.setSourceSpecificationId(
        sourceConnectionSpecification.getSourceSpecificationId());
    expectedSourceImplementationRead.setWorkspaceId(
        sourceConnectionImplementation.getWorkspaceId());
    expectedSourceImplementationRead.setSourceImplementationId(
        sourceConnectionImplementation.getSourceImplementationId());
    expectedSourceImplementationRead.setConnectionConfiguration(newConfiguration.toString());

    final SourceImplementationIdRequestBody sourceImplementationIdRequestBody =
        new SourceImplementationIdRequestBody();
    sourceImplementationIdRequestBody.setSourceImplementationId(
        sourceConnectionImplementation.getSourceImplementationId());

    final SourceImplementationRead actualSourceImplementationRead =
        sourceImplementationsHandler.getSourceImplementation(sourceImplementationIdRequestBody);

    assertEquals(expectedSourceImplementationRead, actualSourceImplementationRead);
  }

  @Test
  void getSourceImplementation() {
    SourceImplementationRead expectedSourceImplementationRead = new SourceImplementationRead();
    expectedSourceImplementationRead.setSourceSpecificationId(
        sourceConnectionImplementation.getSourceSpecificationId());
    expectedSourceImplementationRead.setWorkspaceId(
        sourceConnectionImplementation.getWorkspaceId());
    expectedSourceImplementationRead.setSourceImplementationId(
        sourceConnectionImplementation.getSourceImplementationId());
    expectedSourceImplementationRead.setConnectionConfiguration(
        sourceConnectionImplementation.getConfiguration());

    final SourceImplementationIdRequestBody sourceImplementationIdRequestBody =
        new SourceImplementationIdRequestBody();
    sourceImplementationIdRequestBody.setSourceImplementationId(
        expectedSourceImplementationRead.getSourceImplementationId());

    final SourceImplementationRead actualSourceImplementationRead =
        sourceImplementationsHandler.getSourceImplementation(sourceImplementationIdRequestBody);

    assertEquals(expectedSourceImplementationRead, actualSourceImplementationRead);
  }

  @Test
  void listSourceImplementationsForWorkspace() {
    SourceImplementationRead expectedSourceImplementationRead = new SourceImplementationRead();
    expectedSourceImplementationRead.setSourceSpecificationId(
        sourceConnectionImplementation.getSourceSpecificationId());
    expectedSourceImplementationRead.setWorkspaceId(
        sourceConnectionImplementation.getWorkspaceId());
    expectedSourceImplementationRead.setSourceImplementationId(
        sourceConnectionImplementation.getSourceImplementationId());
    expectedSourceImplementationRead.setConnectionConfiguration(
        sourceConnectionImplementation.getConfiguration());

    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody();
    workspaceIdRequestBody.setWorkspaceId(sourceConnectionImplementation.getWorkspaceId());

    final SourceImplementationReadList actualSourceImplementationRead =
        sourceImplementationsHandler.listSourceImplementationsForWorkspace(workspaceIdRequestBody);

    assertEquals(
        expectedSourceImplementationRead, actualSourceImplementationRead.getSources().get(0));
  }
}
