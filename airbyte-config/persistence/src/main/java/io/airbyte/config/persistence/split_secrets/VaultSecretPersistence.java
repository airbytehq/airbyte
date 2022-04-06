/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import com.bettercloud.vault.VaultException;
import java.nio.ByteBuffer;
import java.util.Optional;
import java.util.UUID;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.codec.binary.Base64;
import org.springframework.vault.authentication.TokenAuthentication;
import org.springframework.vault.client.VaultEndpoint;
import org.springframework.vault.core.VaultTemplate;

@Slf4j
public class VaultSecretPersistence implements SecretPersistence {

  @Data
  class Secret {

    private final String value;

  }

  static VaultTemplate vaultTemplate = null;

  public VaultSecretPersistence() throws VaultException {
    // final UUID uuid = UUID.fromString("fd503a9f-6faa-455e-a872-fa489a400b90");
    // vault.auth().createToken(new TokenRequest().id(uuid).displayName("El testo"));
  }

  private static void init() {
    if (vaultTemplate == null) {
      try {
        vaultTemplate = new VaultTemplate(VaultEndpoint.create("0.0.0.0", 8400),
            new TokenAuthentication("cbe86853-06e2-a27e-cc5d-19e247526e00"));

        // vault.auth().loginByCert();
      } catch (final Exception e) {
        e.printStackTrace();
      }
    }
  }

  @Override
  public Optional<String> read(final SecretCoordinate coordinate) {
    try {
      init();
      return Optional.ofNullable(vaultTemplate.read("secret/test", Secret.class).getData())
          .map(Secret::getValue);

      // return
      // Optional.ofNullable(vault.logical().withNameSpace("airbyte").read("secret/test").getData().get(coordinate.getFullCoordinate()));

    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public void write(final SecretCoordinate coordinate, final String payload) throws IllegalArgumentException {
    init();
    // vaultTemplate.
    vaultTemplate.write("secret/test", new Secret(payload));
    /*
     * try { init(); log.error("____________: " + coordinate.getFullCoordinate() + " " + payload); //
     * final Map<String, String> secrets = //
     * vault.logical().withNameSpace("airbyte").read("secret/test").getData(); //
     * secrets.put(coordinate.getFullCoordinate(), payload); final Map<String, Object> secretToStore =
     * new HashMap<>(); secretToStore.put(coordinate.getFullCoordinate(), payload);
     * secretToStore.forEach((k, v) -> { log.error(k); log.error(v.toString()); }); //
     * vault.logical().withNameSpace("airbyte") final LogicalResponse response =
     * vault.logical().withNameSpace("airbyte").write("secret/test", secretToStore); //
     * log.error("___________: " + response.getDataObject().toString());
     * log.error(read(coordinate).orElse("PAS BIEN")); } catch (final VaultException e) { throw new
     * RuntimeException(e); }
     */
  }

  private static String uuidFromBase64(final String str) {
    final Base64 base64 = new Base64();
    final byte[] bytes = base64.decodeBase64(str);
    final ByteBuffer bb = ByteBuffer.wrap(bytes);
    final UUID uuid = new UUID(bb.getLong(), bb.getLong());
    return uuid.toString();
  }

}
