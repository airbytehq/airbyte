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

public class ArrayTestCase implements SecretsTestCase {

  private final static String KEY1 = "key1";
  private final static String KEY2 = "key2";
  private final static String KEY3 = "key3";

  @Override
  public String getName() {
    return "array";
  }

  @Override
  public Map<SecretCoordinate, String> getFirstSecretMap() {
    return Map.of(
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(0), 1), KEY1,
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(1), 1), KEY2,
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(2), 1), KEY3,
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(3), 1), KEY1,
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(4), 1), KEY2,
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(5), 1), KEY3);
  }

  @Override
  public Map<SecretCoordinate, String> getSecondSecretMap() {
    return Map.of(
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(0), 2), "key8",
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(1), 2), "key9",
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(2), 2), "key10",
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(3), 2), "key5",
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(4), 2), "key6",
        new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(5), 2), "key7");
  }

  @Override
  public Consumer<SecretPersistence> getPersistenceUpdater() {
    return secretPersistence -> {
      secretPersistence.write(
          new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(0), 1),
          KEY1);
      secretPersistence.write(
          new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(1), 1),
          KEY2);
      secretPersistence.write(
          new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(2), 1),
          KEY3);
      secretPersistence.write(
          new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(3), 1),
          KEY1);
      secretPersistence.write(
          new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(4), 1),
          KEY2);
      secretPersistence.write(
          new SecretCoordinate(PREFIX + SecretsHelpersTest.WORKSPACE_ID + SECRET + SecretsHelpersTest.UUIDS.get(5), 1),
          KEY3);
    };
  }

}
