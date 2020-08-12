package io.dataline.server.handlers;

import io.dataline.api.model.SourceIdRequestBody;
import io.dataline.api.model.SourceRead;
import io.dataline.api.model.SourceReadList;
import io.dataline.config.StandardSource;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.config.persistence.PersistenceConfigType;
import io.dataline.server.errors.KnownException;
import java.util.List;
import java.util.stream.Collectors;

public class SourcesHandler {
  private final ConfigPersistence configPersistence;

  public SourcesHandler(ConfigPersistence configPersistence) {
    this.configPersistence = configPersistence;
  }

  public SourceReadList listSources() {
    final List<SourceRead> sourceReads;
    try {
      sourceReads =
          configPersistence
              .getConfigs(PersistenceConfigType.STANDARD_SOURCE, StandardSource.class)
              .stream()
              .map(SourcesHandler::toSourceRead)
              .collect(Collectors.toList());
    } catch (JsonValidationException e) {
      throw new KnownException(422, e.getMessage(), e);
    }

    final SourceReadList sourceReadList = new SourceReadList();
    sourceReadList.setSources(sourceReads);
    return sourceReadList;
  }

  public SourceRead getSource(SourceIdRequestBody sourceIdRequestBody) {
    final String sourceId = sourceIdRequestBody.getSourceId().toString();
    final StandardSource standardSource;
    try {
      standardSource =
          configPersistence.getConfig(
              PersistenceConfigType.STANDARD_SOURCE, sourceId, StandardSource.class);
    } catch (ConfigNotFoundException e) {
      throw new KnownException(404, e.getMessage(), e);
    } catch (JsonValidationException e) {
      throw new KnownException(422, e.getMessage(), e);
    }
    return toSourceRead(standardSource);
  }

  private static SourceRead toSourceRead(StandardSource standardSource) {
    final SourceRead sourceRead = new SourceRead();
    sourceRead.setSourceId(standardSource.getSourceId());
    sourceRead.setName(standardSource.getName());

    return sourceRead;
  }
}
