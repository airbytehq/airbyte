package io.dataline.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.common.collect.Sets;
import io.dataline.api.model.SourceIdRequestBody;
import io.dataline.api.model.SourceRead;
import io.dataline.api.model.SourceReadList;
import io.dataline.config.StandardSource;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.config.persistence.PersistenceConfigType;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SourcesHandlerTest {
  private ConfigPersistence configPersistence;
  private StandardSource source;
  private SourcesHandler sourceHandler;

  @BeforeEach
  void setUp() {
    configPersistence = mock(ConfigPersistence.class);
    source = generateSource();
    sourceHandler = new SourcesHandler(configPersistence);
  }

  private StandardSource generateSource() {
    final UUID sourceId = UUID.randomUUID();

    final StandardSource standardSource = new StandardSource();
    standardSource.setSourceId(sourceId);
    standardSource.setName("presto");

    return standardSource;
  }

  @Test
  void testListSources() throws JsonValidationException {
    final StandardSource source2 = generateSource();
    configPersistence.writeConfig(
        PersistenceConfigType.STANDARD_SOURCE, source2.getSourceId().toString(), source2);

    when(configPersistence.getConfigs(PersistenceConfigType.STANDARD_SOURCE, StandardSource.class))
        .thenReturn(Sets.newHashSet(source, source2));

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
  void testGetSource() throws JsonValidationException, ConfigNotFoundException {
    when(configPersistence.getConfig(
            PersistenceConfigType.STANDARD_SOURCE,
            source.getSourceId().toString(),
            StandardSource.class))
        .thenReturn(source);

    SourceRead expectedSourceRead = new SourceRead();
    expectedSourceRead.setSourceId(source.getSourceId());
    expectedSourceRead.setName(source.getName());

    final SourceIdRequestBody sourceIdRequestBody = new SourceIdRequestBody();
    sourceIdRequestBody.setSourceId(source.getSourceId());

    final SourceRead actualSourceRead = sourceHandler.getSource(sourceIdRequestBody);

    assertEquals(expectedSourceRead, actualSourceRead);
  }
}
