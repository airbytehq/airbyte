/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dynamodb;

import io.airbyte.integrations.base.ssh.SshTunnel;

public class SshPasswordDynamodbDestinationAcceptanceTest extends SshDynamodbDestinationAcceptanceTest {

  @Override
  public SshTunnel.TunnelMethod getTunnelMethod() {
    return SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH;
  }

}
