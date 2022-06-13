/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle;

import io.airbyte.integrations.base.ssh.SshTunnel;

public class SshKeyOracleSourceAcceptanceTest extends AbstractSshOracleSourceAcceptanceTest {

  @Override
  public SshTunnel.TunnelMethod getTunnelMethod() {
    return SshTunnel.TunnelMethod.SSH_KEY_AUTH;
  }

}
