/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
    SshBastionContainer bastion = new SshBastionContainer();
    final Network network = Network.newNetwork();
    // set up env
    MySQLContainer<?> db = startTestContainers(bastion, network);
    config = bastion.getTunnelConfig(SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH, bastion.getBasicDbConfigBuider(db, List.of("public")));
    bastion.stopAndClose();
    Source sshWrappedSource = MySqlSource.sshWrappedSource();
    Exception exception = assertThrows(ConfigErrorException.class, () -> sshWrappedSource.discover(config));

    String expectedMessage = "Timed out while opening a SSH Tunnel. Please double check the given SSH configurations and try again.";
    String actualMessage = exception.getMessage();

    assertTrue(actualMessage.contains(expectedMessage));
  }

  private MySQLContainer startTestContainers(SshBastionContainer bastion, Network network) {
    bastion.initAndStartBastion(network);
    return initAndStartJdbcContainer(network);
  }

  private MySQLContainer initAndStartJdbcContainer(Network network) {
    MySQLContainer<?> db = new MySQLContainer<>("mysql:8.0").withNetwork(network);
    db.start();
    return db;
  }

}
