/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import io.airbyte.cdk.integrations.base.ssh.SshTunnel;
import org.junit.jupiter.api.Disabled;

@Disabled
public class SshKeyClickhouseSourceAcceptanceTest extends
    AbstractSshClickHouseSourceAcceptanceTest {

  @Override
  public SshTunnel.TunnelMethod getTunnelMethod() {
    return SshTunnel.TunnelMethod.SSH_KEY_AUTH;
  }

}
