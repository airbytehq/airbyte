/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle;

import io.airbyte.integrations.base.ssh.SshTunnel;

public class SshPasswordOracleSourceAcceptanceTest extends AbstractSshOracleSourceAcceptanceTest {

  @Override
  public SshTunnel.TunnelMethod getTunnelMethod() {
    return SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH;
  }

}
