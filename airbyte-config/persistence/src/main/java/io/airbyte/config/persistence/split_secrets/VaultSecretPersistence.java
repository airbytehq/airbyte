/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import com.bettercloud.vault.Vault;
import com.bettercloud.vault.VaultConfig;
import com.bettercloud.vault.VaultException;
import io.airbyte.commons.lang.Exceptions;
import java.util.HashMap;
import java.util.Optional;
import lombok.extern.slf4j.Slf4j;

@Slf4j
final public class VaultSecretPersistence implements SecretPersistence {

  private final String secretKey = "value";
  private final Vault vault;
  private final String pathPrefix;

  public VaultSecretPersistence(final String address, final String prefix) {
    this.vault = Exceptions.toRuntime(() -> getVaultClient(address));
    this.pathPrefix = prefix;
  }

  @Override
  public Optional<String> read(final SecretCoordinate coordinate) {
    try {
      final var response = vault.logical().read(pathPrefix + coordinate.getFullCoordinate());
      log.info(pathPrefix);
      final var restResponse = response.getRestResponse();
      final var responseCode = restResponse.getStatus();
      if (responseCode != 200) {
        log.error("failed on read", response);
        return Optional.empty();
      }
      final var data = response.getData();
      return Optional.of(data.get(secretKey));
    } catch (final VaultException e) {
      return Optional.empty();
    }
  }

  @Override
  public void write(final SecretCoordinate coordinate, final String payload) {
    try {
      final var newSecret = new HashMap<String, Object>();
      newSecret.put(secretKey, payload);
      vault.logical().write(pathPrefix + coordinate.getFullCoordinate(), newSecret);
    } catch (final VaultException e) {
      log.error("failed on write", e);
    }
  }

  /**
   * This creates a vault client using a vault agent which uses AWS IAM for auth.
   */
  public static Vault getVaultClient(String address) throws VaultException {
    final var config = new VaultConfig()
        .address(address)
        .engineVersion(2)
        .build();
    return new Vault(config);
  }
}
