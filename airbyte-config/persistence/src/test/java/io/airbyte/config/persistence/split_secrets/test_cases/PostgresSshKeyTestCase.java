/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets.test_cases;

import io.airbyte.config.persistence.split_secrets.SecretCoordinate;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.config.persistence.split_secrets.SecretsHelpersTest;
import io.airbyte.config.persistence.split_secrets.SecretsTestCase;
import java.util.Map;
import java.util.function.Consumer;

public class PostgresSshKeyTestCase implements SecretsTestCase {

  @Override
  public String getName() {
    return "postgres_ssh_key";
  }

  @Override
  public Map<SecretCoordinate, String> getFirstSecretMap() {
    return Map.of(
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(0), 1), "hunter1",
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(1), 1), "hunter2");
  }

  @Override
  public Map<SecretCoordinate, String> getSecondSecretMap() {
    return Map.of(
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(0), 2), "hunter3",
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(1), 2), "hunter4");
  }

  @Override
  public Consumer<SecretPersistence> getPersistenceUpdater() {
    return secretPersistence -> {
      secretPersistence.write(
          new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(0), 1),
          "hunter1");
      secretPersistence.write(
          new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(1), 1),
          "hunter2");
    };
  }

}
