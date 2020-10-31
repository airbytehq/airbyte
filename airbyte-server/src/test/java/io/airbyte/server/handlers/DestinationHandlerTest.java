/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.Lists;
import io.airbyte.api.model.ConnectionRead;
import io.airbyte.api.model.ConnectionReadList;
import io.airbyte.api.model.ConnectionStatus;
import io.airbyte.api.model.ConnectionUpdate;
import io.airbyte.api.model.DestinationCreate;
import io.airbyte.api.model.DestinationDefinitionIdRequestBody;
import io.airbyte.api.model.DestinationDefinitionSpecificationRead;
import io.airbyte.api.model.DestinationIdRequestBody;
import io.airbyte.api.model.DestinationRead;
import io.airbyte.api.model.DestinationReadList;
import io.airbyte.api.model.DestinationUpdate;
import io.airbyte.api.model.WorkspaceIdRequestBody;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationConnectionImplementation;
import io.airbyte.config.StandardDestination;
import io.airbyte.config.StandardSync;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.server.helpers.ConnectionHelpers;
import io.airbyte.server.helpers.ConnectorSpecificationHelpers;
import io.airbyte.server.helpers.DestinationDefinitionHelpers;
import io.airbyte.server.helpers.DestinationHelpers;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Collections;
import java.util.UUID;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DestinationHandlerTest {

  private ConfigRepository configRepository;
  private StandardDestination standardDestination;
  private DestinationDefinitionSpecificationRead destinationDefinitionSpecificationRead;
  private DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody;
  private DestinationConnectionImplementation destinationConnectionImplementation;
  private DestinationHandler destinationHandler;
  private ConnectionsHandler connectionsHandler;
  private SchedulerHandler schedulerHandler;

  private JsonSchemaValidator validator;
  private Supplier<UUID> uuidGenerator;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setUp() throws IOException {
    configRepository = mock(ConfigRepository.class);
    validator = mock(JsonSchemaValidator.class);
    uuidGenerator = mock(Supplier.class);
    connectionsHandler = mock(ConnectionsHandler.class);
    schedulerHandler = mock(SchedulerHandler.class);

    standardDestination = DestinationDefinitionHelpers.generateDestination();
    destinationDefinitionIdRequestBody = new DestinationDefinitionIdRequestBody().destinationDefinitionId(standardDestination.getDestinationId());
    ConnectorSpecification connectorSpecification = ConnectorSpecificationHelpers.generateConnectorSpecification();
    destinationDefinitionSpecificationRead = new DestinationDefinitionSpecificationRead()
        .connectionSpecification(connectorSpecification.getConnectionSpecification())
        .destinationDefinitionId(standardDestination.getDestinationId())
        .documentationUrl(connectorSpecification.getDocumentationUrl().toString());

    destinationConnectionImplementation = DestinationHelpers.generateDestination(standardDestination.getDestinationId());
    destinationHandler =
        new DestinationHandler(configRepository, validator, schedulerHandler, connectionsHandler, uuidGenerator);
  }

  @Test
  void testCreateDestination()
      throws JsonValidationException, ConfigNotFoundException, IOException {
    when(uuidGenerator.get())
        .thenReturn(destinationConnectionImplementation.getDestinationImplementationId());

    when(configRepository.getDestinationConnectionImplementation(destinationConnectionImplementation.getDestinationImplementationId()))
        .thenReturn(destinationConnectionImplementation);

    when(schedulerHandler.getDestinationSpecification(destinationDefinitionIdRequestBody)).thenReturn(destinationDefinitionSpecificationRead);

    when(configRepository.getStandardDestination(standardDestination.getDestinationId()))
        .thenReturn(standardDestination);

    final DestinationCreate destinationCreate = new DestinationCreate()
        .name(destinationConnectionImplementation.getName())
        .workspaceId(destinationConnectionImplementation.getWorkspaceId())
        .destinationDefinitionId(standardDestination.getDestinationId())
        .connectionConfiguration(DestinationHelpers.getTestDestinationJson());

    final DestinationRead actualDestinationRead =
        destinationHandler.createDestination(destinationCreate);

    DestinationRead expectedDestinationRead = new DestinationRead()
        .name(destinationConnectionImplementation.getName())
        .destinationDefinitionId(standardDestination.getDestinationId())
        .workspaceId(destinationConnectionImplementation.getWorkspaceId())
        .destinationId(destinationConnectionImplementation.getDestinationImplementationId())
        .connectionConfiguration(DestinationHelpers.getTestDestinationJson())
        .destinationName(standardDestination.getName());

    assertEquals(expectedDestinationRead, actualDestinationRead);

    verify(validator)
        .validate(
            destinationDefinitionSpecificationRead.getConnectionSpecification(),
            destinationConnectionImplementation.getConfiguration());

    verify(configRepository).writeDestinationConnectionImplementation(destinationConnectionImplementation);
  }

  @Test
  void testDeleteDestination() throws JsonValidationException, ConfigNotFoundException, IOException {
    final JsonNode newConfiguration = destinationConnectionImplementation.getConfiguration();
    ((ObjectNode) newConfiguration).put("apiKey", "987-xyz");

    final DestinationConnectionImplementation expectedDestinationConnectionImplementation = Jsons.clone(destinationConnectionImplementation)
        .withTombstone(true);

    when(configRepository.getDestinationConnectionImplementation(destinationConnectionImplementation.getDestinationImplementationId()))
        .thenReturn(destinationConnectionImplementation)
        .thenReturn(expectedDestinationConnectionImplementation);

    when(schedulerHandler.getDestinationSpecification(destinationDefinitionIdRequestBody)).thenReturn(destinationDefinitionSpecificationRead);
    when(configRepository.getStandardDestination(standardDestination.getDestinationId())).thenReturn(standardDestination);

    final DestinationIdRequestBody destinationId = new DestinationIdRequestBody()
        .destinationId(destinationConnectionImplementation.getDestinationImplementationId());

    final StandardSync standardSync =
        ConnectionHelpers.generateSyncWithDestinationImplId(destinationConnectionImplementation.getDestinationImplementationId());

    final ConnectionRead connectionRead = ConnectionHelpers.generateExpectedConnectionRead(standardSync);

    ConnectionReadList connectionReadList = new ConnectionReadList()
        .connections(Collections.singletonList(connectionRead));

    final WorkspaceIdRequestBody workspaceIdRequestBody =
        new WorkspaceIdRequestBody().workspaceId(destinationConnectionImplementation.getWorkspaceId());
    when(connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody)).thenReturn(connectionReadList);
    destinationHandler.deleteDestination(destinationId);

    verify(configRepository).writeDestinationConnectionImplementation(expectedDestinationConnectionImplementation);

    final ConnectionUpdate expectedConnectionUpdate = new ConnectionUpdate()
        .connectionId(connectionRead.getConnectionId())
        .status(ConnectionStatus.DEPRECATED)
        .syncSchema(connectionRead.getSyncSchema())
        .schedule(connectionRead.getSchedule());

    verify(connectionsHandler).listConnectionsForWorkspace(workspaceIdRequestBody);
    verify(connectionsHandler).updateConnection(expectedConnectionUpdate);
  }

  @Test
  void testUpdateDestination()
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final JsonNode newConfiguration = destinationConnectionImplementation.getConfiguration();

    ((ObjectNode) newConfiguration).put("apiKey", "987-xyz");

    final DestinationConnectionImplementation expectedDestinationConnectionImplementation = Jsons.clone(destinationConnectionImplementation)
        .withConfiguration(newConfiguration)
        .withTombstone(false);

    when(configRepository.getDestinationConnectionImplementation(destinationConnectionImplementation.getDestinationImplementationId()))
        .thenReturn(destinationConnectionImplementation)
        .thenReturn(expectedDestinationConnectionImplementation);

    when(schedulerHandler.getDestinationSpecification(destinationDefinitionIdRequestBody)).thenReturn(destinationDefinitionSpecificationRead);
    when(configRepository.getStandardDestination(standardDestination.getDestinationId())).thenReturn(standardDestination);

    final DestinationUpdate destinationUpdate = new DestinationUpdate()
        .destinationId(destinationConnectionImplementation.getDestinationImplementationId())
        .name(destinationConnectionImplementation.getName())
        .connectionConfiguration(newConfiguration);

    final DestinationRead actualDestinationRead =
        destinationHandler.updateDestination(destinationUpdate);

    DestinationRead expectedDestinationRead = new DestinationRead()
        .name(destinationConnectionImplementation.getName())
        .destinationDefinitionId(standardDestination.getDestinationId())
        .workspaceId(destinationConnectionImplementation.getWorkspaceId())
        .destinationId(destinationConnectionImplementation.getDestinationImplementationId())
        .connectionConfiguration(newConfiguration)
        .destinationName(standardDestination.getName());

    assertEquals(expectedDestinationRead, actualDestinationRead);

    verify(configRepository).writeDestinationConnectionImplementation(expectedDestinationConnectionImplementation);
  }

  @Test
  void testGetDestination() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(configRepository.getDestinationConnectionImplementation(destinationConnectionImplementation.getDestinationImplementationId()))
        .thenReturn(destinationConnectionImplementation);

    when(schedulerHandler.getDestinationSpecification(destinationDefinitionIdRequestBody)).thenReturn(destinationDefinitionSpecificationRead);
    when(configRepository.getStandardDestination(standardDestination.getDestinationId())).thenReturn(standardDestination);

    DestinationRead expectedDestinationRead = new DestinationRead()
        .name(destinationConnectionImplementation.getName())
        .destinationDefinitionId(standardDestination.getDestinationId())
        .workspaceId(destinationConnectionImplementation.getWorkspaceId())
        .destinationId(destinationConnectionImplementation.getDestinationImplementationId())
        .connectionConfiguration(destinationConnectionImplementation.getConfiguration())
        .destinationName(standardDestination.getName());

    final DestinationIdRequestBody destinationIdRequestBody = new DestinationIdRequestBody()
        .destinationId(expectedDestinationRead.getDestinationId());

    final DestinationRead actualDestinationRead =
        destinationHandler.getDestination(destinationIdRequestBody);

    assertEquals(expectedDestinationRead, actualDestinationRead);
  }

  @Test
  void testListDestinationForWorkspace()
      throws JsonValidationException, ConfigNotFoundException, IOException {
    when(configRepository.getDestinationConnectionImplementation(destinationConnectionImplementation.getDestinationImplementationId()))
        .thenReturn(destinationConnectionImplementation);
    when(configRepository.listDestinationConnectionImplementations())
        .thenReturn(Lists.newArrayList(destinationConnectionImplementation));
    when(schedulerHandler.getDestinationSpecification(destinationDefinitionIdRequestBody)).thenReturn(destinationDefinitionSpecificationRead);
    when(configRepository.getStandardDestination(standardDestination.getDestinationId())).thenReturn(standardDestination);

    DestinationRead expectedDestinationRead = new DestinationRead()
        .name(destinationConnectionImplementation.getName())
        .destinationDefinitionId(standardDestination.getDestinationId())
        .workspaceId(destinationConnectionImplementation.getWorkspaceId())
        .destinationId(destinationConnectionImplementation.getDestinationImplementationId())
        .connectionConfiguration(destinationConnectionImplementation.getConfiguration())
        .destinationName(standardDestination.getName());

    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody()
        .workspaceId(destinationConnectionImplementation.getWorkspaceId());

    final DestinationReadList actualDestinationRead =
        destinationHandler.listDestinationsForWorkspace(workspaceIdRequestBody);

    assertEquals(
        expectedDestinationRead,
        actualDestinationRead.getDestinations().get(0));
  }

}
