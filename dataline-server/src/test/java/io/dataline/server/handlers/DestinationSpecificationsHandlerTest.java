package io.dataline.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.common.collect.Sets;
import io.dataline.api.model.DestinationIdRequestBody;
import io.dataline.api.model.DestinationSpecificationRead;
import io.dataline.config.DestinationConnectionSpecification;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.config.persistence.PersistenceConfigType;
import io.dataline.server.helpers.DestinationSpecificationHelpers;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DestinationSpecificationsHandlerTest {
  private ConfigPersistence configPersistence;
  private DestinationConnectionSpecification destinationConnectionSpecification;
  private DestinationSpecificationsHandler destinationSpecificationHandler;

  @BeforeEach
  void setUp() {
    configPersistence = mock(ConfigPersistence.class);
    destinationConnectionSpecification =
        DestinationSpecificationHelpers.generateDestinationSpecification();
    destinationSpecificationHandler = new DestinationSpecificationsHandler(configPersistence);
  }

  @Test
  void testGetDestinationSpecification() throws JsonValidationException {
    when(configPersistence.getConfigs(
            PersistenceConfigType.DESTINATION_CONNECTION_SPECIFICATION,
            DestinationConnectionSpecification.class))
        .thenReturn(Sets.newHashSet(destinationConnectionSpecification));

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
