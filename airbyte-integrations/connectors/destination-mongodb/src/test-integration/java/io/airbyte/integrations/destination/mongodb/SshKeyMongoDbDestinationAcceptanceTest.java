/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb;

import io.airbyte.integrations.base.ssh.SshTunnel;
import io.airbyte.integrations.base.ssh.SshTunnel.TunnelMethod;

public class SshKeyMongoDbDestinationAcceptanceTest extends SshMongoDbDestinationAcceptanceTest {

  @Override
  public SshTunnel.TunnelMethod getTunnelMethod() {
    return TunnelMethod.SSH_KEY_AUTH;
  }

}
