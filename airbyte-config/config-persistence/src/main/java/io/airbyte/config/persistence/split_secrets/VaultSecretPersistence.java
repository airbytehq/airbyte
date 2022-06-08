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

  /**
   * Constructor for testing
   */
  protected VaultSecretPersistence(final String address, final String prefix, final String token) {
    this.vault = Exceptions.toRuntime(() -> getVaultClient(address, token));
    this.pathPrefix = prefix;
  }

  @Override
  public Optional<String> read(final SecretCoordinate coordinate) {
    try {
      final var response = vault.logical().read(pathPrefix + coordinate.getFullCoordinate());
      final var restResponse = response.getRestResponse();
      final var responseCode = restResponse.getStatus();
      if (responseCode != 200) {
        log.error("failed on read. Response code: " + responseCode);
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
   * This creates a vault client using a vault agent which uses AWS IAM for auth using engine version 2.
   */
  private static Vault getVaultClient(final String address) throws VaultException {
    final var config = new VaultConfig()
        .address(address)
        .engineVersion(2)
        .build();
    return new Vault(config);
  }

  /**
   * Vault client for testing
   */
  private static Vault getVaultClient(final String address, final String token) throws VaultException {
    final var config = new VaultConfig()
        .address(address)
        .token(token)
        .engineVersion(2)
        .build();
    return new Vault(config);
  }
}
