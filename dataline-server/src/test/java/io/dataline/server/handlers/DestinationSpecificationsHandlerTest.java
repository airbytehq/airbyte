package io.dataline.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.dataline.api.model.DestinationIdRequestBody;
import io.dataline.api.model.DestinationSpecificationRead;
import io.dataline.config.DestinationConnectionSpecification;
import io.dataline.config.persistence.ConfigPersistenceImpl;
import io.dataline.server.fixtures.DestinationSpecificationFixtures;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DestinationSpecificationsHandlerTest {
  private ConfigPersistenceImpl configPersistence;
  private DestinationConnectionSpecification destinationConnectionSpecification;
  private DestinationSpecificationsHandler destinationSpecificationHandler;

  @BeforeEach
  void setUp() {
    configPersistence = ConfigPersistenceImpl.getTest();
    destinationConnectionSpecification =
        DestinationSpecificationFixtures.createDestinationConnectionSpecification(
            configPersistence);
    destinationSpecificationHandler = new DestinationSpecificationsHandler(configPersistence);
  }

  @AfterEach
  void tearDown() {
    configPersistence.deleteAll();
  }

  @Test
  void getDestinationSpecification() {
    DestinationSpecificationRead expectedDestinationSpecificationRead =
        new DestinationSpecificationRead();
    expectedDestinationSpecificationRead.setDestinationId(
        destinationConnectionSpecification.getDestinationId());
    expectedDestinationSpecificationRead.setDestinationSpecificationId(
        destinationConnectionSpecification.getDestinationSpecificationId());
    expectedDestinationSpecificationRead.setConnectionSpecification(
        destinationConnectionSpecification.getSpecification());

    final DestinationIdRequestBody destinationIdRequestBody = new DestinationIdRequestBody();
    destinationIdRequestBody.setDestinationId(
        expectedDestinationSpecificationRead.getDestinationId());

    final DestinationSpecificationRead actualDestinationSpecificationRead =
        destinationSpecificationHandler.getDestinationSpecification(destinationIdRequestBody);

    assertEquals(expectedDestinationSpecificationRead, actualDestinationSpecificationRead);
  }
}
