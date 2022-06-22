/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets.test_cases;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.config.persistence.split_secrets.SecretCoordinate;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.config.persistence.split_secrets.SecretsHelpersTest;
import io.airbyte.config.persistence.split_secrets.SecretsTestCase;
import java.util.Map;
import java.util.function.Consumer;

public class NestedObjectTestCase implements SecretsTestCase {

  @Override
  public String getName() {
    return "nested_object";
  }

  @Override
  public Map<SecretCoordinate, String> getFirstSecretMap() {
    return Map.of(
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(1), 1), "hunter1",
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(0), 1), "hunter2");
  }

  @Override
  public Map<SecretCoordinate, String> getSecondSecretMap() {
    return Map.of(
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(1), 2), "hunter3",
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(0), 2), "hunter4");
  }

  @Override
  public Consumer<SecretPersistence> getPersistenceUpdater() {
    return secretPersistence -> {
      secretPersistence.write(
          new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(1), 1),
          "hunter1");
      secretPersistence.write(
          new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(0), 1),
          "hunter2");
    };
  }

  // the following helpers are for the custom test suite for evaluating updating individual secret
  // versions

  public JsonNode getUpdatedPartialConfigAfterUpdate1() {
    return Exceptions.toRuntime(() -> getNodeResource(getName(), "updated_partial_config_update1.json"));
  }

  public JsonNode getUpdatedPartialConfigAfterUpdate2() {
    return Exceptions.toRuntime(() -> getNodeResource(getName(), "updated_partial_config_update2.json"));
  }

  public JsonNode getFullConfigUpdate1() {
    return Exceptions.toRuntime(() -> getNodeResource(getName(), "full_config_update1.json"));
  }

  public JsonNode getFullConfigUpdate2() {
    return Exceptions.toRuntime(() -> getNodeResource(getName(), "full_config_update2.json"));
  }

  public Map<SecretCoordinate, String> getSecretMapAfterUpdate1() {
    return Map.of(
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(1), 2), "hunter3",
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(0), 1), "hunter2");
  }

  public Map<SecretCoordinate, String> getSecretMapAfterUpdate2() {
    return Map.of(
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(1), 2), "hunter3",
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(0), 2), "hunter4");
  }

}
