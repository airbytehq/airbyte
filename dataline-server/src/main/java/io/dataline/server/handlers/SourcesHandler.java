package io.dataline.server.handlers;

import io.dataline.api.model.SourceIdRequestBody;
import io.dataline.api.model.SourceRead;
import io.dataline.api.model.SourceReadList;
import io.dataline.config.StandardSource;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.PersistenceConfigType;
import java.util.List;
import java.util.stream.Collectors;

public class SourcesHandler {
  private final ConfigPersistence configPersistence;

  public SourcesHandler(ConfigPersistence configPersistence) {
    this.configPersistence = configPersistence;
  }

  public SourceReadList listSources() {
    final List<SourceRead> sourceReads =
        configPersistence
            .getConfigs(PersistenceConfigType.STANDARD_SOURCE, StandardSource.class)
            .stream()
            .map(SourcesHandler::standardSourceToSourceRead)
            .collect(Collectors.toList());

    final SourceReadList sourceReadList = new SourceReadList();
    sourceReadList.setSources(sourceReads);
    return sourceReadList;
  }

  public SourceRead getSource(SourceIdRequestBody sourceIdRequestBody) {
    final String sourceId = sourceIdRequestBody.getSourceId().toString();
    final StandardSource standardSource =
        configPersistence.getConfig(
            PersistenceConfigType.STANDARD_SOURCE, sourceId, StandardSource.class);
    return standardSourceToSourceRead(standardSource);
  }

  private static SourceRead standardSourceToSourceRead(StandardSource standardSource) {
    final SourceRead sourceRead = new SourceRead();
    sourceRead.setSourceId(standardSource.getSourceId());
    sourceRead.setName(standardSource.getName());

    return sourceRead;
  }
}
