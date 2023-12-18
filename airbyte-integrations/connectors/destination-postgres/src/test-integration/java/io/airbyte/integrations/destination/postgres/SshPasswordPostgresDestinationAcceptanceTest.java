/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

import io.airbyte.cdk.integrations.base.ssh.SshTunnel;
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.DataTypeTestArgumentProvider.TestCompatibility;
import org.junit.jupiter.api.Disabled;

public class SshPasswordPostgresDestinationAcceptanceTest extends SshPostgresDestinationAcceptanceTest {

  @Override
  public SshTunnel.TunnelMethod getTunnelMethod() {
    return SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH;
  }

  @Disabled
  @Override
  public void testIncrementalDedupeSync() throws Exception {

  }

  @Disabled
  @Override
  public void testDataTypeTestWithNormalization(String messagesFilename, String catalogFilename,
                                                TestCompatibility testCompatibility) throws Exception {

  }

  @Disabled
  @Override
  public void testSyncWithNormalization(String messagesFilename, String catalogFilename) throws Exception {

  }

  @Disabled
  @Override
  public void testCustomDbtTransformations() throws Exception {

  }
}
