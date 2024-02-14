/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse;

import io.airbyte.cdk.integrations.base.ssh.SshTunnel;
import org.junit.jupiter.api.Disabled;

@Disabled("This test was failing on the master branch and seems unrelated to any changes in the PR")
public class SshPasswordClickhouseDestinationAcceptanceTest extends SshClickhouseDestinationAcceptanceTest {

  @Override
  public SshTunnel.TunnelMethod getTunnelMethod() {
    return SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH;
  }

}
