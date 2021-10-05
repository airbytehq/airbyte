/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import io.airbyte.integrations.base.ssh.SshTunnel.TunnelMethod;

public class SshKeyMssqlSourceAcceptanceTest extends AbstractSshMssqlSourceAcceptanceTest {


  @Override
  public TunnelMethod getTunnelMethod() {
   return TunnelMethod.SSH_KEY_AUTH;
  }
}
