/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.opensearch;

import io.airbyte.integrations.base.ssh.SshTunnel;

public class SshKeyOpenSearchDestinationAcceptanceTest extends SshOpenSearchDestinationAcceptanceTest {

  public SshTunnel.TunnelMethod getTunnelMethod() {
    return SshTunnel.TunnelMethod.SSH_KEY_AUTH;
  }

}
