/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.oceanbase;

import io.airbyte.cdk.integrations.base.ssh.SshTunnel;
import org.junit.jupiter.api.Disabled;

import java.nio.file.Path;

@Disabled
public class SshPasswordOceanBaseDestinationAcceptanceTest extends SshOceanBaseDestinationAcceptanceTest {

  @Override
  public SshTunnel.TunnelMethod getTunnelMethod() {
    return SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH;
  }
}
