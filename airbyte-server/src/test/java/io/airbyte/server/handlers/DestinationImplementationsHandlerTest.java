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
import io.airbyte.api.model.DestinationIdRequestBody;
import io.airbyte.api.model.DestinationImplementationCreate;
import io.airbyte.api.model.DestinationImplementationIdRequestBody;
import io.airbyte.api.model.DestinationImplementationRead;
import io.airbyte.api.model.DestinationImplementationReadList;
import io.airbyte.api.model.DestinationImplementationUpdate;
import io.airbyte.api.model.DestinationSpecificationRead;
import io.airbyte.api.model.WorkspaceIdRequestBody;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConnectorSpecification;
import io.airbyte.config.DestinationConnectionImplementation;
import io.airbyte.config.StandardDestination;
import io.airbyte.config.StandardSync;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.server.helpers.ConnectionHelpers;
import io.airbyte.server.helpers.ConnectorSpecificationHelpers;
import io.airbyte.server.helpers.DestinationHelpers;
import io.airbyte.server.helpers.DestinationImplementationHelpers;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Collections;
import java.util.UUID;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DestinationImplementationsHandlerTest {

  private ConfigRepository configRepository;
  private StandardDestination standardDestination;
  private DestinationSpecificationRead destinationSpecificationRead;
  private DestinationIdRequestBody destinationIdRequestBody;
  private DestinationConnectionImplementation destinationConnectionImplementation;
  private DestinationImplementationsHandler destinationImplementationsHandler;
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

    standardDestination = DestinationHelpers.generateDestination();
    destinationIdRequestBody = new DestinationIdRequestBody().destinationId(standardDestination.getDestinationId());
    ConnectorSpecification connectorSpecification = ConnectorSpecificationHelpers.generateConnectorSpecification();
    destinationSpecificationRead = new DestinationSpecificationRead()
        .connectionSpecification(connectorSpecification.getConnectionSpecification())
        .destinationId(standardDestination.getDestinationId())
        .documentationUrl(connectorSpecification.getDocumentationUrl().toString());

    destinationConnectionImplementation = DestinationImplementationHelpers.generateDestinationImplementation(standardDestination.getDestinationId());
    destinationImplementationsHandler =
        new DestinationImplementationsHandler(configRepository, validator, schedulerHandler, connectionsHandler, uuidGenerator);
  }

  @Test
  void testCreateDestinationImplementation()
      throws JsonValidationException, ConfigNotFoundException, IOException {
    when(uuidGenerator.get())
        .thenReturn(destinationConnectionImplementation.getDestinationImplementationId());

    when(configRepository.getDestinationConnectionImplementation(destinationConnectionImplementation.getDestinationImplementationId()))
        .thenReturn(destinationConnectionImplementation);

    when(schedulerHandler.getDestinationSpecification(destinationIdRequestBody)).thenReturn(destinationSpecificationRead);

    when(configRepository.getStandardDestination(standardDestination.getDestinationId()))
        .thenReturn(standardDestination);

    final DestinationImplementationCreate destinationImplementationCreate = new DestinationImplementationCreate()
        .name(destinationConnectionImplementation.getName())
        .workspaceId(destinationConnectionImplementation.getWorkspaceId())
        .destinationId(standardDestination.getDestinationId())
        .connectionConfiguration(DestinationImplementationHelpers.getTestImplementationJson());

    final DestinationImplementationRead actualDestinationImplementationRead =
        destinationImplementationsHandler.createDestinationImplementation(destinationImplementationCreate);

    DestinationImplementationRead expectedDestinationImplementationRead = new DestinationImplementationRead()
        .name(destinationConnectionImplementation.getName())
        .destinationId(standardDestination.getDestinationId())
        .workspaceId(destinationConnectionImplementation.getWorkspaceId())
        .destinationImplementationId(destinationConnectionImplementation.getDestinationImplementationId())
        .connectionConfiguration(DestinationImplementationHelpers.getTestImplementationJson())
        .destinationName(standardDestination.getName());

    assertEquals(expectedDestinationImplementationRead, actualDestinationImplementationRead);

    verify(validator)
        .validate(
            destinationSpecificationRead.getConnectionSpecification(),
            destinationConnectionImplementation.getConfiguration());

    verify(configRepository).writeDestinationConnectionImplementation(destinationConnectionImplementation);
  }

  @Test
  void testDeleteDestinationImplementation() throws JsonValidationException, ConfigNotFoundException, IOException {
    final JsonNode newConfiguration = destinationConnectionImplementation.getConfiguration();
    ((ObjectNode) newConfiguration).put("apiKey", "987-xyz");

    final DestinationConnectionImplementation expectedDestinationConnectionImplementation = Jsons.clone(destinationConnectionImplementation)
        .withTombstone(true);

    when(configRepository.getDestinationConnectionImplementation(destinationConnectionImplementation.getDestinationImplementationId()))
        .thenReturn(destinationConnectionImplementation)
        .thenReturn(expectedDestinationConnectionImplementation);

    when(schedulerHandler.getDestinationSpecification(destinationIdRequestBody)).thenReturn(destinationSpecificationRead);
    when(configRepository.getStandardDestination(standardDestination.getDestinationId())).thenReturn(standardDestination);

    final DestinationImplementationIdRequestBody destinationImplementationId = new DestinationImplementationIdRequestBody()
        .destinationImplementationId(destinationConnectionImplementation.getDestinationImplementationId());

    final StandardSync standardSync =
        ConnectionHelpers.generateSyncWithDestinationImplId(destinationConnectionImplementation.getDestinationImplementationId());

    final ConnectionRead connectionRead = ConnectionHelpers.generateExpectedConnectionRead(standardSync);

    ConnectionReadList connectionReadList = new ConnectionReadList()
        .connections(Collections.singletonList(connectionRead));

    final WorkspaceIdRequestBody workspaceIdRequestBody =
        new WorkspaceIdRequestBody().workspaceId(destinationConnectionImplementation.getWorkspaceId());
    when(connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody)).thenReturn(connectionReadList);
    destinationImplementationsHandler.deleteDestinationImplementation(destinationImplementationId);

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
  void testUpdateDestinationImplementation()
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final JsonNode newConfiguration = destinationConnectionImplementation.getConfiguration();

    ((ObjectNode) newConfiguration).put("apiKey", "987-xyz");

    final DestinationConnectionImplementation expectedDestinationConnectionImplementation = Jsons.clone(destinationConnectionImplementation)
        .withConfiguration(newConfiguration)
        .withTombstone(false);

    when(configRepository.getDestinationConnectionImplementation(destinationConnectionImplementation.getDestinationImplementationId()))
        .thenReturn(destinationConnectionImplementation)
        .thenReturn(expectedDestinationConnectionImplementation);

    when(schedulerHandler.getDestinationSpecification(destinationIdRequestBody)).thenReturn(destinationSpecificationRead);
    when(configRepository.getStandardDestination(standardDestination.getDestinationId())).thenReturn(standardDestination);

    final DestinationImplementationUpdate destinationImplementationUpdate = new DestinationImplementationUpdate()
        .destinationImplementationId(destinationConnectionImplementation.getDestinationImplementationId())
        .name(destinationConnectionImplementation.getName())
        .connectionConfiguration(newConfiguration);

    final DestinationImplementationRead actualDestinationImplementationRead =
        destinationImplementationsHandler.updateDestinationImplementation(destinationImplementationUpdate);

    DestinationImplementationRead expectedDestinationImplementationRead = new DestinationImplementationRead()
        .name(destinationConnectionImplementation.getName())
        .destinationId(standardDestination.getDestinationId())
        .workspaceId(destinationConnectionImplementation.getWorkspaceId())
        .destinationImplementationId(destinationConnectionImplementation.getDestinationImplementationId())
        .connectionConfiguration(newConfiguration)
        .destinationName(standardDestination.getName());

    assertEquals(expectedDestinationImplementationRead, actualDestinationImplementationRead);

    verify(configRepository).writeDestinationConnectionImplementation(expectedDestinationConnectionImplementation);
  }

  @Test
  void testGetDestinationImplementation() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(configRepository.getDestinationConnectionImplementation(destinationConnectionImplementation.getDestinationImplementationId()))
        .thenReturn(destinationConnectionImplementation);

    when(schedulerHandler.getDestinationSpecification(destinationIdRequestBody)).thenReturn(destinationSpecificationRead);
    when(configRepository.getStandardDestination(standardDestination.getDestinationId())).thenReturn(standardDestination);

    DestinationImplementationRead expectedDestinationImplementationRead = new DestinationImplementationRead()
        .name(destinationConnectionImplementation.getName())
        .destinationId(standardDestination.getDestinationId())
        .workspaceId(destinationConnectionImplementation.getWorkspaceId())
        .destinationImplementationId(destinationConnectionImplementation.getDestinationImplementationId())
        .connectionConfiguration(destinationConnectionImplementation.getConfiguration())
        .destinationName(standardDestination.getName());

    final DestinationImplementationIdRequestBody destinationImplementationIdRequestBody = new DestinationImplementationIdRequestBody()
        .destinationImplementationId(expectedDestinationImplementationRead.getDestinationImplementationId());

    final DestinationImplementationRead actualDestinationImplementationRead =
        destinationImplementationsHandler.getDestinationImplementation(destinationImplementationIdRequestBody);

    assertEquals(expectedDestinationImplementationRead, actualDestinationImplementationRead);
  }

  @Test
  void testListDestinationImplementationsForWorkspace()
      throws JsonValidationException, ConfigNotFoundException, IOException {
    when(configRepository.getDestinationConnectionImplementation(destinationConnectionImplementation.getDestinationImplementationId()))
        .thenReturn(destinationConnectionImplementation);
    when(configRepository.listDestinationConnectionImplementations())
        .thenReturn(Lists.newArrayList(destinationConnectionImplementation));
    when(schedulerHandler.getDestinationSpecification(destinationIdRequestBody)).thenReturn(destinationSpecificationRead);
    when(configRepository.getStandardDestination(standardDestination.getDestinationId())).thenReturn(standardDestination);

    DestinationImplementationRead expectedDestinationImplementationRead = new DestinationImplementationRead()
        .name(destinationConnectionImplementation.getName())
        .destinationId(standardDestination.getDestinationId())
        .workspaceId(destinationConnectionImplementation.getWorkspaceId())
        .destinationImplementationId(destinationConnectionImplementation.getDestinationImplementationId())
        .connectionConfiguration(destinationConnectionImplementation.getConfiguration())
        .destinationName(standardDestination.getName());

    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody()
        .workspaceId(destinationConnectionImplementation.getWorkspaceId());

    final DestinationImplementationReadList actualDestinationImplementationRead =
        destinationImplementationsHandler.listDestinationImplementationsForWorkspace(workspaceIdRequestBody);

    assertEquals(
        expectedDestinationImplementationRead,
        actualDestinationImplementationRead.getDestinations().get(0));
  }

}
