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

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.api.model.ConnectionRead;
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
import io.airbyte.config.SourceConnectionImplementation;
import io.airbyte.config.StandardSource;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;

public class SourceHandler {

  private final Supplier<UUID> uuidGenerator;
  private final ConfigRepository configRepository;
  private final JsonSchemaValidator validator;
  private SchedulerHandler schedulerHandler;
  private final ConnectionsHandler connectionsHandler;

  public SourceHandler(final ConfigRepository configRepository,
                       final JsonSchemaValidator integrationSchemaValidation,
                       final SchedulerHandler schedulerHandler,
                       final ConnectionsHandler connectionsHandler,
                       final Supplier<UUID> uuidGenerator) {
    this.configRepository = configRepository;
    this.validator = integrationSchemaValidation;
    this.schedulerHandler = schedulerHandler;
    this.connectionsHandler = connectionsHandler;
    this.uuidGenerator = uuidGenerator;
  }

  public SourceHandler(final ConfigRepository configRepository,
                       final JsonSchemaValidator integrationSchemaValidation,
                       final SchedulerHandler schedulerHandler,
                       final ConnectionsHandler connectionsHandler) {
    this(configRepository, integrationSchemaValidation, schedulerHandler, connectionsHandler, UUID::randomUUID);
  }

  public SourceRead createSource(SourceCreate sourceCreate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // validate configuration
    validateSource(
        sourceCreate.getSourceDefinitionId(),
        sourceCreate.getConnectionConfiguration());

    // persist
    final UUID sourceId = uuidGenerator.get();
    persistSourceConnection(
        sourceCreate.getName() != null ? sourceCreate.getName() : "default",
        sourceCreate.getSourceDefinitionId(),
        sourceCreate.getWorkspaceId(),
        sourceId,
        false,
        sourceCreate.getConnectionConfiguration());

    // read configuration from db
    return buildSourceRead(sourceId);
  }

  public SourceRead updateSource(SourceUpdate sourceUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // get existing source
    final SourceConnectionImplementation persistedSource =
        configRepository.getSourceConnectionImplementation(sourceUpdate.getSourceId());

    // validate configuration
    validateSource(
        persistedSource.getSourceId(),
        sourceUpdate.getConnectionConfiguration());

    // persist
    persistSourceConnection(
        sourceUpdate.getName(),
        persistedSource.getSourceId(),
        persistedSource.getWorkspaceId(),
        sourceUpdate.getSourceId(),
        persistedSource.getTombstone(),
        sourceUpdate.getConnectionConfiguration());

    // read configuration from db
    return buildSourceRead(sourceUpdate.getSourceId());
  }

  public SourceRead getSource(SourceIdRequestBody sourceIdRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return buildSourceRead(sourceIdRequestBody.getSourceId());
  }

  public SourceReadList listSourcesForWorkspace(WorkspaceIdRequestBody workspaceIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final List<SourceRead> reads = Lists.newArrayList();

    for (SourceConnectionImplementation sci : configRepository.listSourceConnectionImplementations()) {
      if (!sci.getWorkspaceId().equals(workspaceIdRequestBody.getWorkspaceId())) {
        continue;
      }
      if (sci.getTombstone()) {
        continue;
      }

      reads.add(buildSourceRead(sci.getSourceImplementationId()));
    }

    return new SourceReadList().sources(reads);
  }

  public void deleteSource(SourceIdRequestBody sourceIdRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    // get existing source
    final SourceRead source =
        buildSourceRead(sourceIdRequestBody.getSourceId());

    // "delete" all connections associated with source as well.
    // Delete connections first in case it it fails in the middle, source will still be visible
    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody().workspaceId(source.getWorkspaceId());
    for (ConnectionRead connectionRead : connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody).getConnections()) {
      if (!connectionRead.getSourceId().equals(source.getSourceId())) {
        continue;
      }

      final ConnectionUpdate connectionUpdate = new ConnectionUpdate()
          .connectionId(connectionRead.getConnectionId())
          .syncSchema(connectionRead.getSyncSchema())
          .schedule(connectionRead.getSchedule())
          .status(ConnectionStatus.DEPRECATED);

      connectionsHandler.updateConnection(connectionUpdate);
    }

    // persist
    persistSourceConnection(
        source.getName(),
        source.getSourceDefinitionId(),
        source.getWorkspaceId(),
        source.getSourceId(),
        true,
        source.getConnectionConfiguration());
  }

  private SourceRead buildSourceRead(UUID sourceId)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // read configuration from db
    final SourceConnectionImplementation sourceConnection = configRepository.getSourceConnectionImplementation(sourceId);

    final StandardSource standardSource = configRepository.getStandardSource(sourceConnection.getSourceId());

    return toSourceRead(sourceConnection, standardSource);
  }

  private void validateSource(UUID sourceDefinitionId, JsonNode implementationJson)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    SourceDefinitionSpecificationRead sds =
        schedulerHandler.getSourceSpecification(new SourceDefinitionIdRequestBody().sourceDefinitionId(sourceDefinitionId));

    validator.validate(sds.getConnectionSpecification(), implementationJson);
  }

  private void persistSourceConnection(final String name,
                                       final UUID sourceDefinitionId,
                                       final UUID workspaceId,
                                       final UUID sourceId,
                                       final boolean tombstone,
                                       final JsonNode configurationJson)
      throws JsonValidationException, IOException {
    final SourceConnectionImplementation sourceConnection = new SourceConnectionImplementation()
        .withName(name)
        .withSourceId(sourceDefinitionId)
        .withWorkspaceId(workspaceId)
        .withSourceImplementationId(sourceId)
        .withTombstone(tombstone)
        .withConfiguration(configurationJson);

    configRepository.writeSourceConnectionImplementation(sourceConnection);
  }

  private SourceRead toSourceRead(final SourceConnectionImplementation sourceConnection,
                                  final StandardSource standardSource) {
    return new SourceRead()
        .sourceDefinitionId(standardSource.getSourceId())
        .sourceName(standardSource.getName())
        .sourceId(sourceConnection.getSourceImplementationId())
        .workspaceId(sourceConnection.getWorkspaceId())
        .sourceDefinitionId(sourceConnection.getSourceId())
        .connectionConfiguration(sourceConnection.getConfiguration())
        .name(sourceConnection.getName());
  }

}
