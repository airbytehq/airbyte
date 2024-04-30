/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

import io.airbyte.cdk.integrations.base.ssh.SshTunnel;
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.DataTypeTestArgumentProvider.TestCompatibility;
import org.junit.jupiter.api.Disabled;

@Disabled("Disabled after DV2 migration. Re-enable with fixtures updated to DV2.")
public class SshPasswordPostgresDestinationAcceptanceTest extends SshPostgresDestinationAcceptanceTest {

  @Override
  public SshTunnel.TunnelMethod getTunnelMethod() {
    return SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH;
  }

  @Disabled("sshpass tunnel is not working with DBT container. https://github.com/airbytehq/airbyte/issues/33547")
  public void testIncrementalDedupeSync() throws Exception {
    super.testIncrementalDedupeSync();
  }

  @Disabled("sshpass tunnel is not working with DBT container. https://github.com/airbytehq/airbyte/issues/33547")
  @Override
  public void testDataTypeTestWithNormalization(String messagesFilename,
                                                String catalogFilename,
                                                TestCompatibility testCompatibility)
      throws Exception {
    super.testDataTypeTestWithNormalization(messagesFilename, catalogFilename, testCompatibility);
  }

  @Disabled("sshpass tunnel is not working with DBT container. https://github.com/airbytehq/airbyte/issues/33547")
  @Override
  public void testSyncWithNormalization(String messagesFilename, String catalogFilename) throws Exception {
    super.testSyncWithNormalization(messagesFilename, catalogFilename);
  }

  @Disabled("sshpass tunnel is not working with DBT container. https://github.com/airbytehq/airbyte/issues/33547")
  @Override
  public void testCustomDbtTransformations() throws Exception {
    super.testCustomDbtTransformations();
  }

  // TODO: Although testCustomDbtTransformationsFailure is passing, the failure is for wrong reasons.
  // See disabled tests.

}
