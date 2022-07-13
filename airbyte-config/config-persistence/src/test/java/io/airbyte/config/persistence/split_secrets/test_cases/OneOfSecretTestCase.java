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

public class OneOfSecretTestCase implements SecretsTestCase {

  @Override
  public String getName() {
    return "oneof_secret";
  }

  @Override
  public Map<SecretCoordinate, String> getFirstSecretMap() {
    return Map.of(
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(0), 1), "access_token_1",
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(1), 1), "clientId_1",
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(2), 1), "client_secret_1",
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(3), 1), "refresh_token_1");
  }

  @Override
  public Map<SecretCoordinate, String> getSecondSecretMap() {
    return Map.of(
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(0), 2), "access_token_2");
  }

  @Override
  public Consumer<SecretPersistence> getPersistenceUpdater() {
    return secretPersistence -> {
      secretPersistence.write(
          new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(0), 1),
          "access_token_1");
      secretPersistence.write(
          new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(1), 1),
          "clientId_1");
      secretPersistence.write(
          new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(2), 1),
          "client_secret_1");
      secretPersistence.write(
          new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(3), 1),
          "refresh_token_1");
    };
  }

}
