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
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.SourceConnectionSpecification;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.config.persistence.PersistenceConfigType;
import io.dataline.server.helpers.SourceSpecificationHelpers;
import io.dataline.server.validation.IntegrationSchemaValidation;
import java.io.File;
import java.io.IOException;
import java.util.UUID;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SourceImplementationsHandlerTest {
  private ConfigPersistence configPersistence;
  private SourceConnectionSpecification sourceConnectionSpecification;
  private SourceConnectionImplementation sourceConnectionImplementation;
  private SourceImplementationsHandler sourceImplementationsHandler;
  private IntegrationSchemaValidation validator;
  private Supplier<UUID> uuidGenerator;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setUp() {
    configPersistence = mock(ConfigPersistence.class);
    validator = mock(IntegrationSchemaValidation.class);
    uuidGenerator = mock(Supplier.class);

    sourceConnectionSpecification = SourceSpecificationHelpers.generateSourceSpecification();
    sourceConnectionImplementation =
        generateSourceImplementation(sourceConnectionSpecification.getSourceSpecificationId());

    sourceImplementationsHandler =
        new SourceImplementationsHandler(configPersistence, validator, uuidGenerator);
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

  private SourceConnectionImplementation generateSourceImplementation(UUID sourceSpecificationId) {
    final UUID workspaceId = UUID.randomUUID();
    final UUID sourceImplementationId = UUID.randomUUID();

    JsonNode implementationJson = getTestImplementationJson();

    final SourceConnectionImplementation sourceConnectionImplementation =
        new SourceConnectionImplementation();
    sourceConnectionImplementation.setWorkspaceId(workspaceId);
    sourceConnectionImplementation.setSourceSpecificationId(sourceSpecificationId);
    sourceConnectionImplementation.setSourceImplementationId(sourceImplementationId);
    sourceConnectionImplementation.setConfiguration(implementationJson.toString());

    return sourceConnectionImplementation;
  }

  @Test
  void testCreateSourceImplementation() throws JsonValidationException, ConfigNotFoundException {
    when(uuidGenerator.get())
        .thenReturn(sourceConnectionImplementation.getSourceImplementationId());

    when(configPersistence.getConfig(
            PersistenceConfigType.SOURCE_CONNECTION_IMPLEMENTATION,
            sourceConnectionImplementation.getSourceImplementationId().toString(),
            SourceConnectionImplementation.class))
        .thenReturn(sourceConnectionImplementation);

    final SourceImplementationCreate sourceImplementationCreate = new SourceImplementationCreate();
    sourceImplementationCreate.setWorkspaceId(sourceConnectionImplementation.getWorkspaceId());
    sourceImplementationCreate.setSourceSpecificationId(
        sourceConnectionSpecification.getSourceSpecificationId());
    sourceImplementationCreate.setConnectionConfiguration(getTestImplementationJson().toString());

    final SourceImplementationRead actualSourceImplementationRead =
        sourceImplementationsHandler.createSourceImplementation(sourceImplementationCreate);

    SourceImplementationRead expectedSourceImplementationRead = new SourceImplementationRead();
    expectedSourceImplementationRead.setSourceSpecificationId(
        sourceConnectionSpecification.getSourceSpecificationId());
    expectedSourceImplementationRead.setWorkspaceId(
        sourceConnectionImplementation.getWorkspaceId());
    expectedSourceImplementationRead.setSourceImplementationId(
        sourceConnectionImplementation.getSourceImplementationId());
    expectedSourceImplementationRead.setConnectionConfiguration(
        getTestImplementationJson().toString());

    assertEquals(expectedSourceImplementationRead, actualSourceImplementationRead);

    verify(validator)
        .validateSourceConnectionConfiguration(
            sourceConnectionSpecification.getSourceSpecificationId(),
            sourceConnectionImplementation.getConfiguration());

    verify(configPersistence)
        .writeConfig(
            PersistenceConfigType.SOURCE_CONNECTION_IMPLEMENTATION,
            sourceConnectionImplementation.getSourceImplementationId().toString(),
            sourceConnectionImplementation);
  }

  @Test
  void testUpdateSourceImplementation() throws JsonValidationException, ConfigNotFoundException {
    final Object configuration = sourceConnectionImplementation.getConfiguration();
    final JsonNode newConfiguration;
    try {
      newConfiguration = new ObjectMapper().readTree(configuration.toString());
    } catch (JsonProcessingException e) {
      throw new RuntimeException(e);
    }
    ((ObjectNode) newConfiguration).put("apiKey", "987-xyz");

    final SourceConnectionImplementation expectedSourceConnectionImplementation =
        new SourceConnectionImplementation();
    expectedSourceConnectionImplementation.setWorkspaceId(
        sourceConnectionImplementation.getWorkspaceId());
    expectedSourceConnectionImplementation.setSourceSpecificationId(
        sourceConnectionImplementation.getSourceSpecificationId());
    expectedSourceConnectionImplementation.setSourceImplementationId(
        sourceConnectionImplementation.getSourceImplementationId());
    expectedSourceConnectionImplementation.setConfiguration(newConfiguration.toString());

    when(configPersistence.getConfig(
            PersistenceConfigType.SOURCE_CONNECTION_IMPLEMENTATION,
            sourceConnectionImplementation.getSourceImplementationId().toString(),
            SourceConnectionImplementation.class))
        .thenReturn(sourceConnectionImplementation)
        .thenReturn(expectedSourceConnectionImplementation);

    final SourceImplementationUpdate sourceImplementationUpdate = new SourceImplementationUpdate();
    sourceImplementationUpdate.setSourceImplementationId(
        sourceConnectionImplementation.getSourceImplementationId());
    sourceImplementationUpdate.setConnectionConfiguration(newConfiguration.toString());
    final SourceImplementationRead actualSourceImplementationRead =
        sourceImplementationsHandler.updateSourceImplementation(sourceImplementationUpdate);

    SourceImplementationRead expectedSourceImplementationRead = new SourceImplementationRead();
    expectedSourceImplementationRead.setSourceSpecificationId(
        sourceConnectionSpecification.getSourceSpecificationId());
    expectedSourceImplementationRead.setWorkspaceId(
        sourceConnectionImplementation.getWorkspaceId());
    expectedSourceImplementationRead.setSourceImplementationId(
        sourceConnectionImplementation.getSourceImplementationId());
    expectedSourceImplementationRead.setConnectionConfiguration(newConfiguration.toString());

    assertEquals(expectedSourceImplementationRead, actualSourceImplementationRead);

    verify(configPersistence)
        .writeConfig(
            PersistenceConfigType.SOURCE_CONNECTION_IMPLEMENTATION,
            sourceConnectionImplementation.getSourceImplementationId().toString(),
            expectedSourceConnectionImplementation);
  }

  @Test
  void testGetSourceImplementation() throws JsonValidationException, ConfigNotFoundException {
    when(configPersistence.getConfig(
            PersistenceConfigType.SOURCE_CONNECTION_IMPLEMENTATION,
            sourceConnectionImplementation.getSourceImplementationId().toString(),
            SourceConnectionImplementation.class))
        .thenReturn(sourceConnectionImplementation);

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
  void testListSourceImplementationsForWorkspace() throws JsonValidationException {
    when(configPersistence.getConfigs(
            PersistenceConfigType.SOURCE_CONNECTION_IMPLEMENTATION,
            SourceConnectionImplementation.class))
        .thenReturn(Sets.newHashSet(sourceConnectionImplementation));

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
