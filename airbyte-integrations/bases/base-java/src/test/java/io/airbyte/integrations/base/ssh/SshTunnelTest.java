/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.ssh;

import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.security.KeyPair;
import java.security.PrivateKey;
import java.security.PublicKey;
import org.apache.sshd.common.util.security.SecurityUtils;
import org.apache.sshd.common.util.security.eddsa.EdDSASecurityProviderRegistrar;
import org.junit.jupiter.api.Test;

class SshTunnelTest {

  /**
   * This test verifies that 'net.i2p.crypto:eddsa' is present and EdDSA is supported. If
   * net.i2p.crypto:eddsa will be removed from project, then will be thrown: generator not correctly
   * initialized
   *
   * @throws Exception
   */
  @Test
  public void edDsaIsSupported() throws Exception {
    var keygen = SecurityUtils.getKeyPairGenerator("EdDSA");
    final String message = "hello world";
    KeyPair keyPair = keygen.generateKeyPair();

    byte[] signedMessage = sign(keyPair.getPrivate(), message);

    assertTrue(new EdDSASecurityProviderRegistrar().isSupported());
    assertTrue(verify(keyPair.getPublic(), signedMessage, message));
  }

  private byte[] sign(final PrivateKey privateKey, final String message) throws Exception {
    var signature = SecurityUtils.getSignature("NONEwithEdDSA");
    signature.initSign(privateKey);

    signature.update(message.getBytes(StandardCharsets.UTF_8));

    return signature.sign();
  }

  private boolean verify(final PublicKey publicKey, byte[] signed, final String message)
      throws Exception {
    var signature = SecurityUtils.getSignature("NONEwithEdDSA");
    signature.initVerify(publicKey);

    signature.update(message.getBytes(StandardCharsets.UTF_8));

    return signature.verify(signed);
  }

}
