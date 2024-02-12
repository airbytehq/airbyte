/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import io.airbyte.cdk.integrations.base.ssh.SshTunnel.TunnelMethod;

public class SshKeyMssqlSourceAcceptanceTest extends AbstractSshMssqlSourceAcceptanceTest {

  @Override
  public TunnelMethod getTunnelMethod() {
    return TunnelMethod.SSH_KEY_AUTH;
  }

}
