/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql;

import java.nio.file.Path;
import org.junit.jupiter.api.Disabled;

@Disabled
public class SshPasswordMySQLDestinationAcceptanceTest extends SshMySQLDestinationAcceptanceTest {

  @Override
  public Path getConfigFilePath() {
    return Path.of("secrets/ssh-pwd-config.json");
  }

  /**
   * Legacy normalization doesn't correctly parse the SSH password (or something). All tests involving
   * the normalization container are broken. That's (mostly) fine; DV2 doesn't rely on that container.
   */
  @Override
  @Disabled("Our dbt interface doesn't correctly parse the SSH password. Won't fix this test, since DV2 will replace normalization.")
  public void testSyncWithNormalization(final String messagesFilename, final String catalogFilename)
      throws Exception {
    super.testSyncWithNormalization(messagesFilename, catalogFilename);
  }

  /**
   * Similar to {@link #testSyncWithNormalization(String, String)}, disable the custom dbt test.
   * <p>
   * TODO: get custom dbt transformations working https://github.com/airbytehq/airbyte/issues/33547
   */
  @Override
  @Disabled("Our dbt interface doesn't correctly parse the SSH password. https://github.com/airbytehq/airbyte/issues/33547 to fix this.")
  public void testCustomDbtTransformations() throws Exception {
    super.testCustomDbtTransformations();
  }

}
