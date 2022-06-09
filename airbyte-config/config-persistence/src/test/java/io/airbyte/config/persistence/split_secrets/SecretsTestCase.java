/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;

/**
 * Provides an easy way of accessing a set of resource files in a specific directory when testing
 * secrets-related helpers.
 */
public interface SecretsTestCase {

  String PREFIX = "airbyte_workspace_";
  String SECRET = "_secret_";

  String getName();

  Map<SecretCoordinate, String> getFirstSecretMap();

  Map<SecretCoordinate, String> getSecondSecretMap();

  Consumer<SecretPersistence> getPersistenceUpdater();

  default ConnectorSpecification getSpec() {
    return Exceptions.toRuntime(() -> new ConnectorSpecification().withConnectionSpecification(getNodeResource(getName(), "spec.json")));
  }

  default JsonNode getFullConfig() {
    return Exceptions.toRuntime(() -> getNodeResource(getName(), "full_config.json"));
  }

  default JsonNode getPartialConfig() {
    return Exceptions.toRuntime(() -> getNodeResource(getName(), "partial_config.json"));
  }

  default JsonNode getSortedPartialConfig() {
    return Exceptions.toRuntime(() -> getNodeResource(getName(), "partial_config.json"));
  }

  default JsonNode getUpdateConfig() {
    return Exceptions.toRuntime(() -> getNodeResource(getName(), "update_config.json"));
  }

  default JsonNode getUpdatedPartialConfig() {
    return Exceptions.toRuntime(() -> getNodeResource(getName(), "updated_partial_config.json"));
  }

  default JsonNode getNodeResource(final String testCase, final String fileName) throws IOException {
    return Jsons.deserialize(MoreResources.readResource(testCase + "/" + fileName));
  }

  default List<String> getExpectedSecretsPaths() throws IOException {
    return Arrays.stream(
        MoreResources.readResource(getName() + "/" + "expectedPaths")
            .trim()
            .split(";"))
        .sorted()
        .toList();
  }

}
