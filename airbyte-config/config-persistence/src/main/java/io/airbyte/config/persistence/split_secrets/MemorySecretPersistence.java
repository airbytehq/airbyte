/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

/**
 * Map-based implementation of a {@link SecretPersistence} used for unit testing.
 */
public class MemorySecretPersistence implements SecretPersistence {

  final Map<SecretCoordinate, String> secretMap = new HashMap<>();

  @Override
  public Optional<String> read(final SecretCoordinate coordinate) {
    return Optional.ofNullable(secretMap.get(coordinate));
  }

  @Override
  public void write(final SecretCoordinate coordinate, final String payload) {
    secretMap.put(coordinate, payload);
  }

  public Map<SecretCoordinate, String> getMap() {
    return new HashMap<>(secretMap);
  }

}
