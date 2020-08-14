package io.dataline.server.fixtures;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.dataline.config.DestinationConnectionSpecification;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.PersistenceConfigType;
import java.io.File;
import java.io.IOException;
import java.util.UUID;

public class DestinationSpecificationFixtures {
  public static DestinationConnectionSpecification createDestinationConnectionSpecification(
      ConfigPersistence configPersistence) {
    final UUID destinationId = UUID.randomUUID();
    final UUID destinationSpecificationId = UUID.randomUUID();

    final File specificationFile =
        new File("../dataline-server/src/test/resources/json/TestSpecification.json");

    JsonNode specificationJson;
    try {
      specificationJson = new ObjectMapper().readTree(specificationFile);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }

    final DestinationConnectionSpecification destinationConnectionSpecification =
        new DestinationConnectionSpecification();
    destinationConnectionSpecification.setDestinationId(destinationId);
    destinationConnectionSpecification.setDestinationSpecificationId(destinationSpecificationId);
    destinationConnectionSpecification.setSpecification(specificationJson.toString());

    configPersistence.writeConfig(
        PersistenceConfigType.DESTINATION_CONNECTION_SPECIFICATION,
        destinationSpecificationId.toString(),
        destinationConnectionSpecification);

    return destinationConnectionSpecification;
  }
}
