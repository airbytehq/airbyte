/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.Lists;
import io.dataline.api.model.ConnectionRead;
import io.dataline.api.model.ConnectionReadList;
import io.dataline.api.model.ConnectionStatus;
import io.dataline.api.model.ConnectionUpdate;
import io.dataline.api.model.SourceImplementationCreate;
import io.dataline.api.model.SourceImplementationIdRequestBody;
import io.dataline.api.model.SourceImplementationRead;
import io.dataline.api.model.SourceImplementationReadList;
import io.dataline.api.model.SourceImplementationUpdate;
import io.dataline.api.model.WorkspaceIdRequestBody;
import io.dataline.commons.json.Jsons;
import io.dataline.config.ConfigSchema;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.SourceConnectionSpecification;
import io.dataline.config.StandardSource;
import io.dataline.config.StandardSync;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.server.helpers.ConnectionHelpers;
import io.dataline.server.helpers.SourceHelpers;
import io.dataline.server.helpers.SourceImplementationHelpers;
import io.dataline.server.helpers.SourceSpecificationHelpers;
import io.dataline.server.validation.IntegrationSchemaValidation;
import java.io.IOException;
import java.util.Collections;
import java.util.UUID;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SourceImplementationsHandlerTest {

  private ConfigPersistence configPersistence;
  private StandardSource standardSource;
  private SourceConnectionSpecification sourceConnectionSpecification;
  private SourceConnectionImplementation sourceConnectionImplementation;
  private SourceImplementationsHandler sourceImplementationsHandler;
  private IntegrationSchemaValidation validator;
  private ConnectionsHandler connectionsHandler;
  private Supplier<UUID> uuidGenerator;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setUp() throws IOException {
    configPersistence = mock(ConfigPersistence.class);
    validator = mock(IntegrationSchemaValidation.class);
    connectionsHandler = mock(ConnectionsHandler.class);
    uuidGenerator = mock(Supplier.class);

    standardSource = SourceHelpers.generateSource();
    sourceConnectionSpecification = SourceSpecificationHelpers.generateSourceSpecification(standardSource.getSourceId());
    sourceConnectionImplementation =
        SourceImplementationHelpers.generateSourceImplementation(sourceConnectionSpecification.getSourceSpecificationId());

    sourceImplementationsHandler = new SourceImplementationsHandler(configPersistence, validator, connectionsHandler, uuidGenerator);
  }

  @Test
  void testCreateSourceImplementation()
      throws JsonValidationException, ConfigNotFoundException, IOException {
    when(uuidGenerator.get())
        .thenReturn(sourceConnectionImplementation.getSourceImplementationId());

    when(configPersistence.getConfig(
        ConfigSchema.SOURCE_CONNECTION_IMPLEMENTATION,
        sourceConnectionImplementation.getSourceImplementationId().toString(),
        SourceConnectionImplementation.class))
            .thenReturn(sourceConnectionImplementation);

    when(configPersistence.getConfig(
        ConfigSchema.SOURCE_CONNECTION_SPECIFICATION,
        sourceConnectionSpecification.getSourceSpecificationId().toString(),
        SourceConnectionSpecification.class))
            .thenReturn(sourceConnectionSpecification);

    when(configPersistence.getConfig(
        ConfigSchema.STANDARD_SOURCE,
        sourceConnectionSpecification.getSourceId().toString(),
        StandardSource.class))
            .thenReturn(standardSource);

    final SourceImplementationCreate sourceImplementationCreate = new SourceImplementationCreate()
        .name(sourceConnectionImplementation.getName())
        .workspaceId(sourceConnectionImplementation.getWorkspaceId())
        .sourceSpecificationId(sourceConnectionSpecification.getSourceSpecificationId())
        .connectionConfiguration(SourceImplementationHelpers.getTestImplementationJson());

    final SourceImplementationRead actualSourceImplementationRead =
        sourceImplementationsHandler.createSourceImplementation(sourceImplementationCreate);

    final SourceImplementationRead expectedSourceImplementationRead =
        SourceImplementationHelpers.getSourceImplementationRead(sourceConnectionImplementation, standardSource)
            .connectionConfiguration(SourceImplementationHelpers.getTestImplementationJson());

    assertEquals(expectedSourceImplementationRead, actualSourceImplementationRead);

    verify(validator)
        .validateConfig(
            sourceConnectionSpecification.getSourceSpecificationId(),
            sourceConnectionImplementation.getConfiguration());

    verify(configPersistence)
        .writeConfig(
            ConfigSchema.SOURCE_CONNECTION_IMPLEMENTATION,
            sourceConnectionImplementation.getSourceImplementationId().toString(),
            sourceConnectionImplementation);
  }

  @Test
  void testUpdateSourceImplementation() throws JsonValidationException, ConfigNotFoundException, IOException {
    final JsonNode newConfiguration = sourceConnectionImplementation.getConfiguration();
    ((ObjectNode) newConfiguration).put("apiKey", "987-xyz");

    final SourceConnectionImplementation expectedSourceConnectionImplementation = Jsons.clone(sourceConnectionImplementation)
        .withConfiguration(newConfiguration)
        .withTombstone(false);

    when(configPersistence.getConfig(
        ConfigSchema.SOURCE_CONNECTION_IMPLEMENTATION,
        sourceConnectionImplementation.getSourceImplementationId().toString(),
        SourceConnectionImplementation.class))
            .thenReturn(sourceConnectionImplementation)
            .thenReturn(expectedSourceConnectionImplementation);

    when(configPersistence.getConfig(
        ConfigSchema.SOURCE_CONNECTION_SPECIFICATION,
        sourceConnectionSpecification.getSourceSpecificationId().toString(),
        SourceConnectionSpecification.class))
            .thenReturn(sourceConnectionSpecification);

    when(configPersistence.getConfig(
        ConfigSchema.STANDARD_SOURCE,
        sourceConnectionSpecification.getSourceId().toString(),
        StandardSource.class))
            .thenReturn(standardSource);

    final SourceImplementationUpdate sourceImplementationUpdate = new SourceImplementationUpdate()
        .name(sourceConnectionImplementation.getName())
        .sourceImplementationId(sourceConnectionImplementation.getSourceImplementationId())
        .connectionConfiguration(newConfiguration);

    final SourceImplementationRead actualSourceImplementationRead =
        sourceImplementationsHandler.updateSourceImplementation(sourceImplementationUpdate);

    SourceImplementationRead expectedSourceImplementationRead =
        SourceImplementationHelpers.getSourceImplementationRead(sourceConnectionImplementation, standardSource)
            .connectionConfiguration(newConfiguration);

    assertEquals(expectedSourceImplementationRead, actualSourceImplementationRead);

    verify(configPersistence)
        .writeConfig(
            ConfigSchema.SOURCE_CONNECTION_IMPLEMENTATION,
            sourceConnectionImplementation.getSourceImplementationId().toString(),
            expectedSourceConnectionImplementation);
  }

  @Test
  void testGetSourceImplementation() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(configPersistence.getConfig(
        ConfigSchema.SOURCE_CONNECTION_IMPLEMENTATION,
        sourceConnectionImplementation.getSourceImplementationId().toString(),
        SourceConnectionImplementation.class))
            .thenReturn(sourceConnectionImplementation);

    when(configPersistence.getConfig(
        ConfigSchema.SOURCE_CONNECTION_SPECIFICATION,
        sourceConnectionSpecification.getSourceSpecificationId().toString(),
        SourceConnectionSpecification.class))
            .thenReturn(sourceConnectionSpecification);

    when(configPersistence.getConfig(
        ConfigSchema.STANDARD_SOURCE,
        sourceConnectionSpecification.getSourceId().toString(),
        StandardSource.class))
            .thenReturn(standardSource);

    SourceImplementationRead expectedSourceImplementationRead =
        SourceImplementationHelpers.getSourceImplementationRead(sourceConnectionImplementation, standardSource);

    final SourceImplementationIdRequestBody sourceImplementationIdRequestBody = new SourceImplementationIdRequestBody()
        .sourceImplementationId(expectedSourceImplementationRead.getSourceImplementationId());

    final SourceImplementationRead actualSourceImplementationRead =
        sourceImplementationsHandler.getSourceImplementation(sourceImplementationIdRequestBody);

    assertEquals(expectedSourceImplementationRead, actualSourceImplementationRead);
  }

  @Test
  void testListSourceImplementationsForWorkspace()
      throws JsonValidationException, ConfigNotFoundException, IOException {
    when(configPersistence.listConfigs(
        ConfigSchema.SOURCE_CONNECTION_IMPLEMENTATION,
        SourceConnectionImplementation.class))
            .thenReturn(Lists.newArrayList(sourceConnectionImplementation));

    when(configPersistence.getConfig(
        ConfigSchema.SOURCE_CONNECTION_SPECIFICATION,
        sourceConnectionSpecification.getSourceSpecificationId().toString(),
        SourceConnectionSpecification.class))
            .thenReturn(sourceConnectionSpecification);

    when(configPersistence.getConfig(
        ConfigSchema.STANDARD_SOURCE,
        sourceConnectionSpecification.getSourceId().toString(),
        StandardSource.class))
            .thenReturn(standardSource);

    SourceImplementationRead expectedSourceImplementationRead =
        SourceImplementationHelpers.getSourceImplementationRead(sourceConnectionImplementation, standardSource);

    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody()
        .workspaceId(sourceConnectionImplementation.getWorkspaceId());

    final SourceImplementationReadList actualSourceImplementationRead =
        sourceImplementationsHandler.listSourceImplementationsForWorkspace(workspaceIdRequestBody);

    assertEquals(expectedSourceImplementationRead, actualSourceImplementationRead.getSources().get(0));
  }

  @Test
  void testDeleteSourceImplementation() throws JsonValidationException, ConfigNotFoundException, IOException {
    final JsonNode newConfiguration = sourceConnectionImplementation.getConfiguration();
    ((ObjectNode) newConfiguration).put("apiKey", "987-xyz");

    final SourceConnectionImplementation expectedSourceConnectionImplementation = Jsons.clone(sourceConnectionImplementation)
        .withTombstone(true);

    when(configPersistence.getConfig(
        ConfigSchema.SOURCE_CONNECTION_IMPLEMENTATION,
        sourceConnectionImplementation.getSourceImplementationId().toString(),
        SourceConnectionImplementation.class))
            .thenReturn(sourceConnectionImplementation)
            .thenReturn(expectedSourceConnectionImplementation);

    when(configPersistence.getConfig(
        ConfigSchema.SOURCE_CONNECTION_SPECIFICATION,
        sourceConnectionSpecification.getSourceSpecificationId().toString(),
        SourceConnectionSpecification.class))
            .thenReturn(sourceConnectionSpecification);

    when(configPersistence.getConfig(
        ConfigSchema.STANDARD_SOURCE,
        sourceConnectionSpecification.getSourceId().toString(),
        StandardSource.class))
            .thenReturn(standardSource);

    final SourceImplementationIdRequestBody sourceImplementationIdRequestBody = new SourceImplementationIdRequestBody()
        .sourceImplementationId(sourceConnectionImplementation.getSourceImplementationId());

    final StandardSync standardSync = ConnectionHelpers.generateSync(sourceConnectionImplementation.getSourceImplementationId());

    final ConnectionRead connectionRead = ConnectionHelpers.generateExpectedConnectionRead(standardSync);

    ConnectionReadList connectionReadList = new ConnectionReadList()
        .connections(Collections.singletonList(connectionRead));

    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody().workspaceId(sourceConnectionImplementation.getWorkspaceId());
    when(connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody)).thenReturn(connectionReadList);
    sourceImplementationsHandler.deleteSourceImplementation(sourceImplementationIdRequestBody);

    verify(configPersistence)
        .writeConfig(
            ConfigSchema.SOURCE_CONNECTION_IMPLEMENTATION,
            sourceConnectionImplementation.getSourceImplementationId().toString(),
            expectedSourceConnectionImplementation);

    final ConnectionUpdate expectedConnectionUpdate = new ConnectionUpdate()
        .connectionId(connectionRead.getConnectionId())
        .status(ConnectionStatus.DEPRECATED)
        .syncSchema(connectionRead.getSyncSchema())
        .schedule(connectionRead.getSchedule());

    verify(connectionsHandler).listConnectionsForWorkspace(workspaceIdRequestBody);
    verify(connectionsHandler).updateConnection(expectedConnectionUpdate);
  }

}
