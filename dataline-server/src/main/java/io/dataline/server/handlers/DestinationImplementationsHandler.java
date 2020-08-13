package io.dataline.server.handlers;

import io.dataline.api.model.*;
import io.dataline.config.DestinationConnectionImplementation;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.config.persistence.PersistenceConfigType;
import io.dataline.server.errors.KnownException;
import io.dataline.server.validation.IntegrationSchemaValidation;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

public class DestinationImplementationsHandler {
  private final ConfigPersistence configPersistence;
  private final IntegrationSchemaValidation validator;

  public DestinationImplementationsHandler(ConfigPersistence configPersistence) {
    this.configPersistence = configPersistence;
    this.validator = new IntegrationSchemaValidation(configPersistence);
  }

  public DestinationImplementationRead createDestinationImplementation(
      DestinationImplementationCreate destinationImplementationCreate) {
    // validate configuration
    validateDestinationImplementation(
        destinationImplementationCreate.getDestinationSpecificationId(),
        destinationImplementationCreate.getConnectionConfiguration());

    // persist
    final UUID destinationImplementationId = UUID.randomUUID();
    persistDestinationConnectionImplementation(
        destinationImplementationCreate.getDestinationSpecificationId(),
        destinationImplementationCreate.getWorkspaceId(),
        destinationImplementationId,
        destinationImplementationCreate.getConnectionConfiguration());

    // read configuration from db
    return getDestinationImplementationInternal(destinationImplementationId);
  }

  public DestinationImplementationRead updateDestinationImplementation(
      DestinationImplementationUpdate destinationImplementationUpdate) {
    // get existing implementation
    final DestinationImplementationRead persistedDestinationImplementation =
        getDestinationImplementationInternal(
            destinationImplementationUpdate.getDestinationImplementationId());

    // validate configuration
    validateDestinationImplementation(
        persistedDestinationImplementation.getDestinationSpecificationId(),
        destinationImplementationUpdate.getConnectionConfiguration());

    // persist
    persistDestinationConnectionImplementation(
        persistedDestinationImplementation.getDestinationSpecificationId(),
        persistedDestinationImplementation.getWorkspaceId(),
        destinationImplementationUpdate.getDestinationImplementationId(),
        destinationImplementationUpdate.getConnectionConfiguration());

    // read configuration from db
    return getDestinationImplementationInternal(
        destinationImplementationUpdate.getDestinationImplementationId());
  }

  public DestinationImplementationRead getDestinationImplementation(
      DestinationImplementationIdRequestBody destinationImplementationIdRequestBody) {

    return getDestinationImplementationInternal(
        destinationImplementationIdRequestBody.getDestinationImplementationId());
  }

  public DestinationImplementationReadList listDestinationImplementationsForWorkspace(
      WorkspaceIdRequestBody workspaceIdRequestBody) {
    try {

      final List<DestinationImplementationRead> reads =
          configPersistence
              .getConfigs(
                  PersistenceConfigType.DESTINATION_CONNECTION_IMPLEMENTATION,
                  DestinationConnectionImplementation.class)
              .stream()
              .filter(
                  destinationConnectionImplementation ->
                      destinationConnectionImplementation
                          .getWorkspaceId()
                          .equals(workspaceIdRequestBody.getWorkspaceId()))
              .map(this::toDestinationImplementationRead)
              .collect(Collectors.toList());

      final DestinationImplementationReadList destinationImplementationReadList =
          new DestinationImplementationReadList();
      destinationImplementationReadList.setDestinations(reads);
      return destinationImplementationReadList;
    } catch (JsonValidationException e) {
      throw new KnownException(
          422,
          String.format(
              "Attempted to retrieve a configuration does not fulfill the specification. Errors: %s",
              e.getMessage()));
    }
  }

  private DestinationImplementationRead getDestinationImplementationInternal(
      UUID destinationImplementationId) {
    // read configuration from db
    final DestinationConnectionImplementation retrievedDestinationConnectionImplementation;
    try {
      retrievedDestinationConnectionImplementation =
          configPersistence.getConfig(
              PersistenceConfigType.DESTINATION_CONNECTION_IMPLEMENTATION,
              destinationImplementationId.toString(),
              DestinationConnectionImplementation.class);
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
              "Could not find destination specification: %s.", destinationImplementationId));
    }

    return toDestinationImplementationRead(retrievedDestinationConnectionImplementation);
  }

  private void validateDestinationImplementation(
      UUID destinationConnectionSpecificationId, Object implementation) {
    try {
      validator.validateDestinationConnectionConfiguration(
          destinationConnectionSpecificationId, implementation);
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
              "Could not find destination specification: %s.",
              destinationConnectionSpecificationId));
    }
  }

  private void persistDestinationConnectionImplementation(
      UUID destinationSpecificationId,
      UUID workspaceId,
      UUID destinationImplementationId,
      Object configuration) {
    final DestinationConnectionImplementation destinationConnectionImplementation =
        new DestinationConnectionImplementation();
    destinationConnectionImplementation.setDestinationSpecificationId(destinationSpecificationId);
    destinationConnectionImplementation.setWorkspaceId(workspaceId);
    destinationConnectionImplementation.setDestinationImplementationId(destinationImplementationId);
    destinationConnectionImplementation.setConfiguration(configuration);

    configPersistence.writeConfig(
        PersistenceConfigType.DESTINATION_CONNECTION_IMPLEMENTATION,
        destinationImplementationId.toString(),
        destinationConnectionImplementation);
  }

  private DestinationImplementationRead toDestinationImplementationRead(
      DestinationConnectionImplementation destinationConnectionImplementation) {
    final DestinationImplementationRead destinationImplementationRead =
        new DestinationImplementationRead();
    destinationImplementationRead.setDestinationImplementationId(
        destinationConnectionImplementation.getDestinationImplementationId());
    destinationImplementationRead.setWorkspaceId(
        destinationConnectionImplementation.getWorkspaceId());
    destinationImplementationRead.setDestinationSpecificationId(
        destinationConnectionImplementation.getDestinationSpecificationId());
    destinationImplementationRead.setConnectionConfiguration(
        destinationConnectionImplementation.getConfiguration());

    return destinationImplementationRead;
  }
}
