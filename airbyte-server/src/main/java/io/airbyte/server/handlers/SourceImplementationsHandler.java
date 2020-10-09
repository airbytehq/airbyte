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
import io.airbyte.api.model.SourceImplementationCreate;
import io.airbyte.api.model.SourceImplementationIdRequestBody;
import io.airbyte.api.model.SourceImplementationRead;
import io.airbyte.api.model.SourceImplementationReadList;
import io.airbyte.api.model.SourceImplementationUpdate;
import io.airbyte.api.model.WorkspaceIdRequestBody;
import io.airbyte.commons.json.JsonValidationException;
import io.airbyte.config.SourceConnectionImplementation;
import io.airbyte.config.SourceConnectionSpecification;
import io.airbyte.config.StandardSource;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.server.validation.IntegrationSchemaValidation;
import java.io.IOException;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;

public class SourceImplementationsHandler {

  private final Supplier<UUID> uuidGenerator;
  private final ConfigRepository configRepository;
  private final IntegrationSchemaValidation validator;
  private final ConnectionsHandler connectionsHandler;

  public SourceImplementationsHandler(final ConfigRepository configRepository,
                                      final IntegrationSchemaValidation integrationSchemaValidation,
                                      final ConnectionsHandler connectionsHandler,
                                      final Supplier<UUID> uuidGenerator) {
    this.configRepository = configRepository;
    this.validator = integrationSchemaValidation;
    this.connectionsHandler = connectionsHandler;
    this.uuidGenerator = uuidGenerator;
  }

  public SourceImplementationsHandler(final ConfigRepository configRepository,
                                      final IntegrationSchemaValidation integrationSchemaValidation,
                                      final ConnectionsHandler connectionsHandler) {
    this(configRepository, integrationSchemaValidation, connectionsHandler, UUID::randomUUID);
  }

  public SourceImplementationRead createSourceImplementation(SourceImplementationCreate sourceImplementationCreate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // validate configuration
    validateSourceImplementation(
        sourceImplementationCreate.getSourceSpecificationId(),
        sourceImplementationCreate.getConnectionConfiguration());

    // persist
    final UUID sourceImplementationId = uuidGenerator.get();
    persistSourceConnectionImplementation(
        sourceImplementationCreate.getName() != null ? sourceImplementationCreate.getName() : "default",
        sourceImplementationCreate.getSourceSpecificationId(),
        sourceImplementationCreate.getWorkspaceId(),
        sourceImplementationId,
        false,
        sourceImplementationCreate.getConnectionConfiguration());

    // read configuration from db
    return buildSourceImplementationRead(sourceImplementationId);
  }

  public SourceImplementationRead updateSourceImplementation(SourceImplementationUpdate sourceImplementationUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // get existing implementation
    final SourceConnectionImplementation persistedSourceImplementation =
        configRepository.getSourceConnectionImplementation(sourceImplementationUpdate.getSourceImplementationId());

    // validate configuration
    validateSourceImplementation(
        persistedSourceImplementation.getSourceSpecificationId(),
        sourceImplementationUpdate.getConnectionConfiguration());

    // persist
    persistSourceConnectionImplementation(
        sourceImplementationUpdate.getName(),
        persistedSourceImplementation.getSourceSpecificationId(),
        persistedSourceImplementation.getWorkspaceId(),
        sourceImplementationUpdate.getSourceImplementationId(),
        persistedSourceImplementation.getTombstone(),
        sourceImplementationUpdate.getConnectionConfiguration());

    // read configuration from db
    return buildSourceImplementationRead(sourceImplementationUpdate.getSourceImplementationId());
  }

  public SourceImplementationRead getSourceImplementation(SourceImplementationIdRequestBody sourceImplementationIdRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return buildSourceImplementationRead(sourceImplementationIdRequestBody.getSourceImplementationId());
  }

  public SourceImplementationReadList listSourceImplementationsForWorkspace(WorkspaceIdRequestBody workspaceIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final List<SourceImplementationRead> reads = Lists.newArrayList();

    for (SourceConnectionImplementation sci : configRepository.listSourceConnectionImplementations()) {
      if (!sci.getWorkspaceId().equals(workspaceIdRequestBody.getWorkspaceId())) {
        continue;
      }
      if (sci.getTombstone()) {
        continue;
      }

      reads.add(buildSourceImplementationRead(sci.getSourceImplementationId()));
    }

    return new SourceImplementationReadList().sources(reads);
  }

  public void deleteSourceImplementation(SourceImplementationIdRequestBody sourceImplementationIdRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    // get existing implementation
    final SourceImplementationRead sourceImplementation =
        buildSourceImplementationRead(sourceImplementationIdRequestBody.getSourceImplementationId());

    // "delete" all connections associated with source implementation as well.
    // Delete connections first in case it it fails in the middle, source will still be visible
    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody().workspaceId(sourceImplementation.getWorkspaceId());
    for (ConnectionRead connectionRead : connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody).getConnections()) {
      if (!connectionRead.getSourceImplementationId().equals(sourceImplementation.getSourceImplementationId())) {
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
    persistSourceConnectionImplementation(
        sourceImplementation.getName(),
        sourceImplementation.getSourceSpecificationId(),
        sourceImplementation.getWorkspaceId(),
        sourceImplementation.getSourceImplementationId(),
        true,
        sourceImplementation.getConnectionConfiguration());
  }

  private SourceImplementationRead buildSourceImplementationRead(UUID sourceImplementationId)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // read configuration from db
    final SourceConnectionImplementation sourceConnectionImplementation = configRepository.getSourceConnectionImplementation(sourceImplementationId);

    final StandardSource standardSource = configRepository.getStandardSource(sourceConnectionImplementation.getSourceId());

    return toSourceImplementationRead(sourceConnectionImplementation, standardSource);
  }

  private void validateSourceImplementation(UUID sourceConnectionSpecificationId, JsonNode implementationJson)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    SourceConnectionSpecification scs = configRepository.getSourceConnectionSpecification(sourceConnectionSpecificationId);
    validator.validateConfig(scs, implementationJson);
  }

  private void persistSourceConnectionImplementation(final String name,
                                                     final UUID sourceSpecificationId,
                                                     final UUID workspaceId,
                                                     final UUID sourceImplementationId,
                                                     final boolean tombstone,
                                                     final JsonNode configurationJson)
      throws JsonValidationException, IOException {
    final SourceConnectionImplementation sourceConnectionImplementation = new SourceConnectionImplementation()
        .withName(name)
        .withSourceId(sourceSpecificationId)
        .withWorkspaceId(workspaceId)
        .withSourceImplementationId(sourceImplementationId)
        .withTombstone(tombstone)
        .withConfiguration(configurationJson);

    configRepository.writeSourceConnectionImplementation(sourceConnectionImplementation);
  }

  private SourceImplementationRead toSourceImplementationRead(final SourceConnectionImplementation sourceConnectionImplementation,
                                                              final StandardSource standardSource) {
    return new SourceImplementationRead()
        .sourceId(standardSource.getSourceId())
        .sourceName(standardSource.getName())
        .sourceImplementationId(sourceConnectionImplementation.getSourceImplementationId())
        .workspaceId(sourceConnectionImplementation.getWorkspaceId())
        .sourceSpecificationId(sourceConnectionImplementation.getSourceSpecificationId())
        .connectionConfiguration(sourceConnectionImplementation.getConfiguration())
        .name(sourceConnectionImplementation.getName());
  }

}
