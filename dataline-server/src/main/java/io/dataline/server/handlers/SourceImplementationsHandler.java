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

import io.dataline.api.model.SourceImplementationCreate;
import io.dataline.api.model.SourceImplementationIdRequestBody;
import io.dataline.api.model.SourceImplementationRead;
import io.dataline.api.model.SourceImplementationReadList;
import io.dataline.api.model.SourceImplementationUpdate;
import io.dataline.api.model.WorkspaceIdRequestBody;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.config.persistence.PersistenceConfigType;
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

  public SourceImplementationsHandler(
      ConfigPersistence configPersistence,
      IntegrationSchemaValidation integrationSchemaValidation,
      Supplier<UUID> uuidGenerator) {
    this.configPersistence = configPersistence;
    this.validator = integrationSchemaValidation;
    this.uuidGenerator = uuidGenerator;
  }

  public SourceImplementationsHandler(
      ConfigPersistence configPersistence,
      IntegrationSchemaValidation integrationSchemaValidation) {
    this(configPersistence, integrationSchemaValidation, UUID::randomUUID);
  }

  public SourceImplementationRead createSourceImplementation(
      SourceImplementationCreate sourceImplementationCreate) {
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

  public SourceImplementationRead updateSourceImplementation(
      SourceImplementationUpdate sourceImplementationUpdate) {
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

  public SourceImplementationRead getSourceImplementation(
      SourceImplementationIdRequestBody sourceImplementationIdRequestBody) {

    return getSourceImplementationReadInternal(
        sourceImplementationIdRequestBody.getSourceImplementationId());
  }

  public SourceImplementationReadList listSourceImplementationsForWorkspace(
      WorkspaceIdRequestBody workspaceIdRequestBody) {

    final List<SourceImplementationRead> reads =
        ConfigFetchers.getSourceConnectionImplementations(configPersistence).stream()
            .filter(
                sourceConnectionImplementation ->
                    sourceConnectionImplementation
                        .getWorkspaceId()
                        .equals(workspaceIdRequestBody.getWorkspaceId()))
            .map(
                sourceConnectionImplementation -> {
                  final UUID sourceId =
                      ConfigFetchers.getSourceConnectionSpecification(
                              configPersistence,
                              sourceConnectionImplementation.getSourceSpecificationId())
                          .getSourceId();
                  return toSourceImplementationRead(sourceConnectionImplementation, sourceId);
                })
            .collect(Collectors.toList());

    final SourceImplementationReadList sourceImplementationReadList =
        new SourceImplementationReadList();
    sourceImplementationReadList.setSources(reads);
    return sourceImplementationReadList;
  }

  public void deleteSourceImplementation(
      SourceImplementationIdRequestBody sourceImplementationIdRequestBody) {
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
  }

  private SourceConnectionImplementation getSourceConnectionImplementationInternal(
      UUID sourceImplementationId) {
    return ConfigFetchers.getSourceConnectionImplementation(
        configPersistence, sourceImplementationId);
  }

  private SourceImplementationRead getSourceImplementationReadInternal(
      UUID sourceImplementationId) {
    // read configuration from db
    final SourceConnectionImplementation retrievedSourceConnectionImplementation =
        getSourceConnectionImplementationInternal(sourceImplementationId);

    final UUID sourceId =
        ConfigFetchers.getSourceConnectionSpecification(
                configPersistence,
                retrievedSourceConnectionImplementation.getSourceSpecificationId())
            .getSourceId();

    return toSourceImplementationRead(retrievedSourceConnectionImplementation, sourceId);
  }

  private void validateSourceImplementation(
      UUID sourceConnectionSpecificationId, Object implementation) {
    try {
      validator.validateSourceConnectionConfiguration(
          sourceConnectionSpecificationId, implementation);
    } catch (JsonValidationException e) {
      throw new KnownException(
          422,
          String.format(
              "The provided configuration does not fulfill the specification. Errors: %s",
              e.getMessage()));
    }
  }

  private void persistSourceConnectionImplementation(
      UUID sourceSpecificationId,
      UUID workspaceId,
      UUID sourceImplementationId,
      boolean tombstone,
      Object configuration) {
    final SourceConnectionImplementation sourceConnectionImplementation =
        new SourceConnectionImplementation();
    sourceConnectionImplementation.setSourceSpecificationId(sourceSpecificationId);
    sourceConnectionImplementation.setWorkspaceId(workspaceId);
    sourceConnectionImplementation.setSourceImplementationId(sourceImplementationId);
    sourceConnectionImplementation.setTombstone(tombstone);
    sourceConnectionImplementation.setConfiguration(configuration);

    ConfigFetchers.writeConfig(
        configPersistence,
        PersistenceConfigType.SOURCE_CONNECTION_IMPLEMENTATION,
        sourceImplementationId.toString(),
        sourceConnectionImplementation);
  }

  private SourceImplementationRead toSourceImplementationRead(
      SourceConnectionImplementation sourceConnectionImplementation, UUID sourceId) {
    final SourceImplementationRead sourceImplementationRead = new SourceImplementationRead();
    sourceImplementationRead.setSourceId(sourceId);
    sourceImplementationRead.setSourceImplementationId(
        sourceConnectionImplementation.getSourceImplementationId());
    sourceImplementationRead.setWorkspaceId(sourceConnectionImplementation.getWorkspaceId());
    sourceImplementationRead.setSourceSpecificationId(
        sourceConnectionImplementation.getSourceSpecificationId());
    sourceImplementationRead.setConnectionConfiguration(
        sourceConnectionImplementation.getConfiguration());

    return sourceImplementationRead;
  }
}
