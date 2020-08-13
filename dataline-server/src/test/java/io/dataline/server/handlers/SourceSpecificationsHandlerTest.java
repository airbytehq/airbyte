package io.dataline.server.handlers;

import static org.junit.jupiter.api.Assertions.*;

import io.dataline.api.model.SourceIdRequestBody;
import io.dataline.api.model.SourceSpecificationRead;
import io.dataline.config.SourceConnectionSpecification;
import io.dataline.config.persistence.ConfigPersistenceImpl;
import io.dataline.server.fixtures.SourceSpecificationFixtures;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SourceSpecificationsHandlerTest {
  private ConfigPersistenceImpl configPersistence;
  private SourceConnectionSpecification sourceConnectionSpecification;
  private SourceSpecificationsHandler sourceSpecificationHandler;

  @BeforeEach
  void setUp() {
    configPersistence = ConfigPersistenceImpl.getTest();
    sourceConnectionSpecification =
        SourceSpecificationFixtures.createSourceConnectionSpecification(configPersistence);
    sourceSpecificationHandler = new SourceSpecificationsHandler(configPersistence);
  }

  @AfterEach
  void tearDown() {
    configPersistence.deleteAll();
  }

  @Test
  void getSourceSpecification() {
    SourceSpecificationRead expectedSourceSpecificationRead = new SourceSpecificationRead();
    expectedSourceSpecificationRead.setSourceId(sourceConnectionSpecification.getSourceId());
    expectedSourceSpecificationRead.setSourceSpecificationId(
        sourceConnectionSpecification.getSourceSpecificationId());
    expectedSourceSpecificationRead.setConnectionSpecification(
        sourceConnectionSpecification.getSpecification());

    final SourceIdRequestBody sourceIdRequestBody = new SourceIdRequestBody();
    sourceIdRequestBody.setSourceId(expectedSourceSpecificationRead.getSourceId());

    final SourceSpecificationRead actualSourceSpecificationRead =
        sourceSpecificationHandler.getSourceSpecification(sourceIdRequestBody);

    assertEquals(expectedSourceSpecificationRead, actualSourceSpecificationRead);
  }
}
