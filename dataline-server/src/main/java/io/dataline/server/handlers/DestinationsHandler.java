package io.dataline.server.handlers;

import io.dataline.api.model.DestinationIdRequestBody;
import io.dataline.api.model.DestinationRead;
import io.dataline.api.model.DestinationReadList;
import io.dataline.config.StandardDestination;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.config.persistence.PersistenceConfigType;
import io.dataline.server.errors.KnownException;
import java.util.List;
import java.util.stream.Collectors;

public class DestinationsHandler {
  private final ConfigPersistence configPersistence;

  public DestinationsHandler(ConfigPersistence configPersistence) {
    this.configPersistence = configPersistence;
  }

  public DestinationReadList listDestinations() {
    final List<DestinationRead> destinationReads;
    try {
      destinationReads =
          configPersistence
              .getConfigs(PersistenceConfigType.STANDARD_DESTINATION, StandardDestination.class)
              .stream()
              .map(DestinationsHandler::toDestinationRead)
              .collect(Collectors.toList());
    } catch (JsonValidationException e) {
      throw new KnownException(422, e.getMessage(), e);
    }

    final DestinationReadList destinationReadList = new DestinationReadList();
    destinationReadList.setDestinations(destinationReads);
    return destinationReadList;
  }

  public DestinationRead getDestination(DestinationIdRequestBody destinationIdRequestBody) {
    final String destinationId = destinationIdRequestBody.getDestinationId().toString();
    final StandardDestination standardDestination;
    try {
      standardDestination =
          configPersistence.getConfig(
              PersistenceConfigType.STANDARD_DESTINATION, destinationId, StandardDestination.class);
    } catch (ConfigNotFoundException e) {
      throw new KnownException(404, e.getMessage(), e);
    } catch (JsonValidationException e) {
      throw new KnownException(422, e.getMessage(), e);
    }
    return toDestinationRead(standardDestination);
  }

  private static DestinationRead toDestinationRead(StandardDestination standardDestination) {
    final DestinationRead destinationRead = new DestinationRead();
    destinationRead.setDestinationId(standardDestination.getDestinationId());
    destinationRead.setName(standardDestination.getName());

    return destinationRead;
  }
}
