/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.Lists;
import io.airbyte.api.model.generated.DestinationCloneConfiguration;
import io.airbyte.api.model.generated.DestinationCloneRequestBody;
import io.airbyte.api.model.generated.DestinationCreate;
import io.airbyte.api.model.generated.DestinationDefinitionSpecificationRead;
import io.airbyte.api.model.generated.DestinationIdRequestBody;
import io.airbyte.api.model.generated.DestinationRead;
import io.airbyte.api.model.generated.DestinationReadList;
import io.airbyte.api.model.generated.DestinationSearch;
import io.airbyte.api.model.generated.DestinationUpdate;
import io.airbyte.api.model.generated.WorkspaceIdRequestBody;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.server.converters.ConfigurationUpdate;
import io.airbyte.commons.server.helpers.ConnectorSpecificationHelpers;
import io.airbyte.commons.server.helpers.DestinationHelpers;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryReader;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.airbyte.persistence.job.factory.OAuthConfigSupplier;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.UUID;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DestinationHandlerTest {

  private ConfigRepository configRepository;
  private SecretsRepositoryReader secretsRepositoryReader;
  private SecretsRepositoryWriter secretsRepositoryWriter;
  private StandardDestinationDefinition standardDestinationDefinition;
  private DestinationDefinitionSpecificationRead destinationDefinitionSpecificationRead;
  private DestinationConnection destinationConnection;
  private DestinationHandler destinationHandler;
  private ConnectionsHandler connectionsHandler;
  private ConfigurationUpdate configurationUpdate;
  private JsonSchemaValidator validator;
  private Supplier<UUID> uuidGenerator;
  private JsonSecretsProcessor secretsProcessor;
  private ConnectorSpecification connectorSpecification;
  private OAuthConfigSupplier oAuthConfigSupplier;

  // needs to match name of file in src/test/resources/icons
  private static final String ICON = "test-destination.svg";
  private static final String LOADED_ICON = DestinationDefinitionsHandler.loadIcon(ICON);

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setUp() throws IOException {
    configRepository = mock(ConfigRepository.class);
    secretsRepositoryReader = mock(SecretsRepositoryReader.class);
    secretsRepositoryWriter = mock(SecretsRepositoryWriter.class);
    validator = mock(JsonSchemaValidator.class);
    uuidGenerator = mock(Supplier.class);
    connectionsHandler = mock(ConnectionsHandler.class);
    configurationUpdate = mock(ConfigurationUpdate.class);
    secretsProcessor = mock(JsonSecretsProcessor.class);
    oAuthConfigSupplier = mock(OAuthConfigSupplier.class);

    connectorSpecification = ConnectorSpecificationHelpers.generateConnectorSpecification();

    standardDestinationDefinition = new StandardDestinationDefinition()
        .withDestinationDefinitionId(UUID.randomUUID())
        .withName("db2")
        .withDockerRepository("thebestrepo")
        .withDockerImageTag("thelatesttag")
        .withDocumentationUrl("https://wikipedia.org")
        .withSpec(connectorSpecification)
        .withIcon(ICON);

    destinationDefinitionSpecificationRead = new DestinationDefinitionSpecificationRead()
        .connectionSpecification(connectorSpecification.getConnectionSpecification())
        .destinationDefinitionId(standardDestinationDefinition.getDestinationDefinitionId())
        .documentationUrl(connectorSpecification.getDocumentationUrl().toString());

    destinationConnection = DestinationHelpers.generateDestination(standardDestinationDefinition.getDestinationDefinitionId());

    destinationHandler =
        new DestinationHandler(configRepository,
            secretsRepositoryReader,
            secretsRepositoryWriter,
            validator,
            connectionsHandler,
            uuidGenerator,
            secretsProcessor,
            configurationUpdate,
            oAuthConfigSupplier);
  }

  @Test
  void testCreateDestination() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(uuidGenerator.get())
        .thenReturn(destinationConnection.getDestinationId());
    when(configRepository.getDestinationConnection(destinationConnection.getDestinationId()))
        .thenReturn(destinationConnection);
    when(configRepository.getStandardDestinationDefinition(standardDestinationDefinition.getDestinationDefinitionId()))
        .thenReturn(standardDestinationDefinition);
    when(oAuthConfigSupplier.maskDestinationOAuthParameters(destinationDefinitionSpecificationRead.getDestinationDefinitionId(),
        destinationConnection.getWorkspaceId(),
        destinationConnection.getConfiguration())).thenReturn(destinationConnection.getConfiguration());
    when(secretsProcessor.prepareSecretsForOutput(destinationConnection.getConfiguration(),
        destinationDefinitionSpecificationRead.getConnectionSpecification()))
            .thenReturn(destinationConnection.getConfiguration());

    final DestinationCreate destinationCreate = new DestinationCreate()
        .name(destinationConnection.getName())
        .workspaceId(destinationConnection.getWorkspaceId())
        .destinationDefinitionId(standardDestinationDefinition.getDestinationDefinitionId())
        .connectionConfiguration(DestinationHelpers.getTestDestinationJson());

    final DestinationRead actualDestinationRead =
        destinationHandler.createDestination(destinationCreate);

    final DestinationRead expectedDestinationRead = new DestinationRead()
        .name(destinationConnection.getName())
        .destinationDefinitionId(standardDestinationDefinition.getDestinationDefinitionId())
        .workspaceId(destinationConnection.getWorkspaceId())
        .destinationId(destinationConnection.getDestinationId())
        .connectionConfiguration(DestinationHelpers.getTestDestinationJson())
        .destinationName(standardDestinationDefinition.getName())
        .icon(LOADED_ICON);

    assertEquals(expectedDestinationRead, actualDestinationRead);

    verify(validator).ensure(destinationDefinitionSpecificationRead.getConnectionSpecification(), destinationConnection.getConfiguration());
    verify(secretsRepositoryWriter).writeDestinationConnection(destinationConnection, connectorSpecification);
    verify(oAuthConfigSupplier).maskDestinationOAuthParameters(destinationDefinitionSpecificationRead.getDestinationDefinitionId(),
        destinationConnection.getWorkspaceId(), destinationConnection.getConfiguration());
    verify(secretsProcessor)
        .prepareSecretsForOutput(destinationConnection.getConfiguration(), destinationDefinitionSpecificationRead.getConnectionSpecification());
  }

  @Test
  void testUpdateDestination() throws JsonValidationException, ConfigNotFoundException, IOException {
    final String updatedDestName = "my updated dest name";
    final JsonNode newConfiguration = destinationConnection.getConfiguration();
    ((ObjectNode) newConfiguration).put("apiKey", "987-xyz");

    final DestinationConnection expectedDestinationConnection = Jsons.clone(destinationConnection)
        .withName(updatedDestName)
        .withConfiguration(newConfiguration)
        .withTombstone(false);

    final DestinationUpdate destinationUpdate = new DestinationUpdate()
        .name(updatedDestName)
        .destinationId(destinationConnection.getDestinationId())
        .connectionConfiguration(newConfiguration);

    when(secretsProcessor
        .copySecrets(destinationConnection.getConfiguration(), newConfiguration, destinationDefinitionSpecificationRead.getConnectionSpecification()))
            .thenReturn(newConfiguration);
    when(secretsProcessor.prepareSecretsForOutput(newConfiguration, destinationDefinitionSpecificationRead.getConnectionSpecification()))
        .thenReturn(newConfiguration);
    when(oAuthConfigSupplier.maskDestinationOAuthParameters(destinationDefinitionSpecificationRead.getDestinationDefinitionId(),
        destinationConnection.getWorkspaceId(),
        newConfiguration)).thenReturn(newConfiguration);
    when(configRepository.getStandardDestinationDefinition(standardDestinationDefinition.getDestinationDefinitionId()))
        .thenReturn(standardDestinationDefinition);
    when(configRepository.getDestinationDefinitionFromDestination(destinationConnection.getDestinationId()))
        .thenReturn(standardDestinationDefinition);
    when(configRepository.getDestinationConnection(destinationConnection.getDestinationId()))
        .thenReturn(expectedDestinationConnection);
    when(configurationUpdate.destination(destinationConnection.getDestinationId(), updatedDestName, newConfiguration))
        .thenReturn(expectedDestinationConnection);

    final DestinationRead actualDestinationRead = destinationHandler.updateDestination(destinationUpdate);

    final DestinationRead expectedDestinationRead = DestinationHelpers
        .getDestinationRead(expectedDestinationConnection, standardDestinationDefinition).connectionConfiguration(newConfiguration);

    assertEquals(expectedDestinationRead, actualDestinationRead);

    verify(secretsProcessor).prepareSecretsForOutput(newConfiguration, destinationDefinitionSpecificationRead.getConnectionSpecification());
    verify(secretsRepositoryWriter).writeDestinationConnection(expectedDestinationConnection, connectorSpecification);
    verify(oAuthConfigSupplier).maskDestinationOAuthParameters(destinationDefinitionSpecificationRead.getDestinationDefinitionId(),
        destinationConnection.getWorkspaceId(), newConfiguration);
    verify(validator).ensure(destinationDefinitionSpecificationRead.getConnectionSpecification(), newConfiguration);
  }

  @Test
  void testGetDestination() throws JsonValidationException, ConfigNotFoundException, IOException {
    final DestinationRead expectedDestinationRead = new DestinationRead()
        .name(destinationConnection.getName())
        .destinationDefinitionId(standardDestinationDefinition.getDestinationDefinitionId())
        .workspaceId(destinationConnection.getWorkspaceId())
        .destinationId(destinationConnection.getDestinationId())
        .connectionConfiguration(destinationConnection.getConfiguration())
        .destinationName(standardDestinationDefinition.getName())
        .icon(LOADED_ICON);
    final DestinationIdRequestBody destinationIdRequestBody =
        new DestinationIdRequestBody().destinationId(expectedDestinationRead.getDestinationId());

    when(secretsProcessor.prepareSecretsForOutput(destinationConnection.getConfiguration(),
        destinationDefinitionSpecificationRead.getConnectionSpecification()))
            .thenReturn(destinationConnection.getConfiguration());
    when(configRepository.getDestinationConnection(destinationConnection.getDestinationId())).thenReturn(destinationConnection);
    when(configRepository.getStandardDestinationDefinition(standardDestinationDefinition.getDestinationDefinitionId()))
        .thenReturn(standardDestinationDefinition);

    final DestinationRead actualDestinationRead = destinationHandler.getDestination(destinationIdRequestBody);

    assertEquals(expectedDestinationRead, actualDestinationRead);

    // make sure the icon was loaded into actual svg content
    assertTrue(expectedDestinationRead.getIcon().startsWith("<svg>"));

    verify(secretsProcessor)
        .prepareSecretsForOutput(destinationConnection.getConfiguration(), destinationDefinitionSpecificationRead.getConnectionSpecification());
  }

  @Test
  void testListDestinationForWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
    final DestinationRead expectedDestinationRead = new DestinationRead()
        .name(destinationConnection.getName())
        .destinationDefinitionId(standardDestinationDefinition.getDestinationDefinitionId())
        .workspaceId(destinationConnection.getWorkspaceId())
        .destinationId(destinationConnection.getDestinationId())
        .connectionConfiguration(destinationConnection.getConfiguration())
        .destinationName(standardDestinationDefinition.getName())
        .icon(LOADED_ICON);
    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody().workspaceId(destinationConnection.getWorkspaceId());

    when(configRepository.getDestinationConnection(destinationConnection.getDestinationId())).thenReturn(destinationConnection);
    when(configRepository.listWorkspaceDestinationConnection(destinationConnection.getWorkspaceId()))
        .thenReturn(Lists.newArrayList(destinationConnection));
    when(configRepository.getStandardDestinationDefinition(standardDestinationDefinition.getDestinationDefinitionId()))
        .thenReturn(standardDestinationDefinition);
    when(secretsProcessor.prepareSecretsForOutput(destinationConnection.getConfiguration(),
        destinationDefinitionSpecificationRead.getConnectionSpecification()))
            .thenReturn(destinationConnection.getConfiguration());

    final DestinationReadList actualDestinationRead = destinationHandler.listDestinationsForWorkspace(workspaceIdRequestBody);

    assertEquals(expectedDestinationRead, actualDestinationRead.getDestinations().get(0));
    verify(secretsProcessor)
        .prepareSecretsForOutput(destinationConnection.getConfiguration(), destinationDefinitionSpecificationRead.getConnectionSpecification());
  }

  @Test
  void testSearchDestinations() throws JsonValidationException, ConfigNotFoundException, IOException {
    final DestinationRead expectedDestinationRead = new DestinationRead()
        .name(destinationConnection.getName())
        .destinationDefinitionId(standardDestinationDefinition.getDestinationDefinitionId())
        .workspaceId(destinationConnection.getWorkspaceId())
        .destinationId(destinationConnection.getDestinationId())
        .connectionConfiguration(destinationConnection.getConfiguration())
        .destinationName(standardDestinationDefinition.getName())
        .icon(LOADED_ICON);

    when(configRepository.getDestinationConnection(destinationConnection.getDestinationId())).thenReturn(destinationConnection);
    when(configRepository.listDestinationConnection()).thenReturn(Lists.newArrayList(destinationConnection));
    when(configRepository.getStandardDestinationDefinition(standardDestinationDefinition.getDestinationDefinitionId()))
        .thenReturn(standardDestinationDefinition);
    when(secretsProcessor.prepareSecretsForOutput(destinationConnection.getConfiguration(),
        destinationDefinitionSpecificationRead.getConnectionSpecification()))
            .thenReturn(destinationConnection.getConfiguration());

    when(connectionsHandler.matchSearch(new DestinationSearch(), expectedDestinationRead)).thenReturn(true);
    DestinationReadList actualDestinationRead = destinationHandler.searchDestinations(new DestinationSearch());
    assertEquals(1, actualDestinationRead.getDestinations().size());
    assertEquals(expectedDestinationRead, actualDestinationRead.getDestinations().get(0));
    verify(secretsProcessor)
        .prepareSecretsForOutput(destinationConnection.getConfiguration(), destinationDefinitionSpecificationRead.getConnectionSpecification());

    when(connectionsHandler.matchSearch(new DestinationSearch(), expectedDestinationRead)).thenReturn(false);
    actualDestinationRead = destinationHandler.searchDestinations(new DestinationSearch());
    assertEquals(0, actualDestinationRead.getDestinations().size());
  }

  @Test
  void testCloneDestinationWithConfiguration() throws JsonValidationException, ConfigNotFoundException, IOException {
    final DestinationConnection clonedConnection = DestinationHelpers.generateDestination(standardDestinationDefinition.getDestinationDefinitionId());
    final DestinationRead expectedDestinationRead = new DestinationRead()
        .name(clonedConnection.getName())
        .destinationDefinitionId(standardDestinationDefinition.getDestinationDefinitionId())
        .workspaceId(clonedConnection.getWorkspaceId())
        .destinationId(clonedConnection.getDestinationId())
        .connectionConfiguration(clonedConnection.getConfiguration())
        .destinationName(standardDestinationDefinition.getName())
        .icon(LOADED_ICON);
    final DestinationRead destinationRead = new DestinationRead()
        .name(destinationConnection.getName())
        .destinationDefinitionId(standardDestinationDefinition.getDestinationDefinitionId())
        .workspaceId(destinationConnection.getWorkspaceId())
        .destinationId(destinationConnection.getDestinationId())
        .connectionConfiguration(destinationConnection.getConfiguration())
        .destinationName(standardDestinationDefinition.getName());

    final DestinationCloneConfiguration destinationCloneConfiguration = new DestinationCloneConfiguration().name("Copy Name");
    final DestinationCloneRequestBody destinationCloneRequestBody = new DestinationCloneRequestBody()
        .destinationCloneId(destinationRead.getDestinationId()).destinationConfiguration(destinationCloneConfiguration);

    when(uuidGenerator.get()).thenReturn(clonedConnection.getDestinationId());
    when(secretsRepositoryReader.getDestinationConnectionWithSecrets(destinationConnection.getDestinationId())).thenReturn(destinationConnection);
    when(configRepository.getDestinationConnection(clonedConnection.getDestinationId())).thenReturn(clonedConnection);

    when(configRepository.getStandardDestinationDefinition(destinationDefinitionSpecificationRead.getDestinationDefinitionId()))
        .thenReturn(standardDestinationDefinition);
    when(configRepository.getDestinationDefinitionFromDestination(destinationConnection.getDestinationId()))
        .thenReturn(standardDestinationDefinition);
    when(secretsProcessor.prepareSecretsForOutput(destinationConnection.getConfiguration(),
        destinationDefinitionSpecificationRead.getConnectionSpecification()))
            .thenReturn(destinationConnection.getConfiguration());

    final DestinationRead actualDestinationRead = destinationHandler.cloneDestination(destinationCloneRequestBody);

    assertEquals(expectedDestinationRead, actualDestinationRead);
  }

  @Test
  void testCloneDestinationWithoutConfiguration() throws JsonValidationException, ConfigNotFoundException, IOException {
    final DestinationConnection clonedConnection = DestinationHelpers.generateDestination(standardDestinationDefinition.getDestinationDefinitionId());
    final DestinationRead expectedDestinationRead = new DestinationRead()
        .name(clonedConnection.getName())
        .destinationDefinitionId(standardDestinationDefinition.getDestinationDefinitionId())
        .workspaceId(clonedConnection.getWorkspaceId())
        .destinationId(clonedConnection.getDestinationId())
        .connectionConfiguration(clonedConnection.getConfiguration())
        .destinationName(standardDestinationDefinition.getName())
        .icon(LOADED_ICON);
    final DestinationRead destinationRead = new DestinationRead()
        .name(destinationConnection.getName())
        .destinationDefinitionId(standardDestinationDefinition.getDestinationDefinitionId())
        .workspaceId(destinationConnection.getWorkspaceId())
        .destinationId(destinationConnection.getDestinationId())
        .connectionConfiguration(destinationConnection.getConfiguration())
        .destinationName(standardDestinationDefinition.getName());

    final DestinationCloneRequestBody destinationCloneRequestBody =
        new DestinationCloneRequestBody().destinationCloneId(destinationRead.getDestinationId());

    when(uuidGenerator.get()).thenReturn(clonedConnection.getDestinationId());
    when(secretsRepositoryReader.getDestinationConnectionWithSecrets(destinationConnection.getDestinationId())).thenReturn(destinationConnection);
    when(configRepository.getDestinationConnection(clonedConnection.getDestinationId())).thenReturn(clonedConnection);

    when(configRepository.getStandardDestinationDefinition(destinationDefinitionSpecificationRead.getDestinationDefinitionId()))
        .thenReturn(standardDestinationDefinition);
    when(configRepository.getDestinationDefinitionFromDestination(destinationConnection.getDestinationId()))
        .thenReturn(standardDestinationDefinition);
    when(secretsProcessor.prepareSecretsForOutput(destinationConnection.getConfiguration(),
        destinationDefinitionSpecificationRead.getConnectionSpecification()))
            .thenReturn(destinationConnection.getConfiguration());

    final DestinationRead actualDestinationRead = destinationHandler.cloneDestination(destinationCloneRequestBody);

    assertEquals(expectedDestinationRead, actualDestinationRead);
  }

}
