package io.dataline.server.helpers;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.PersistenceConfigType;
import java.io.File;
import java.io.IOException;
import java.util.UUID;

public class SourceImplementationHelpers {
  public static SourceConnectionImplementation generateSourceImplementationMock(
      ConfigPersistence configPersistence, UUID sourceSpecificationId) {
    final UUID workspaceId = UUID.randomUUID();
    final UUID sourceImplementationId = UUID.randomUUID();

    JsonNode implementationJson = getTestImplementationJson();

    final SourceConnectionImplementation sourceConnectionImplementation =
        new SourceConnectionImplementation();
    sourceConnectionImplementation.setWorkspaceId(workspaceId);
    sourceConnectionImplementation.setSourceSpecificationId(sourceSpecificationId);
    sourceConnectionImplementation.setSourceImplementationId(sourceImplementationId);
    sourceConnectionImplementation.setConfiguration(implementationJson.toString());

    return sourceConnectionImplementation;
  }

  public static JsonNode getTestImplementationJson() {
    final File implementationFile =
        new File("../dataline-server/src/test/resources/json/TestImplementation.json");

    try {
      return new ObjectMapper().readTree(implementationFile);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }
}
