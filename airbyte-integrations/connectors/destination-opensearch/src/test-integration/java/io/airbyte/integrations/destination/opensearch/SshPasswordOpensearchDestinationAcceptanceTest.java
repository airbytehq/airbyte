/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.opensearch;

import io.airbyte.integrations.base.ssh.SshTunnel;

public class SshPasswordOpensearchDestinationAcceptanceTest extends SshOpensearchDestinationAcceptanceTest {

  @Override
  public SshTunnel.TunnelMethod getTunnelMethod() {
    return SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH;
  }

}
