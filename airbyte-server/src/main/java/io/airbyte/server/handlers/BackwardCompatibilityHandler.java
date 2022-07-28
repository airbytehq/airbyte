/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static io.airbyte.server.constants.DockerImageName.MYSQL_DOCKER_IMAGES;
import static io.airbyte.server.constants.DockerImageName.MYSQL_REPLICATION_ERRORS;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Set;

public class BackwardCompatibilityHandler {

  public void updateSourceConnectionForBackwardCompatibility(String dockerImageName,
                                                             SourceConnection sourceConnection,
                                                             JsonNode configuration,
                                                             JsonNode connectionSpecification,
                                                             Set<String> validationResult,
                                                             ConfigRepository configRepository)
      throws JsonValidationException, IOException, ConfigNotFoundException {

    if (MYSQL_DOCKER_IMAGES.contains(dockerImageName)) {
      if (validationResult.stream().anyMatch(MYSQL_REPLICATION_ERRORS::contains)) {
        handleMySqlReplicationMethod(sourceConnection, configuration, connectionSpecification);
        configRepository.writeSourceConnectionNoSecrets(sourceConnection);
      }
    }
  }

  private void handleMySqlReplicationMethod(SourceConnection sourceConnection, JsonNode configuration, JsonNode connectionSpecification)
      throws JsonValidationException, IOException {
    final JsonNode properties = connectionSpecification.get("properties");
    final JsonNode clone = Jsons.clone(configuration);

    if (properties.get("replication_method").isObject() && configuration.get("replication_method").isTextual()) {
      final String replicationMethod = configuration.get("replication_method").asText();
      final JsonNode replicationMethodNode = Jsons.jsonNode(ImmutableMap.builder()
          .put("method", replicationMethod)
          .build());
      ((ObjectNode) clone).put("replication_method", replicationMethodNode);
    } else if (properties.get("replication_method").isObject() && configuration.get("replication_method").isObject()) {
      final String replicationMethod = configuration.get("replication_method").get("method").asText();
      ((ObjectNode) clone).put("replication_method", replicationMethod);
    }
    sourceConnection.setConfiguration(clone);
  }

}
