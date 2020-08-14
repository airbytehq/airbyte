package io.dataline.server.handlers;

import io.dataline.api.model.DestinationIdRequestBody;
import io.dataline.api.model.DestinationSpecificationRead;
import io.dataline.config.DestinationConnectionSpecification;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.config.persistence.PersistenceConfigType;
import io.dataline.server.errors.KnownException;

public class DestinationSpecificationsHandler {
  private final ConfigPersistence configPersistence;

  public DestinationSpecificationsHandler(ConfigPersistence configPersistence) {
    this.configPersistence = configPersistence;
  }

  public DestinationSpecificationRead getDestinationSpecification(
      DestinationIdRequestBody destinationIdRequestBody) {
    final DestinationConnectionSpecification destinationConnection;
    try {
      // todo (cgardens) - this is a shortcoming of rolling our own disk storage. since we are not
      //   querying on a the primary key, we have to list all of the specification objects and then
      //   filter.
      destinationConnection =
          configPersistence
              .getConfigs(
                  PersistenceConfigType.DESTINATION_CONNECTION_SPECIFICATION,
                  DestinationConnectionSpecification.class)
              .stream()
              .filter(
                  destinationSpecification ->
                      destinationSpecification
                          .getDestinationId()
                          .equals(destinationIdRequestBody.getDestinationId()))
              .findFirst()
              .orElseThrow(
                  () ->
                      new KnownException(
                          404,
                          String.format(
                              "Could not find a destination specification for destination: %s",
                              destinationIdRequestBody.getDestinationId())));
    } catch (JsonValidationException e) {
      throw new KnownException(422, e.getMessage(), e);
    }

    return toDestinationSpecificationRead(destinationConnection);
  }

  private static DestinationSpecificationRead toDestinationSpecificationRead(
      DestinationConnectionSpecification destinationConnectionSpecification) {
    final DestinationSpecificationRead destinationSpecificationRead =
        new DestinationSpecificationRead();
    destinationSpecificationRead.setDestinationId(
        destinationConnectionSpecification.getDestinationId());
    destinationSpecificationRead.setDestinationSpecificationId(
        destinationConnectionSpecification.getDestinationSpecificationId());
    destinationSpecificationRead.setConnectionSpecification(
        destinationConnectionSpecification.getSpecification());

    return destinationSpecificationRead;
  }
}
