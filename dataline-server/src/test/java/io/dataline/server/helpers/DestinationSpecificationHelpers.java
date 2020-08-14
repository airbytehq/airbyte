package io.dataline.server.helpers;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.dataline.config.DestinationConnectionSpecification;
import java.io.File;
import java.io.IOException;
import java.util.UUID;

public class DestinationSpecificationHelpers {
  public static DestinationConnectionSpecification generateDestinationSpecification() {
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

    return destinationConnectionSpecification;
  }
}
