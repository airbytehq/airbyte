/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.ssh;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.ssh.SshTunnel.TunnelMethod;
import java.nio.charset.StandardCharsets;
import java.security.KeyPair;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.util.Arrays;
import org.apache.sshd.client.SshClient;
import org.apache.sshd.client.session.ClientSession;
import org.apache.sshd.common.util.security.SecurityUtils;
import org.apache.sshd.common.util.security.eddsa.EdDSASecurityProviderRegistrar;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

class SshTunnelTest {

  private static final String SSH_ED25519_PRIVATE_KEY = "-----BEGIN OPENSSH PRIVATE KEY-----\\n"
      + "b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW\\n"
      + "QyNTUxOQAAACDbBP+5jmEtjh1JvhzVQsvvTC2IQrX6P68XzrV7ZbnGsQAAAKBgtw9/YLcP\\n"
      + "fwAAAAtzc2gtZWQyNTUxOQAAACDbBP+5jmEtjh1JvhzVQsvvTC2IQrX6P68XzrV7ZbnGsQ\\n"
      + "AAAEAaKYn22N1O78HfdG22C7hcG2HiezKMzlq4JTdgYG1DstsE/7mOYS2OHUm+HNVCy+9M\\n"
      + "LYhCtfo/rxfOtXtlucaxAAAAHHRmbG9yZXNfZHQwMUB0ZmxvcmVzX2R0MDEtUEMB\\n"
      + "-----END OPENSSH PRIVATE KEY-----";
  private static final String SSH_RSA_PRIVATE_KEY = "-----BEGIN OPENSSH PRIVATE KEY-----\\n"
      + "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\\n"
      + "-----END OPENSSH PRIVATE KEY-----";
  private static final String HOST_PORT_CONFIG =
      "{\"ssl\":true,\"host\":\"fakehost.com\",\"port\":5432,\"schema\":\"public\",\"database\":\"postgres\",\"password\":\"<dummyPassword>\",\"username\":\"postgres\",\"tunnel_method\":{\"ssh_key\":\""
          + "%s"
          + "\",\"tunnel_host\":\"faketunnel.com\",\"tunnel_port\":22,\"tunnel_user\":\"ec2-user\",\"tunnel_method\":\"SSH_KEY_AUTH\"}}";

  private static final String URL_CONFIG_WITH_PORT =
      "{\"ssl\":true,\"endpoint\":\"http://fakehost.com:9090/service\",\"password\":\"<dummyPassword>\",\"username\":\"restuser\",\"tunnel_method\":{\"ssh_key\":\""
          + "%s"
          + "\",\"tunnel_host\":\"faketunnel.com\",\"tunnel_port\":22,\"tunnel_user\":\"ec2-user\",\"tunnel_method\":\"SSH_KEY_AUTH\"}}";

  private static final String URL_CONFIG_NO_PORT =
      "{\"ssl\":true,\"endpoint\":\"http://fakehost.com/service\",\"password\":\"<dummyPassword>\",\"username\":\"restuser\",\"tunnel_method\":{\"ssh_key\":\""
          + "%s"
          + "\",\"tunnel_host\":\"faketunnel.com\",\"tunnel_port\":22,\"tunnel_user\":\"ec2-user\",\"tunnel_method\":\"SSH_KEY_AUTH\"}}";

  /**
   * This test verifies that OpenSsh correctly replaces values in connector configuration in a spec
   * with host/port config and in a spec with endpoint URL config
   *
   * @param configString
   * @throws Exception
   */
  @ParameterizedTest
  @ValueSource(strings = {HOST_PORT_CONFIG, URL_CONFIG_WITH_PORT, URL_CONFIG_NO_PORT})
  public void testConfigInTunnel(final String configString) throws Exception {
    final JsonNode config = (new ObjectMapper()).readTree(String.format(configString, SSH_RSA_PRIVATE_KEY));
    String endPointURL = Jsons.getStringOrNull(config, "endpoint");
    final SshTunnel sshTunnel = new SshTunnel(
        config,
        endPointURL == null ? Arrays.asList(new String[] {"host"}) : null,
        endPointURL == null ? Arrays.asList(new String[] {"port"}) : null,
        endPointURL == null ? null : "endpoint",
        endPointURL,
        TunnelMethod.SSH_KEY_AUTH,
        "faketunnel.com",
        22,
        "tunnelUser",
        SSH_RSA_PRIVATE_KEY,
        "tunnelUserPassword",
        endPointURL == null ? "fakeHost.com" : null,
        endPointURL == null ? 5432 : 0) {

      @Override
      ClientSession openTunnel(final SshClient client) {
        tunnelLocalPort = 8080;
        return null; // Prevent tunnel from attempting to connect
      }

    };

    final JsonNode configInTunnel = sshTunnel.getConfigInTunnel();
    if (endPointURL == null) {
      assertTrue(configInTunnel.has("port"));
      assertTrue(configInTunnel.has("host"));
      assertFalse(configInTunnel.has("endpoint"));
      assertEquals(8080, configInTunnel.get("port").asInt());
      assertEquals("127.0.0.1", configInTunnel.get("host").asText());
    } else {
      assertFalse(configInTunnel.has("port"));
      assertFalse(configInTunnel.has("host"));
      assertTrue(configInTunnel.has("endpoint"));
      assertEquals("http://127.0.0.1:8080/service", configInTunnel.get("endpoint").asText());
    }
  }

  /**
   * This test verifies that SshTunnel correctly extracts private key pairs from keys formatted as
   * EdDSA and OpenSSH
   *
   * @param privateKey
   * @throws Exception
   */
  @ParameterizedTest
  @ValueSource(strings = {SSH_ED25519_PRIVATE_KEY, SSH_RSA_PRIVATE_KEY})
  public void getKeyPair(final String privateKey) throws Exception {
    final JsonNode config = (new ObjectMapper()).readTree(String.format(HOST_PORT_CONFIG, privateKey));
    final SshTunnel sshTunnel = new SshTunnel(
        config,
        Arrays.asList(new String[] {"host"}),
        Arrays.asList(new String[] {"port"}),
        null,
        null,
        TunnelMethod.SSH_KEY_AUTH,
        "faketunnel.com",
        22,
        "tunnelUser",
        privateKey,
        "tunnelUserPassword",
        "fakeHost.com",
        5432) {

      @Override
      ClientSession openTunnel(final SshClient client) {
        return null; // Prevent tunnel from attempting to connect
      }

    };

    final KeyPair authKeyPair = sshTunnel.getPrivateKeyPair();
    assertNotNull(authKeyPair);// actually, all is good if there is no exception on previous line
  }

  /**
   * This test verifies that 'net.i2p.crypto:eddsa' is present and EdDSA is supported. If
   * net.i2p.crypto:eddsa will be removed from project, then will be thrown: generator not correctly
   * initialized
   *
   * @throws Exception
   */
  @Test
  public void edDsaIsSupported() throws Exception {
    final var keygen = SecurityUtils.getKeyPairGenerator("EdDSA");
    final String message = "hello world";
    final KeyPair keyPair = keygen.generateKeyPair();

    final byte[] signedMessage = sign(keyPair.getPrivate(), message);

    assertTrue(new EdDSASecurityProviderRegistrar().isSupported());
    assertTrue(verify(keyPair.getPublic(), signedMessage, message));
  }

  private byte[] sign(final PrivateKey privateKey, final String message) throws Exception {
    final var signature = SecurityUtils.getSignature("NONEwithEdDSA");
    signature.initSign(privateKey);

    signature.update(message.getBytes(StandardCharsets.UTF_8));

    return signature.sign();
  }

  private boolean verify(final PublicKey publicKey, final byte[] signed, final String message)
      throws Exception {
    final var signature = SecurityUtils.getSignature("NONEwithEdDSA");
    signature.initVerify(publicKey);

    signature.update(message.getBytes(StandardCharsets.UTF_8));

    return signature.verify(signed);
  }

}
