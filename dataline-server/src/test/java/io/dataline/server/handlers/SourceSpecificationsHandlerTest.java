package io.dataline.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.common.collect.Sets;
import io.dataline.api.model.SourceIdRequestBody;
import io.dataline.api.model.SourceSpecificationRead;
import io.dataline.config.SourceConnectionSpecification;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.config.persistence.PersistenceConfigType;
import io.dataline.server.helpers.SourceSpecificationHelpers;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SourceSpecificationsHandlerTest {
  private ConfigPersistence configPersistence;
  private SourceConnectionSpecification sourceConnectionSpecification;
  private SourceSpecificationsHandler sourceSpecificationHandler;

  @BeforeEach
  void setUp() {
    configPersistence = mock(ConfigPersistence.class);
    sourceConnectionSpecification = SourceSpecificationHelpers.generateSourceSpecification();
    sourceSpecificationHandler = new SourceSpecificationsHandler(configPersistence);
  }

  @Test
  void testGetSourceSpecification() throws JsonValidationException {
    when(configPersistence.getConfigs(
            PersistenceConfigType.SOURCE_CONNECTION_SPECIFICATION,
            SourceConnectionSpecification.class))
        .thenReturn(Sets.newHashSet(sourceConnectionSpecification));

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
