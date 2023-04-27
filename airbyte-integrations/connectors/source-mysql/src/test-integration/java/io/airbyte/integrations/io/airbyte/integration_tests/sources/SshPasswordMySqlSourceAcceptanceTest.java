/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.ssh.SshBastionContainer;
import io.airbyte.integrations.base.ssh.SshTunnel;
import io.airbyte.integrations.source.mysql.MySqlSource;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import java.nio.file.Path;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.testcontainers.containers.MySQLContainer;
import org.testcontainers.containers.Network;
import uk.org.webcompere.systemstubs.environment.EnvironmentVariables;
import uk.org.webcompere.systemstubs.jupiter.SystemStub;
import uk.org.webcompere.systemstubs.jupiter.SystemStubsExtension;

@ExtendWith(SystemStubsExtension.class)
public class SshPasswordMySqlSourceAcceptanceTest extends AbstractSshMySqlSourceAcceptanceTest {

  @SystemStub
  private EnvironmentVariables environmentVariables;

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    environmentVariables.set(EnvVariableFeatureFlags.USE_STREAM_CAPABLE_STATE, "true");
    super.setupEnvironment(environment);
  }

  @Override
  public Path getConfigFilePath() {
    return Path.of("secrets/ssh-pwd-repl-config.json");
  }

  @Test
  public void sshTimeoutExceptionMarkAsConfigErrorTest() throws Exception {
    final SshBastionContainer bastion = new SshBastionContainer();
    final Network network = Network.newNetwork();
    // set up env
    final MySQLContainer<?> db = startTestContainers(bastion, network);
    config = bastion.getTunnelConfig(SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH, bastion.getBasicDbConfigBuider(db, List.of("public")), true);
    bastion.stopAndClose();
    final Source sshWrappedSource = MySqlSource.sshWrappedSource();
    final Exception exception = assertThrows(ConfigErrorException.class, () -> sshWrappedSource.discover(config));

    final String expectedMessage = "Timed out while opening a SSH Tunnel. Please double check the given SSH configurations and try again.";
    final String actualMessage = exception.getMessage();

    assertTrue(actualMessage.contains(expectedMessage));
  }

  private MySQLContainer startTestContainers(final SshBastionContainer bastion, final Network network) {
    bastion.initAndStartBastion(network);
    return initAndStartJdbcContainer(network);
  }

  private MySQLContainer initAndStartJdbcContainer(final Network network) {
    final MySQLContainer<?> db = new MySQLContainer<>("mysql:8.0").withNetwork(network);
    db.start();
    return db;
  }

}
