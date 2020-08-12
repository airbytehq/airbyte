package io.dataline.server.handlers;

import io.dataline.api.model.SourceImplementationCreate;
import io.dataline.api.model.SourceImplementationRead;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.config.persistence.PersistenceConfigType;
import io.dataline.server.errors.KnownException;
import io.dataline.server.validation.IntegrationSchemaValidation;
import java.util.UUID;

public class SourceImplementationsHandler {
  private final ConfigPersistence configPersistence;

  public SourceImplementationsHandler(ConfigPersistence configPersistence) {
    this.configPersistence = configPersistence;
  }

  public SourceImplementationRead createSourceImplementation(
      SourceImplementationCreate sourceImplementationCreate) {
    try {
      // validate configuration
      final IntegrationSchemaValidation validator =
          new IntegrationSchemaValidation(configPersistence);
      validator.validateSourceConnectionConfiguration(
          sourceImplementationCreate.getSourceSpecificationId(),
          sourceImplementationCreate.getConnectionConfiguration());

      // persist
      final UUID sourceImplementationId = UUID.randomUUID();
      final SourceConnectionImplementation newSourceConnectionImplementation =
          new SourceConnectionImplementation();
      newSourceConnectionImplementation.setSourceSpecificationId(
          sourceImplementationCreate.getSourceSpecificationId());
      newSourceConnectionImplementation.setSourceImplementationId(sourceImplementationId);
      newSourceConnectionImplementation.setConfiguration(
          sourceImplementationCreate.getConnectionConfiguration());

      configPersistence.writeConfig(
          PersistenceConfigType.SOURCE_CONNECTION_IMPLEMENTATION,
          sourceImplementationId.toString(),
          newSourceConnectionImplementation);

      // read configuration from db
      final SourceConnectionImplementation retrievedSourceConnectionImplementation =
          configPersistence.getConfig(
              PersistenceConfigType.SOURCE_CONNECTION_IMPLEMENTATION,
              sourceImplementationId.toString(),
              SourceConnectionImplementation.class);

      return toSourceImplementationRead(retrievedSourceConnectionImplementation);
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
              "Could not find source specification: %s.",
              sourceImplementationCreate.getSourceSpecificationId()));
    }
  }

  private SourceImplementationRead toSourceImplementationRead(
      SourceConnectionImplementation sourceConnectionImplementation) {
    final SourceImplementationRead sourceImplementationRead = new SourceImplementationRead();
    sourceConnectionImplementation.setSourceImplementationId(
        sourceConnectionImplementation.getSourceImplementationId());
    sourceConnectionImplementation.setSourceSpecificationId(
        sourceConnectionImplementation.getSourceSpecificationId());
    sourceConnectionImplementation.setConfiguration(
        sourceConnectionImplementation.getConfiguration());

    return sourceImplementationRead;
  }
}
