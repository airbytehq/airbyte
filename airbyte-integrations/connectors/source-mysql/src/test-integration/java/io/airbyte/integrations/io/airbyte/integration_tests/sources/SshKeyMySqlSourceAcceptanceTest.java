/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import java.nio.file.Path;
import org.junit.jupiter.api.extension.ExtendWith;
import uk.org.webcompere.systemstubs.environment.EnvironmentVariables;
import uk.org.webcompere.systemstubs.jupiter.SystemStub;
import uk.org.webcompere.systemstubs.jupiter.SystemStubsExtension;

@ExtendWith(SystemStubsExtension.class)
public class SshKeyMySqlSourceAcceptanceTest extends AbstractSshMySqlSourceAcceptanceTest {

  @SystemStub
  private EnvironmentVariables environmentVariables;

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    environmentVariables.set(EnvVariableFeatureFlags.USE_STREAM_CAPABLE_STATE, "true");
    super.setupEnvironment(environment);
  }

  @Override
  public Path getConfigFilePath() {
    return Path.of("secrets/ssh-key-repl-config.json");
  }

}
