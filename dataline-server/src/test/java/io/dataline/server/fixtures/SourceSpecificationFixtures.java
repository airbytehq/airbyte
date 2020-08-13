package io.dataline.server.fixtures;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.dataline.config.SourceConnectionSpecification;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.PersistenceConfigType;
import java.io.File;
import java.io.IOException;
import java.util.UUID;

public class SourceSpecificationFixtures {
  public static SourceConnectionSpecification createSourceConnectionSpecification(
      ConfigPersistence configPersistence) {
    final UUID sourceId = UUID.randomUUID();
    final UUID sourceSpecificationId = UUID.randomUUID();

    final File specificationFile =
        new File("../dataline-server/src/test/resources/json/TestSpecification.json");

    JsonNode specificationJson;
    try {
      specificationJson = new ObjectMapper().readTree(specificationFile);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }

    final SourceConnectionSpecification sourceConnectionSpecification =
        new SourceConnectionSpecification();
    sourceConnectionSpecification.setSourceId(sourceId);
    sourceConnectionSpecification.setSourceSpecificationId(sourceSpecificationId);
    sourceConnectionSpecification.setSpecification(specificationJson.toString());

    configPersistence.writeConfig(
        PersistenceConfigType.SOURCE_CONNECTION_SPECIFICATION,
        sourceSpecificationId.toString(),
        sourceConnectionSpecification);

    return sourceConnectionSpecification;
  }
}
