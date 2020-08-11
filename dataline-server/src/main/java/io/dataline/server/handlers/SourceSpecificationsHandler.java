package io.dataline.server.handlers;

import io.dataline.api.model.SourceIdRequestBody;
import io.dataline.api.model.SourceSpecificationRead;
import io.dataline.config.SourceConnectionSpecification;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.PersistenceConfigType;

public class SourceSpecificationsHandler {
  private final ConfigPersistence configPersistence;

  public SourceSpecificationsHandler(ConfigPersistence configPersistence) {
    this.configPersistence = configPersistence;
  }

  public SourceSpecificationRead getSourceSpecification(SourceIdRequestBody sourceIdRequestBody) {
    final SourceConnectionSpecification sourceConnection =
        configPersistence
            .getConfigs(
                PersistenceConfigType.SOURCE_CONNECTION_SPECIFICATION,
                SourceConnectionSpecification.class)
            .stream()
            .filter(
                sourceSpecification ->
                    sourceSpecification.getSourceId().equals(sourceIdRequestBody.getSourceId()))
            .findFirst()
            .orElseThrow(() -> new RuntimeException("blah"));

    return standardSourceToSourceRead(sourceConnection);
  }

  private static SourceSpecificationRead standardSourceToSourceRead(
      SourceConnectionSpecification sourceConnectionSpecification) {
    final SourceSpecificationRead sourceSpecificationRead = new SourceSpecificationRead();
    sourceSpecificationRead.setSourceId(sourceConnectionSpecification.getSourceId());
    sourceSpecificationRead.setSourceSpecificationId(
        sourceConnectionSpecification.getSourceSpecificationId());
    sourceSpecificationRead.setConnectionSpecification(
        sourceConnectionSpecification.getSpecification());

    return sourceSpecificationRead;
  }
}
