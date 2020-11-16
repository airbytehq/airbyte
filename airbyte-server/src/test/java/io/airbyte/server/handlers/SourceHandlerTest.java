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
import io.airbyte.api.model.SourceCreate;
import io.airbyte.api.model.SourceDefinitionIdRequestBody;
import io.airbyte.api.model.SourceDefinitionSpecificationRead;
import io.airbyte.api.model.SourceIdRequestBody;
import io.airbyte.api.model.SourceRead;
import io.airbyte.api.model.SourceReadList;
import io.airbyte.api.model.SourceUpdate;
import io.airbyte.api.model.WorkspaceIdRequestBody;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSourceDefinition;
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
  private StandardSourceDefinition standardSourceDefinition;
  private SourceDefinitionSpecificationRead sourceDefinitionSpecificationRead;
  private SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody;
  private SourceConnection sourceConnection;
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

    standardSourceDefinition = SourceDefinitionHelpers.generateSource();
    sourceDefinitionIdRequestBody = new SourceDefinitionIdRequestBody().sourceDefinitionId(standardSourceDefinition.getSourceDefinitionId());
    final ConnectorSpecification connectorSpecification = ConnectorSpecificationHelpers.generateConnectorSpecification();
    sourceDefinitionSpecificationRead = new SourceDefinitionSpecificationRead()
        .sourceDefinitionId(standardSourceDefinition.getSourceDefinitionId())
        .connectionSpecification(connectorSpecification.getConnectionSpecification())
        .documentationUrl(connectorSpecification.getDocumentationUrl().toString());

    sourceConnection = SourceHelpers.generateSource(standardSourceDefinition.getSourceDefinitionId());

    sourceHandler = new SourceHandler(configRepository, validator, schedulerHandler, connectionsHandler, uuidGenerator);
  }

  @Test
  void testCreateSource() throws JsonValidationException, ConfigNotFoundException, IOException {
    final SourceCreate sourceCreate = new SourceCreate()
        .name(sourceConnection.getName())
        .workspaceId(sourceConnection.getWorkspaceId())
        .sourceDefinitionId(standardSourceDefinition.getSourceDefinitionId())
        .connectionConfiguration(sourceConnection.getConfiguration());

    when(uuidGenerator.get()).thenReturn(sourceConnection.getSourceId());
    when(configRepository.getSourceConnection(sourceConnection.getSourceId())).thenReturn(sourceConnection);
    when(schedulerHandler.getSourceDefinitionSpecification(sourceDefinitionIdRequestBody)).thenReturn(sourceDefinitionSpecificationRead);
    when(configRepository.getStandardSource(sourceDefinitionSpecificationRead.getSourceDefinitionId()))
        .thenReturn(standardSourceDefinition);

    final SourceRead actualSourceRead = sourceHandler.createSource(sourceCreate);

    final SourceRead expectedSourceRead = SourceHelpers.getSourceRead(sourceConnection, standardSourceDefinition)
        .connectionConfiguration(sourceConnection.getConfiguration());

    assertEquals(expectedSourceRead, actualSourceRead);

    verify(configRepository).writeSourceConnection(sourceConnection);
    verify(validator).ensure(sourceDefinitionSpecificationRead.getConnectionSpecification(), sourceConnection.getConfiguration());
  }

  @Test
  void testUpdateSource() throws JsonValidationException, ConfigNotFoundException, IOException {
    final JsonNode newConfiguration = sourceConnection.getConfiguration();
    ((ObjectNode) newConfiguration).put("apiKey", "987-xyz");

    final SourceConnection expectedSourceConnection = Jsons.clone(sourceConnection)
        .withConfiguration(newConfiguration)
        .withTombstone(false);

    final SourceUpdate sourceUpdate = new SourceUpdate()
        .name(sourceConnection.getName())
        .sourceId(sourceConnection.getSourceId())
        .connectionConfiguration(newConfiguration);

    when(configRepository.getSourceConnection(sourceConnection.getSourceId()))
        .thenReturn(sourceConnection)
        .thenReturn(expectedSourceConnection);
    when(schedulerHandler.getSourceDefinitionSpecification(sourceDefinitionIdRequestBody)).thenReturn(sourceDefinitionSpecificationRead);
    when(configRepository.getStandardSource(sourceDefinitionSpecificationRead.getSourceDefinitionId())).thenReturn(standardSourceDefinition);

    final SourceRead actualSourceRead = sourceHandler.updateSource(sourceUpdate);
    final SourceRead expectedSourceRead =
        SourceHelpers.getSourceRead(sourceConnection, standardSourceDefinition).connectionConfiguration(newConfiguration);

    assertEquals(expectedSourceRead, actualSourceRead);

    verify(configRepository).writeSourceConnection(expectedSourceConnection);
    verify(validator).ensure(sourceDefinitionSpecificationRead.getConnectionSpecification(), newConfiguration);
  }

  @Test
  void testGetSource() throws JsonValidationException, ConfigNotFoundException, IOException {
    final SourceRead expectedSourceRead = SourceHelpers.getSourceRead(sourceConnection, standardSourceDefinition);
    final SourceIdRequestBody sourceIdRequestBody = new SourceIdRequestBody().sourceId(expectedSourceRead.getSourceId());

    when(configRepository.getSourceConnection(sourceConnection.getSourceId())).thenReturn(sourceConnection);
    when(schedulerHandler.getSourceDefinitionSpecification(sourceDefinitionIdRequestBody)).thenReturn(sourceDefinitionSpecificationRead);
    when(configRepository.getStandardSource(sourceDefinitionSpecificationRead.getSourceDefinitionId())).thenReturn(standardSourceDefinition);

    final SourceRead actualSourceRead = sourceHandler.getSource(sourceIdRequestBody);

    assertEquals(expectedSourceRead, actualSourceRead);
  }

  @Test
  void testListSourcesForWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
    final SourceRead expectedSourceRead = SourceHelpers.getSourceRead(sourceConnection, standardSourceDefinition);
    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody().workspaceId(sourceConnection.getWorkspaceId());

    when(configRepository.getSourceConnection(sourceConnection.getSourceId())).thenReturn(sourceConnection);
    when(configRepository.listSourceConnection()).thenReturn(Lists.newArrayList(sourceConnection));
    when(schedulerHandler.getSourceDefinitionSpecification(sourceDefinitionIdRequestBody)).thenReturn(sourceDefinitionSpecificationRead);
    when(configRepository.getStandardSource(sourceDefinitionSpecificationRead.getSourceDefinitionId())).thenReturn(standardSourceDefinition);

    final SourceReadList actualSourceReadList = sourceHandler.listSourcesForWorkspace(workspaceIdRequestBody);

    assertEquals(expectedSourceRead, actualSourceReadList.getSources().get(0));
  }

  @Test
  void testDeleteSource() throws JsonValidationException, ConfigNotFoundException, IOException {
    final JsonNode newConfiguration = sourceConnection.getConfiguration();
    ((ObjectNode) newConfiguration).put("apiKey", "987-xyz");

    final SourceConnection expectedSourceConnection = Jsons.clone(sourceConnection).withTombstone(true);

    final SourceIdRequestBody sourceIdRequestBody = new SourceIdRequestBody().sourceId(sourceConnection.getSourceId());
    final StandardSync standardSync = ConnectionHelpers.generateSyncWithSourceId(sourceConnection.getSourceId());
    final ConnectionRead connectionRead = ConnectionHelpers.generateExpectedConnectionRead(standardSync);
    final ConnectionReadList connectionReadList = new ConnectionReadList().connections(Collections.singletonList(connectionRead));
    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody().workspaceId(sourceConnection.getWorkspaceId());

    when(configRepository.getSourceConnection(sourceConnection.getSourceId()))
        .thenReturn(sourceConnection)
        .thenReturn(expectedSourceConnection);
    when(schedulerHandler.getSourceDefinitionSpecification(sourceDefinitionIdRequestBody)).thenReturn(sourceDefinitionSpecificationRead);
    when(configRepository.getStandardSource(sourceDefinitionSpecificationRead.getSourceDefinitionId())).thenReturn(standardSourceDefinition);
    when(connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody)).thenReturn(connectionReadList);

    sourceHandler.deleteSource(sourceIdRequestBody);

    verify(configRepository).writeSourceConnection(expectedSourceConnection);
    verify(connectionsHandler).listConnectionsForWorkspace(workspaceIdRequestBody);
    verify(connectionsHandler).deleteConnection(connectionRead);
  }

}
