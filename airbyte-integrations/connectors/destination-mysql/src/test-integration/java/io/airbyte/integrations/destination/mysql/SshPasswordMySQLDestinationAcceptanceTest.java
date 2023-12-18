/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql;

import io.airbyte.cdk.integrations.standardtest.destination.argproviders.DataArgumentsProvider;
import java.nio.file.Path;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ArgumentsSource;

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
  @Disabled
  @ParameterizedTest
  @ArgumentsSource(DataArgumentsProvider.class)
  public void testSyncWithNormalization(final String messagesFilename, final String catalogFilename)
      throws Exception {

  }

  /**
   * Similar to {@link #testSyncWithNormalization(String, String)}, disable the custom dbt test.
   * <p>
   * TODO: get custom dbt transformations working https://github.com/airbytehq/airbyte/issues/33547
   */
  @Override
  @Disabled
  @Test
  public void testCustomDbtTransformations() throws Exception {

  }

}
