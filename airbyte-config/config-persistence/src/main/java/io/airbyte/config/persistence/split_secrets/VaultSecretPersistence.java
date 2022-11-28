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
import lombok.val;

@Slf4j
final public class VaultSecretPersistence implements SecretPersistence {

  private final String SECRET_KEY = "value";
  private final Vault vault;
  private final String pathPrefix;

  public VaultSecretPersistence(final String address, final String prefix, final String token) {
    this.vault = Exceptions.toRuntime(() -> getVaultClient(address, token));
    this.pathPrefix = prefix;
  }

  @Override
  public Optional<String> read(final SecretCoordinate coordinate) {
    try {
      val response = vault.logical().read(pathPrefix + coordinate.getFullCoordinate());
      val restResponse = response.getRestResponse();
      val responseCode = restResponse.getStatus();
      final Boolean isErrorResponse = responseCode / 100 != 2;

      if (isErrorResponse) {
        log.error("Vault failed on read. Response code: " + responseCode);
        return Optional.empty();
      }
      val data = response.getData();
      return Optional.of(data.get(SECRET_KEY));
    } catch (final VaultException e) {
      return Optional.empty();
    }
  }

  @Override
  public void write(final SecretCoordinate coordinate, final String payload) {
    try {
      val newSecret = new HashMap<String, Object>();
      newSecret.put(SECRET_KEY, payload);
      vault.logical().write(pathPrefix + coordinate.getFullCoordinate(), newSecret);
    } catch (final VaultException e) {
      log.error("Vault failed on write", e);
    }
  }

  private static Vault getVaultClient(final String address, final String token) throws VaultException {
    val config = new VaultConfig()
        .address(address)
        .token(token)
        .engineVersion(2)
        .build();
    return new Vault(config);
  }

}
