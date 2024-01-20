/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb;

import io.airbyte.cdk.integrations.base.ssh.SshTunnel;

public class SshPasswordMongoDbDestinationAcceptanceTest extends SshMongoDbDestinationAcceptanceTest {

  @Override
  public SshTunnel.TunnelMethod getTunnelMethod() {
    return SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH;
  }

}
