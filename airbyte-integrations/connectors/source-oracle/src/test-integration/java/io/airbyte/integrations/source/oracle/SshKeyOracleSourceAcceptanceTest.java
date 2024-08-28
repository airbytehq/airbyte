/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle;

import io.airbyte.cdk.integrations.base.ssh.SshTunnel;
import org.junit.jupiter.api.Disabled;

@Disabled
public class SshKeyOracleSourceAcceptanceTest extends AbstractSshOracleSourceAcceptanceTest {

  @Override
  public SshTunnel.TunnelMethod getTunnelMethod() {
    return SshTunnel.TunnelMethod.SSH_KEY_AUTH;
  }

}
