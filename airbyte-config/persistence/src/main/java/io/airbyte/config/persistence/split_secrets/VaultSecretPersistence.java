/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import com.bettercloud.vault.Vault;
import com.bettercloud.vault.VaultConfig;
import com.bettercloud.vault.VaultException;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

public class VaultSecretPersistence implements SecretPersistence {

  final VaultConfig config = new VaultConfig().address("http://vault:8200")
      .token("00000000-0000-0000-0000-000000000000")
      .build();
  final Vault vault = new Vault(config);

  public VaultSecretPersistence() throws VaultException {}

  @Override
  public Optional<String> read(final SecretCoordinate coordinate) {
    try {

      return Optional.ofNullable(vault.logical().read("secret/test").getData().get(coordinate.getFullCoordinate()));
    } catch (final VaultException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public void write(final SecretCoordinate coordinate, final String payload) throws IllegalArgumentException {
    try {
      final Map<String, String> secrets = vault.logical().read("secret/test").getData();
      secrets.put(coordinate.getFullCoordinate(), payload);
      final Map<String, Object> secretToStore = new HashMap<>();
      secrets.forEach((k, v) -> {
        secretToStore.put(k, v);
      });
      vault.logical().write("secret/test", secretToStore);
    } catch (final VaultException e) {
      throw new RuntimeException(e);
    }
  }

}
