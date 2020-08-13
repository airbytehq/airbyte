package io.dataline.server.handlers;

import io.dataline.api.model.*;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.config.persistence.PersistenceConfigType;
import io.dataline.server.errors.KnownException;
import io.dataline.server.validation.IntegrationSchemaValidation;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

public class SourceImplementationsHandler {
  private final ConfigPersistence configPersistence;
  private final IntegrationSchemaValidation validator;

  public SourceImplementationsHandler(ConfigPersistence configPersistence) {
    this.configPersistence = configPersistence;
    this.validator = new IntegrationSchemaValidation(configPersistence);
  }

  public SourceImplementationRead createSourceImplementation(
      SourceImplementationCreate sourceImplementationCreate) {
    // validate configuration
    validateSourceImplementation(
        sourceImplementationCreate.getSourceSpecificationId(),
        sourceImplementationCreate.getConnectionConfiguration());

    // persist
    final UUID sourceImplementationId = UUID.randomUUID();
    persistSourceConnectionImplementation(
        sourceImplementationCreate.getSourceSpecificationId(),
        sourceImplementationCreate.getWorkspaceId(),
        sourceImplementationId,
        sourceImplementationCreate.getConnectionConfiguration());

    // read configuration from db
    return getSourceImplementationInternal(sourceImplementationId);
  }

  public SourceImplementationRead updateSourceImplementation(
      SourceImplementationUpdate sourceImplementationUpdate) {
    // get existing implementation
    final SourceImplementationRead persistedSourceImplementation =
        getSourceImplementationInternal(sourceImplementationUpdate.getSourceImplementationId());

    // validate configuration
    validateSourceImplementation(
        persistedSourceImplementation.getSourceSpecificationId(),
        sourceImplementationUpdate.getConnectionConfiguration());

    // persist
    persistSourceConnectionImplementation(
        persistedSourceImplementation.getSourceSpecificationId(),
        persistedSourceImplementation.getWorkspaceId(),
        sourceImplementationUpdate.getSourceImplementationId(),
        sourceImplementationUpdate.getConnectionConfiguration());

    // read configuration from db
    return getSourceImplementationInternal(sourceImplementationUpdate.getSourceImplementationId());
  }

  public SourceImplementationRead getSourceImplementation(
      SourceImplementationIdRequestBody sourceImplementationIdRequestBody) {

    return getSourceImplementationInternal(
        sourceImplementationIdRequestBody.getSourceImplementationId());
  }

  public SourceImplementationReadList listSourceImplementationsForWorkspace(
      WorkspaceIdRequestBody workspaceIdRequestBody) {
    try {

      final List<SourceImplementationRead> reads =
          configPersistence
              .getConfigs(
                  PersistenceConfigType.SOURCE_CONNECTION_IMPLEMENTATION,
                  SourceConnectionImplementation.class)
              .stream()
              .filter(
                  sourceConnectionImplementation ->
                      sourceConnectionImplementation
                          .getWorkspaceId()
                          .equals(workspaceIdRequestBody.getWorkspaceId()))
              .map(this::toSourceImplementationRead)
              .collect(Collectors.toList());

      final SourceImplementationReadList sourceImplementationReadList =
          new SourceImplementationReadList();
      sourceImplementationReadList.setSources(reads);
      return sourceImplementationReadList;
    } catch (JsonValidationException e) {
      throw new KnownException(
          422,
          String.format(
              "Attempted to retrieve a configuration does not fulfill the specification. Errors: %s",
              e.getMessage()));
    }
  }

  private SourceImplementationRead getSourceImplementationInternal(UUID sourceImplementationId) {
    // read configuration from db
    final SourceConnectionImplementation retrievedSourceConnectionImplementation;
    try {
      retrievedSourceConnectionImplementation =
          configPersistence.getConfig(
              PersistenceConfigType.SOURCE_CONNECTION_IMPLEMENTATION,
              sourceImplementationId.toString(),
              SourceConnectionImplementation.class);
    } catch (JsonValidationException e) {
      throw new KnownException(
          422,
          String.format(
              "The provided configuration does not fulfill the specification. Errors: %s",
              e.getMessage()));
    } catch (ConfigNotFoundException e) {
      throw new KnownException(
          422, String.format("Could not find source specification: %s.", sourceImplementationId));
    }

    return toSourceImplementationRead(retrievedSourceConnectionImplementation);
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
    } catch (ConfigNotFoundException e) {
      throw new KnownException(
          422,
          String.format(
              "Could not find source specification: %s.", sourceConnectionSpecificationId));
    }
  }

  private void persistSourceConnectionImplementation(
      UUID sourceSpecificationId,
      UUID workspaceId,
      UUID sourceImplementationId,
      Object configuration) {
    final SourceConnectionImplementation sourceConnectionImplementation =
        new SourceConnectionImplementation();
    sourceConnectionImplementation.setSourceSpecificationId(sourceSpecificationId);
    sourceConnectionImplementation.setWorkspaceId(workspaceId);
    sourceConnectionImplementation.setSourceImplementationId(sourceImplementationId);
    sourceConnectionImplementation.setConfiguration(configuration);

    configPersistence.writeConfig(
        PersistenceConfigType.SOURCE_CONNECTION_IMPLEMENTATION,
        sourceImplementationId.toString(),
        sourceConnectionImplementation);
  }

  private SourceImplementationRead toSourceImplementationRead(
      SourceConnectionImplementation sourceConnectionImplementation) {
    final SourceImplementationRead sourceImplementationRead = new SourceImplementationRead();
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
