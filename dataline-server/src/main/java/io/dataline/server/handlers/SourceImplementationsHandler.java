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

import com.fasterxml.jackson.databind.JsonNode;
import io.dataline.api.model.ConnectionStatus;
import io.dataline.api.model.ConnectionUpdate;
import io.dataline.api.model.SourceImplementationCreate;
import io.dataline.api.model.SourceImplementationIdRequestBody;
import io.dataline.api.model.SourceImplementationRead;
import io.dataline.api.model.SourceImplementationReadList;
import io.dataline.api.model.SourceImplementationUpdate;
import io.dataline.api.model.WorkspaceIdRequestBody;
import io.dataline.config.ConfigSchema;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.StandardSource;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.server.errors.KnownException;
import io.dataline.server.helpers.ConfigFetchers;
import io.dataline.server.validation.IntegrationSchemaValidation;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;
import java.util.stream.Collectors;

public class SourceImplementationsHandler {

  private final Supplier<UUID> uuidGenerator;
  private final ConfigPersistence configPersistence;
  private final IntegrationSchemaValidation validator;
  private final ConnectionsHandler connectionsHandler;

  public SourceImplementationsHandler(ConfigPersistence configPersistence,
                                      IntegrationSchemaValidation integrationSchemaValidation,
                                      ConnectionsHandler connectionsHandler,
                                      Supplier<UUID> uuidGenerator) {
    this.configPersistence = configPersistence;
    this.validator = integrationSchemaValidation;
    this.connectionsHandler = connectionsHandler;
    this.uuidGenerator = uuidGenerator;
  }

  public SourceImplementationsHandler(ConfigPersistence configPersistence,
                                      IntegrationSchemaValidation integrationSchemaValidation,
                                      ConnectionsHandler connectionsHandler) {
    this(configPersistence, integrationSchemaValidation, connectionsHandler, UUID::randomUUID);
  }

  public SourceImplementationRead createSourceImplementation(SourceImplementationCreate sourceImplementationCreate) {
    // validate configuration
    validateSourceImplementation(
        sourceImplementationCreate.getSourceSpecificationId(),
        sourceImplementationCreate.getConnectionConfiguration());

    // persist
    final UUID sourceImplementationId = uuidGenerator.get();
    persistSourceConnectionImplementation(
        sourceImplementationCreate.getSourceSpecificationId(),
        sourceImplementationCreate.getWorkspaceId(),
        sourceImplementationId,
        false,
        sourceImplementationCreate.getConnectionConfiguration());

    // read configuration from db
    return getSourceImplementationReadInternal(sourceImplementationId);
  }

  public SourceImplementationRead updateSourceImplementation(SourceImplementationUpdate sourceImplementationUpdate) {
    // get existing implementation
    final SourceConnectionImplementation persistedSourceImplementation =
        getSourceConnectionImplementationInternal(
            sourceImplementationUpdate.getSourceImplementationId());

    // validate configuration
    validateSourceImplementation(
        persistedSourceImplementation.getSourceSpecificationId(),
        sourceImplementationUpdate.getConnectionConfiguration());

    // persist
    persistSourceConnectionImplementation(
        persistedSourceImplementation.getSourceSpecificationId(),
        persistedSourceImplementation.getWorkspaceId(),
        sourceImplementationUpdate.getSourceImplementationId(),
        persistedSourceImplementation.getTombstone(),
        sourceImplementationUpdate.getConnectionConfiguration());

    // read configuration from db
    return getSourceImplementationReadInternal(
        sourceImplementationUpdate.getSourceImplementationId());
  }

  public SourceImplementationRead getSourceImplementation(SourceImplementationIdRequestBody sourceImplementationIdRequestBody) {

    return getSourceImplementationReadInternal(
        sourceImplementationIdRequestBody.getSourceImplementationId());
  }

  public SourceImplementationReadList listSourceImplementationsForWorkspace(WorkspaceIdRequestBody workspaceIdRequestBody) {

    final List<SourceImplementationRead> reads =
        ConfigFetchers.getSourceConnectionImplementations(configPersistence).stream()
            .filter(sourceImpl -> sourceImpl.getWorkspaceId().equals(workspaceIdRequestBody.getWorkspaceId()))
            .filter(sourceImpl -> !sourceImpl.getTombstone())
            .map(
                sourceConnectionImplementation -> {
                  final UUID sourceId =
                      ConfigFetchers.getSourceConnectionSpecification(
                          configPersistence,
                          sourceConnectionImplementation.getSourceSpecificationId())
                          .getSourceId();
                  final StandardSource standardSource =
                      ConfigFetchers.getStandardSource(
                          configPersistence,
                          sourceId);
                  return toSourceImplementationRead(sourceConnectionImplementation, standardSource);
                })
            .collect(Collectors.toList());

    final SourceImplementationReadList sourceImplementationReadList =
        new SourceImplementationReadList();
    sourceImplementationReadList.setSources(reads);
    return sourceImplementationReadList;
  }

  public void deleteSourceImplementation(SourceImplementationIdRequestBody sourceImplementationIdRequestBody) {
    // get existing implementation
    final SourceImplementationRead persistedSourceImplementation =
        getSourceImplementationReadInternal(
            sourceImplementationIdRequestBody.getSourceImplementationId());

    // persist
    persistSourceConnectionImplementation(
        persistedSourceImplementation.getSourceSpecificationId(),
        persistedSourceImplementation.getWorkspaceId(),
        persistedSourceImplementation.getSourceImplementationId(),
        true,
        persistedSourceImplementation.getConnectionConfiguration());

    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody();
    workspaceIdRequestBody.setWorkspaceId(persistedSourceImplementation.getWorkspaceId());
    // "delete" all connections associated with source implementation as well.
    connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody).getConnections().stream()
        .filter(connectionRead -> connectionRead.getSourceImplementationId().equals(sourceImplementationIdRequestBody.getSourceImplementationId()))
        .forEach(connectionRead -> {
          final ConnectionUpdate connectionUpdate = new ConnectionUpdate();
          connectionUpdate.setConnectionId(connectionRead.getConnectionId());
          connectionUpdate.setSyncSchema(connectionRead.getSyncSchema());
          connectionUpdate.setSchedule(connectionRead.getSchedule());
          connectionUpdate.setStatus(ConnectionStatus.DEPRECATED);

          connectionsHandler.updateConnection(connectionUpdate);
        });
  }

  private SourceConnectionImplementation getSourceConnectionImplementationInternal(UUID sourceImplementationId) {
    return ConfigFetchers.getSourceConnectionImplementation(
        configPersistence, sourceImplementationId);
  }

  private SourceImplementationRead getSourceImplementationReadInternal(UUID sourceImplementationId) {
    // read configuration from db
    final SourceConnectionImplementation retrievedSourceConnectionImplementation =
        getSourceConnectionImplementationInternal(sourceImplementationId);

    final UUID sourceId =
        ConfigFetchers.getSourceConnectionSpecification(
            configPersistence,
            retrievedSourceConnectionImplementation.getSourceSpecificationId())
            .getSourceId();
    final StandardSource standardSource =
        ConfigFetchers.getStandardSource(
            configPersistence,
            sourceId);
    return toSourceImplementationRead(retrievedSourceConnectionImplementation, standardSource);
  }

  private void validateSourceImplementation(UUID sourceConnectionSpecificationId, JsonNode implementationJson) {
    try {
      validator.validateSourceConnectionConfiguration(sourceConnectionSpecificationId, implementationJson);
    } catch (JsonValidationException e) {
      throw new KnownException(
          422,
          String.format(
              "The provided configuration does not fulfill the specification. Errors: %s",
              e.getMessage()));
    }
  }

  private void persistSourceConnectionImplementation(UUID sourceSpecificationId,
                                                     UUID workspaceId,
                                                     UUID sourceImplementationId,
                                                     boolean tombstone,
                                                     JsonNode configurationJson) {
    final SourceConnectionImplementation sourceConnectionImplementation =
        new SourceConnectionImplementation();
    sourceConnectionImplementation.withSourceSpecificationId(sourceSpecificationId);
    sourceConnectionImplementation.withWorkspaceId(workspaceId);
    sourceConnectionImplementation.withSourceImplementationId(sourceImplementationId);
    sourceConnectionImplementation.withTombstone(tombstone);
    sourceConnectionImplementation.withConfiguration(configurationJson);

    ConfigFetchers.writeConfig(
        configPersistence,
        ConfigSchema.SOURCE_CONNECTION_IMPLEMENTATION,
        sourceImplementationId.toString(),
        sourceConnectionImplementation);
  }

  private SourceImplementationRead toSourceImplementationRead(SourceConnectionImplementation sourceConnectionImplementation,
                                                              StandardSource standardSource) {
    final SourceImplementationRead sourceImplementationRead = new SourceImplementationRead();
    sourceImplementationRead.setSourceId(standardSource.getSourceId());
    sourceImplementationRead.setSourceImplementationId(
        sourceConnectionImplementation.getSourceImplementationId());
    sourceImplementationRead.setWorkspaceId(sourceConnectionImplementation.getWorkspaceId());
    sourceImplementationRead.setSourceSpecificationId(
        sourceConnectionImplementation.getSourceSpecificationId());
    sourceImplementationRead.setConnectionConfiguration(sourceConnectionImplementation.getConfiguration());
    sourceImplementationRead.setSourceName(standardSource.getName());

    return sourceImplementationRead;
  }

}
