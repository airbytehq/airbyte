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
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class VaultSecretPersistence implements SecretPersistence {

  final VaultConfig rootConfig = new VaultConfig().address("http://vault:8400")
      // .nameSpace("secret/test")
      // .token("3c9fd6be-7bc2-9d1f-6fb3-cd746c0fc4e8")
      .build();
  final Vault vault = new Vault(rootConfig);

  public VaultSecretPersistence() throws VaultException {
    log.error("_____________________________: Unsealing");
    // final SealResponse sealResponse = vault.seal()/* .withNameSpace("secret/test")
    // */.unseal("3c9fd6be-7bc2-9d1f-6fb3-cd746c0fc4e8", true);
    // log.error("_____________________________: Seal: " + sealResponse.getSealed());
  }

  @Override
  public Optional<String> read(final SecretCoordinate coordinate) {
    try {
      // final AuthResponse response = vault.auth().createToken(new
      // TokenRequest().id(UUID.fromString("00000000-0000-0000-0000-000000000000")));
      // response.getAuthClientToken()
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
