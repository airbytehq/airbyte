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

  private static final String REPLICATION_METHOD_FIELD = "replication_method";
  private static final String REPLICATION_FIELD = "replication";
  private static final String METHOD_FIELD = "method";
  private static final String PROPERTIES_FIELD = "properties";
  private static final String REPLICATION_TYPE_FIELD = "replication_type";

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
    final JsonNode properties = connectionSpecification.get(PROPERTIES_FIELD);
    final JsonNode clone = Jsons.clone(configuration);

    modifyMySqlSourceConfigReplication(configuration, properties, (ObjectNode) clone);
    saveModifiedSourceConfig(sourceConnection, configuration, configRepository, clone);
  }

  private void modifyMySqlSourceConfigReplication(JsonNode configuration, JsonNode properties, ObjectNode clone) {
    if (properties.get(REPLICATION_METHOD_FIELD).isObject() && configuration.get(REPLICATION_METHOD_FIELD).isTextual()) {
      final String replicationMethod = configuration.get(REPLICATION_METHOD_FIELD).asText();
      final JsonNode replicationMethodNode = Jsons.jsonNode(ImmutableMap.builder()
          .put(METHOD_FIELD, replicationMethod)
          .build());
      clone.put(REPLICATION_METHOD_FIELD, replicationMethodNode);
    } else if (properties.get(REPLICATION_METHOD_FIELD).isObject() && configuration.get(REPLICATION_METHOD_FIELD).isObject()) {
      final String replicationMethod = configuration.get(REPLICATION_METHOD_FIELD).get(METHOD_FIELD).asText();
      clone.put(REPLICATION_METHOD_FIELD, replicationMethod);
    }
  }

  private void handleMsSqlReplicationMethod(SourceConnection sourceConnection,
                                            JsonNode configuration,
                                            JsonNode connectionSpecification,
                                            ConfigRepository configRepository)
      throws JsonValidationException, IOException {
    final JsonNode clone = Jsons.clone(configuration);

    final JsonNode specReplicationMethod = connectionSpecification.get(PROPERTIES_FIELD).get(REPLICATION_METHOD_FIELD);
    final JsonNode configReplicationMethod = configuration.get(REPLICATION_METHOD_FIELD);
    final JsonNode specReplication = connectionSpecification.get(PROPERTIES_FIELD).get(REPLICATION_FIELD);
    final JsonNode configReplication = configuration.get(REPLICATION_FIELD);

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
      final ObjectNode replication = (ObjectNode) configuration.get(REPLICATION_FIELD);
      final JsonNode replicationType = replication.get(REPLICATION_TYPE_FIELD);
      if (replicationType != null) {
        final ObjectNode replicationClone = Jsons.clone(replication);
        replicationClone.remove(REPLICATION_TYPE_FIELD);
        replicationClone.put(METHOD_FIELD, replicationType);
        clone.remove(REPLICATION_FIELD);
        clone.put(REPLICATION_METHOD_FIELD, replicationClone);
      }
    } else if (specReplication != null && configReplication == null && configReplicationMethod != null && configReplicationMethod.isObject()) {
      final ObjectNode replicationMethod = (ObjectNode) configuration.get(REPLICATION_METHOD_FIELD);
      final JsonNode method = replicationMethod.get(METHOD_FIELD);
      if (method != null) {
        final ObjectNode replicationMethodClone = Jsons.clone(replicationMethod);
        replicationMethodClone.remove(METHOD_FIELD);
        replicationMethodClone.put(REPLICATION_TYPE_FIELD, method);
        clone.remove(REPLICATION_METHOD_FIELD);
        clone.put(REPLICATION_FIELD, replicationMethodClone);
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
