/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets.test_cases;

import io.airbyte.config.persistence.split_secrets.SecretCoordinate;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.config.persistence.split_secrets.SecretsTestCase;
import java.util.Map;
import java.util.function.Consumer;

public class OptionalPasswordTestCase implements SecretsTestCase {

  @Override
  public String getName() {
    return "optional_password";
  }

  @Override
  public Map<SecretCoordinate, String> getFirstSecretMap() {
    return Map.of();
  }

  @Override
  public Map<SecretCoordinate, String> getSecondSecretMap() {
    return Map.of();
  }

  @Override
  public Consumer<SecretPersistence> getPersistenceUpdater() {
    return secretPersistence -> {};
  }

}
