/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mariadb_columnstore;

import io.airbyte.integrations.base.ssh.SshTunnel;

public class SshKeyMariadbColumnstoreDestinationAcceptanceTest extends SshMariadbColumnstoreDestinationAcceptanceTest {

  @Override
  public SshTunnel.TunnelMethod getTunnelMethod() {
    return SshTunnel.TunnelMethod.SSH_KEY_AUTH;
  }

}
