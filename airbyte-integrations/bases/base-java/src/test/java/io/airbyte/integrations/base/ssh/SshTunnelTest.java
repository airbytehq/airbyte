package io.airbyte.integrations.base.ssh;

import static org.junit.jupiter.api.Assertions.assertTrue;

import org.apache.sshd.common.util.security.eddsa.EdDSASecurityProviderRegistrar;
import org.junit.jupiter.api.Test;

class SshTunnelTest {

  @Test
  public void edDsaIsSupported() {
    assertTrue(new EdDSASecurityProviderRegistrar().isSupported());
  }
}
