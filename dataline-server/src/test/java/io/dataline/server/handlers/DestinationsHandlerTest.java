package io.dataline.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.dataline.api.model.DestinationIdRequestBody;
import io.dataline.api.model.DestinationRead;
import io.dataline.api.model.DestinationReadList;
import io.dataline.config.StandardDestination;
import io.dataline.config.persistence.ConfigPersistenceImpl;
import io.dataline.config.persistence.PersistenceConfigType;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DestinationsHandlerTest {
  private ConfigPersistenceImpl configPersistence;
  private StandardDestination destination;
  private DestinationsHandler destinationHandler;

  @BeforeEach
  void setUp() {
    configPersistence = ConfigPersistenceImpl.getTest();
    destination = creatDestination();
    destinationHandler = new DestinationsHandler(configPersistence);
  }

  @AfterEach
  void tearDown() {
    configPersistence.deleteAll();
  }

  private StandardDestination creatDestination() {
    final UUID destinationId = UUID.randomUUID();

    final StandardDestination standardDestination = new StandardDestination();
    standardDestination.setDestinationId(destinationId);
    standardDestination.setName("presto");

    configPersistence.writeConfig(
        PersistenceConfigType.STANDARD_DESTINATION, destinationId.toString(), standardDestination);

    return standardDestination;
  }

  @Test
  void listDestinations() {
    final StandardDestination destination2 = creatDestination();
    configPersistence.writeConfig(
        PersistenceConfigType.STANDARD_DESTINATION,
        destination2.getDestinationId().toString(),
        destination2);

    DestinationRead expectedDestinationRead1 = new DestinationRead();
    expectedDestinationRead1.setDestinationId(destination.getDestinationId());
    expectedDestinationRead1.setName(destination.getName());

    DestinationRead expectedDestinationRead2 = new DestinationRead();
    expectedDestinationRead2.setDestinationId(destination2.getDestinationId());
    expectedDestinationRead2.setName(destination2.getName());

    final DestinationReadList actualDestinationReadList = destinationHandler.listDestinations();

    final Optional<DestinationRead> actualDestinationRead1 =
        actualDestinationReadList.getDestinations().stream()
            .filter(
                destinationRead ->
                    destinationRead.getDestinationId().equals(destination.getDestinationId()))
            .findFirst();
    final Optional<DestinationRead> actualDestinationRead2 =
        actualDestinationReadList.getDestinations().stream()
            .filter(
                destinationRead ->
                    destinationRead.getDestinationId().equals(destination2.getDestinationId()))
            .findFirst();

    assertTrue(actualDestinationRead1.isPresent());
    assertEquals(expectedDestinationRead1, actualDestinationRead1.get());
    assertTrue(actualDestinationRead2.isPresent());
    assertEquals(expectedDestinationRead2, actualDestinationRead2.get());
  }

  @Test
  void getDestination() {
    DestinationRead expectedDestinationRead = new DestinationRead();
    expectedDestinationRead.setDestinationId(destination.getDestinationId());
    expectedDestinationRead.setName(destination.getName());

    final DestinationIdRequestBody destinationIdRequestBody = new DestinationIdRequestBody();
    destinationIdRequestBody.setDestinationId(destination.getDestinationId());

    final DestinationRead actualDestinationRead =
        destinationHandler.getDestination(destinationIdRequestBody);

    assertEquals(expectedDestinationRead, actualDestinationRead);
  }
}
