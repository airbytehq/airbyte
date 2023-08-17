/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import io.airbyte.integrations.base.ssh.SshTunnel.TunnelMethod;
import org.junit.jupiter.api.Disabled;

@Disabled
public class SshPasswordMssqlSourceAcceptanceTest extends AbstractSshMssqlSourceAcceptanceTest {

  @Override
  public TunnelMethod getTunnelMethod() {
    return TunnelMethod.SSH_PASSWORD_AUTH;
  }

}
