/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static io.airbyte.server.constants.DockerImageName.MSSQL_DOCKER_IMAGES;
import static io.airbyte.server.constants.DockerImageName.MYSQL_DOCKER_IMAGES;
import static io.airbyte.server.constants.DockerImageName.MYSQL_REPLICATION_ERRORS;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.SourceConnection;
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
      throws JsonValidationException, IOException {

    if (MYSQL_DOCKER_IMAGES.contains(dockerImageName)) {
      if (!validationResult.isEmpty() && validationResult.stream().anyMatch(MYSQL_REPLICATION_ERRORS::contains)) {
        handleMySqlReplicationMethod(sourceConnection, configuration, connectionSpecification, configRepository);
      }
    }
    if (MSSQL_DOCKER_IMAGES.contains(dockerImageName)) {
      handleMsSqlReplicationMethod(sourceConnection, configuration, connectionSpecification, configRepository);
    }
  }

  private void handleMySqlReplicationMethod(SourceConnection sourceConnection,
                                            JsonNode configuration,
                                            JsonNode connectionSpecification,
                                            ConfigRepository configRepository)
      throws JsonValidationException, IOException {
    final JsonNode properties = connectionSpecification.get("properties");
    final JsonNode clone = Jsons.clone(configuration);

    modifyMySqlSourceConfigReplication(configuration, properties, (ObjectNode) clone);
    saveModifiedSourceConfig(sourceConnection, configuration, configRepository, clone);
  }

  private void modifyMySqlSourceConfigReplication(JsonNode configuration, JsonNode properties, ObjectNode clone) {
    if (properties.get("replication_method").isObject() && configuration.get("replication_method").isTextual()) {
      final String replicationMethod = configuration.get("replication_method").asText();
      final JsonNode replicationMethodNode = Jsons.jsonNode(ImmutableMap.builder()
          .put("method", replicationMethod)
          .build());
      clone.put("replication_method", replicationMethodNode);
    } else if (properties.get("replication_method").isObject() && configuration.get("replication_method").isObject()) {
      final String replicationMethod = configuration.get("replication_method").get("method").asText();
      clone.put("replication_method", replicationMethod);
    }
  }

  private void handleMsSqlReplicationMethod(SourceConnection sourceConnection,
                                            JsonNode configuration,
                                            JsonNode connectionSpecification,
                                            ConfigRepository configRepository)
      throws JsonValidationException, IOException {
    final JsonNode clone = Jsons.clone(configuration);

    final JsonNode specReplicationMethod = connectionSpecification.get("properties").get("replication_method");
    final JsonNode configReplicationMethod = configuration.get("replication_method");
    final JsonNode specReplication = connectionSpecification.get("properties").get("replication");
    final JsonNode configReplication = configuration.get("replication");

    modifyMsSqlSourceConfigReplication(configuration, (ObjectNode) clone, specReplicationMethod, configReplicationMethod, specReplication,
        configReplication);
    saveModifiedSourceConfig(sourceConnection, configuration, configRepository, clone);
  }

  private void modifyMsSqlSourceConfigReplication(JsonNode configuration,
                                                  ObjectNode clone,
                                                  JsonNode specReplicationMethod,
                                                  JsonNode configReplicationMethod,
                                                  JsonNode specReplication,
                                                  JsonNode configReplication) {
    if (specReplicationMethod != null && configReplicationMethod == null && configReplication != null && configReplication.isObject()) {
      final ObjectNode replication = (ObjectNode) configuration.get("replication");
      final JsonNode replicationType = replication.get("replication_type");
      if (replicationType!=null) {
        final ObjectNode replicationClone = Jsons.clone(replication);
        replicationClone.remove("replication_type");
        replicationClone.put("method", replicationType);
        clone.remove("replication");
        clone.put("replication_method", replicationClone);
      }
    } else if (specReplication != null && configReplication == null && configReplicationMethod != null && configReplicationMethod.isObject()) {
      final ObjectNode replicationMethod = (ObjectNode) configuration.get("replication_method");
      final JsonNode method = replicationMethod.get("method");
      if (method!=null){
        final ObjectNode replicationMethodClone = Jsons.clone(replicationMethod);
        replicationMethodClone.remove("method");
        replicationMethodClone.put("replication_type", method);
        clone.remove("replication_method");
        clone.put("replication", replicationMethodClone);
      }
    }
  }

  private void saveModifiedSourceConfig(SourceConnection sourceConnection, JsonNode configuration, ConfigRepository configRepository, JsonNode clone)
      throws JsonValidationException, IOException {
    if (!clone.equals(configuration)) {
      sourceConnection.setConfiguration(clone);
      configRepository.writeSourceConnectionNoSecrets(sourceConnection);
    }
  }

}
