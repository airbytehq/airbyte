package io.dataline.server.handlers;

import static org.junit.jupiter.api.Assertions.*;

import io.dataline.api.model.SourceIdRequestBody;
import io.dataline.api.model.SourceRead;
import io.dataline.api.model.SourceReadList;
import io.dataline.config.StandardSource;
import io.dataline.config.persistence.ConfigPersistenceImpl;
import io.dataline.config.persistence.PersistenceConfigType;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SourcesHandlerTest {
  private ConfigPersistenceImpl configPersistence;
  private StandardSource source;
  private SourcesHandler sourceHandler;

  @BeforeEach
  void setUp() {
    configPersistence = ConfigPersistenceImpl.getTest();
    source = creatSource();
    sourceHandler = new SourcesHandler(configPersistence);
  }

  @AfterEach
  void tearDown() {
    configPersistence.deleteAll();
  }

  private StandardSource creatSource() {
    final UUID sourceId = UUID.randomUUID();

    final StandardSource standardSource = new StandardSource();
    standardSource.setSourceId(sourceId);
    standardSource.setName("presto");

    configPersistence.writeConfig(
        PersistenceConfigType.STANDARD_SOURCE, sourceId.toString(), standardSource);

    return standardSource;
  }

  @Test
  void listSources() {
    final StandardSource source2 = creatSource();
    configPersistence.writeConfig(
        PersistenceConfigType.STANDARD_SOURCE, source2.getSourceId().toString(), source2);

    SourceRead expectedSourceRead1 = new SourceRead();
    expectedSourceRead1.setSourceId(source.getSourceId());
    expectedSourceRead1.setName(source.getName());

    SourceRead expectedSourceRead2 = new SourceRead();
    expectedSourceRead2.setSourceId(source2.getSourceId());
    expectedSourceRead2.setName(source2.getName());

    final SourceReadList actualSourceReadList = sourceHandler.listSources();

    final Optional<SourceRead> actualSourceRead1 =
        actualSourceReadList.getSources().stream()
            .filter(sourceRead -> sourceRead.getSourceId().equals(source.getSourceId()))
            .findFirst();
    final Optional<SourceRead> actualSourceRead2 =
        actualSourceReadList.getSources().stream()
            .filter(sourceRead -> sourceRead.getSourceId().equals(source2.getSourceId()))
            .findFirst();

    assertTrue(actualSourceRead1.isPresent());
    assertEquals(expectedSourceRead1, actualSourceRead1.get());
    assertTrue(actualSourceRead2.isPresent());
    assertEquals(expectedSourceRead2, actualSourceRead2.get());
  }

  @Test
  void getSource() {
    SourceRead expectedSourceRead = new SourceRead();
    expectedSourceRead.setSourceId(source.getSourceId());
    expectedSourceRead.setName(source.getName());

    final SourceIdRequestBody sourceIdRequestBody = new SourceIdRequestBody();
    sourceIdRequestBody.setSourceId(source.getSourceId());

    final SourceRead actualSourceRead = sourceHandler.getSource(sourceIdRequestBody);

    assertEquals(expectedSourceRead, actualSourceRead);
  }
}
