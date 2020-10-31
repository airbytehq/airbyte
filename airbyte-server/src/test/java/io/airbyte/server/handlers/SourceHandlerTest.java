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
import io.airbyte.api.model.SourceCreate;
import io.airbyte.api.model.SourceDefinitionIdRequestBody;
import io.airbyte.api.model.SourceDefinitionSpecificationRead;
import io.airbyte.api.model.SourceIdRequestBody;
import io.airbyte.api.model.SourceRead;
import io.airbyte.api.model.SourceReadList;
import io.airbyte.api.model.SourceUpdate;
import io.airbyte.api.model.WorkspaceIdRequestBody;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.SourceConnectionImplementation;
import io.airbyte.config.StandardSource;
import io.airbyte.config.StandardSync;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.server.helpers.ConnectionHelpers;
import io.airbyte.server.helpers.ConnectorSpecificationHelpers;
import io.airbyte.server.helpers.SourceDefinitionHelpers;
import io.airbyte.server.helpers.SourceHelpers;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Collections;
import java.util.UUID;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SourceHandlerTest {

  private ConfigRepository configRepository;
  private StandardSource standardSource;
  private SourceDefinitionSpecificationRead sourceDefinitionSpecificationRead;
  private SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody;
  private SourceConnectionImplementation sourceConnectionImplementation;
  private SourceHandler sourceHandler;
  private JsonSchemaValidator validator;
  private ConnectionsHandler connectionsHandler;
  private SchedulerHandler schedulerHandler;
  private Supplier<UUID> uuidGenerator;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setUp() throws IOException {
    configRepository = mock(ConfigRepository.class);
    validator = mock(JsonSchemaValidator.class);
    connectionsHandler = mock(ConnectionsHandler.class);
    schedulerHandler = mock(SchedulerHandler.class);
    uuidGenerator = mock(Supplier.class);

    standardSource = SourceDefinitionHelpers.generateSource();
    sourceDefinitionIdRequestBody = new SourceDefinitionIdRequestBody().sourceDefinitionId(standardSource.getSourceId());
    ConnectorSpecification connectorSpecification = ConnectorSpecificationHelpers.generateConnectorSpecification();
    sourceDefinitionSpecificationRead = new SourceDefinitionSpecificationRead()
        .sourceDefinitionId(standardSource.getSourceId())
        .connectionSpecification(connectorSpecification.getConnectionSpecification())
        .documentationUrl(connectorSpecification.getDocumentationUrl().toString());

    sourceConnectionImplementation =
        SourceHelpers.generateSource(standardSource.getSourceId());

    sourceHandler = new SourceHandler(configRepository, validator, schedulerHandler, connectionsHandler, uuidGenerator);
  }

  @Test
  void testCreateSource()
      throws JsonValidationException, ConfigNotFoundException, IOException {
    when(uuidGenerator.get())
        .thenReturn(sourceConnectionImplementation.getSourceImplementationId());

    when(configRepository.getSourceConnectionImplementation(sourceConnectionImplementation.getSourceImplementationId()))
        .thenReturn(sourceConnectionImplementation);

    when(schedulerHandler.getSourceSpecification(sourceDefinitionIdRequestBody)).thenReturn(sourceDefinitionSpecificationRead);

    when(configRepository.getStandardSource(sourceDefinitionSpecificationRead.getSourceDefinitionId()))
        .thenReturn(standardSource);

    final SourceCreate sourceCreate = new SourceCreate()
        .name(sourceConnectionImplementation.getName())
        .workspaceId(sourceConnectionImplementation.getWorkspaceId())
        .sourceDefinitionId(standardSource.getSourceId())
        .connectionConfiguration(SourceHelpers.getTestImplementationJson());

    final SourceRead actualSourceRead =
        sourceHandler.createSource(sourceCreate);

    final SourceRead expectedSourceRead =
        SourceHelpers.getSourceRead(sourceConnectionImplementation, standardSource)
            .connectionConfiguration(SourceHelpers.getTestImplementationJson());

    assertEquals(expectedSourceRead, actualSourceRead);

    verify(validator)
        .validate(
            sourceDefinitionSpecificationRead.getConnectionSpecification(),
            sourceConnectionImplementation.getConfiguration());

    verify(configRepository).writeSourceConnectionImplementation(sourceConnectionImplementation);
  }

  @Test
  void testUpdateSource() throws JsonValidationException, ConfigNotFoundException, IOException {
    final JsonNode newConfiguration = sourceConnectionImplementation.getConfiguration();
    ((ObjectNode) newConfiguration).put("apiKey", "987-xyz");

    final SourceConnectionImplementation expectedSourceConnectionImplementation = Jsons.clone(sourceConnectionImplementation)
        .withConfiguration(newConfiguration)
        .withTombstone(false);

    when(configRepository.getSourceConnectionImplementation(sourceConnectionImplementation.getSourceImplementationId()))
        .thenReturn(sourceConnectionImplementation)
        .thenReturn(expectedSourceConnectionImplementation);

    when(schedulerHandler.getSourceSpecification(sourceDefinitionIdRequestBody)).thenReturn(sourceDefinitionSpecificationRead);

    when(configRepository.getStandardSource(sourceDefinitionSpecificationRead.getSourceDefinitionId()))
        .thenReturn(standardSource);

    final SourceUpdate sourceUpdate = new SourceUpdate()
        .name(sourceConnectionImplementation.getName())
        .sourceId(sourceConnectionImplementation.getSourceImplementationId())
        .connectionConfiguration(newConfiguration);

    final SourceRead actualSourceRead =
        sourceHandler.updateSource(sourceUpdate);

    SourceRead expectedSourceRead =
        SourceHelpers.getSourceRead(sourceConnectionImplementation, standardSource)
            .connectionConfiguration(newConfiguration);

    assertEquals(expectedSourceRead, actualSourceRead);

    verify(configRepository).writeSourceConnectionImplementation(expectedSourceConnectionImplementation);
  }

  @Test
  void testGetSourceImplementation() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(configRepository.getSourceConnectionImplementation(sourceConnectionImplementation.getSourceImplementationId()))
        .thenReturn(sourceConnectionImplementation);

    when(schedulerHandler.getSourceSpecification(sourceDefinitionIdRequestBody))
        .thenReturn(sourceDefinitionSpecificationRead);

    when(configRepository.getStandardSource(sourceDefinitionSpecificationRead.getSourceDefinitionId()))
        .thenReturn(standardSource);

    SourceRead expectedSourceRead =
        SourceHelpers.getSourceRead(sourceConnectionImplementation, standardSource);

    final SourceIdRequestBody sourceIdRequestBody = new SourceIdRequestBody()
        .sourceId(expectedSourceRead.getSourceId());

    final SourceRead actualSourceRead =
        sourceHandler.getSource(sourceIdRequestBody);

    assertEquals(expectedSourceRead, actualSourceRead);
  }

  @Test
  void testListSourceImplementationsForWorkspace()
      throws JsonValidationException, ConfigNotFoundException, IOException {
    when(configRepository.getSourceConnectionImplementation(sourceConnectionImplementation.getSourceImplementationId()))
        .thenReturn(sourceConnectionImplementation);
    when(configRepository.listSourceConnectionImplementations())
        .thenReturn(Lists.newArrayList(sourceConnectionImplementation));
    when(schedulerHandler.getSourceSpecification(sourceDefinitionIdRequestBody)).thenReturn(sourceDefinitionSpecificationRead);
    when(configRepository.getStandardSource(sourceDefinitionSpecificationRead.getSourceDefinitionId()))
        .thenReturn(standardSource);

    SourceRead expectedSourceRead =
        SourceHelpers.getSourceRead(sourceConnectionImplementation, standardSource);

    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody()
        .workspaceId(sourceConnectionImplementation.getWorkspaceId());

    final SourceReadList actualSourceImplementationRead =
        sourceHandler.listSourcesForWorkspace(workspaceIdRequestBody);

    assertEquals(expectedSourceRead, actualSourceImplementationRead.getSources().get(0));
  }

  @Test
  void testDeleteSourceImplementation() throws JsonValidationException, ConfigNotFoundException, IOException {
    final JsonNode newConfiguration = sourceConnectionImplementation.getConfiguration();
    ((ObjectNode) newConfiguration).put("apiKey", "987-xyz");

    final SourceConnectionImplementation expectedSourceConnectionImplementation = Jsons.clone(sourceConnectionImplementation)
        .withTombstone(true);

    when(configRepository.getSourceConnectionImplementation(sourceConnectionImplementation.getSourceImplementationId()))
        .thenReturn(sourceConnectionImplementation)
        .thenReturn(expectedSourceConnectionImplementation);

    when(schedulerHandler.getSourceSpecification(sourceDefinitionIdRequestBody)).thenReturn(sourceDefinitionSpecificationRead);

    when(configRepository.getStandardSource(sourceDefinitionSpecificationRead.getSourceDefinitionId()))
        .thenReturn(standardSource);

    final SourceIdRequestBody sourceIdRequestBody = new SourceIdRequestBody()
        .sourceId(sourceConnectionImplementation.getSourceImplementationId());

    final StandardSync standardSync = ConnectionHelpers.generateSyncWithSourceImplId(sourceConnectionImplementation.getSourceImplementationId());

    final ConnectionRead connectionRead = ConnectionHelpers.generateExpectedConnectionRead(standardSync);

    ConnectionReadList connectionReadList = new ConnectionReadList()
        .connections(Collections.singletonList(connectionRead));

    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody().workspaceId(sourceConnectionImplementation.getWorkspaceId());
    when(connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody)).thenReturn(connectionReadList);
    sourceHandler.deleteSource(sourceIdRequestBody);

    verify(configRepository).writeSourceConnectionImplementation(expectedSourceConnectionImplementation);

    final ConnectionUpdate expectedConnectionUpdate = new ConnectionUpdate()
        .connectionId(connectionRead.getConnectionId())
        .status(ConnectionStatus.DEPRECATED)
        .syncSchema(connectionRead.getSyncSchema())
        .schedule(connectionRead.getSchedule());

    verify(connectionsHandler).listConnectionsForWorkspace(workspaceIdRequestBody);
    verify(connectionsHandler).updateConnection(expectedConnectionUpdate);
  }

}
