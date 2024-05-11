/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.cdk.integrations.base.ssh.SshBastionContainer;
import io.airbyte.cdk.integrations.base.ssh.SshTunnel;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.integrations.source.mysql.MySQLTestDatabase;
import io.airbyte.integrations.source.mysql.MySQLTestDatabase.BaseImage;
import io.airbyte.integrations.source.mysql.MySQLTestDatabase.ContainerModifier;
import io.airbyte.integrations.source.mysql.MySqlSource;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;

public class SshPasswordMySqlSourceAcceptanceTest extends AbstractSshMySqlSourceAcceptanceTest {

  @Override
  public Path getConfigFilePath() {
    return Path.of("secrets/ssh-pwd-repl-config.json");
  }

  @Test
  public void sshTimeoutExceptionMarkAsConfigErrorTest() throws Exception {
    try (final var testdb = MySQLTestDatabase.in(BaseImage.MYSQL_8, ContainerModifier.NETWORK)) {
      final SshBastionContainer bastion = new SshBastionContainer();
      bastion.initAndStartBastion(testdb.getContainer().getNetwork());
      final var config = testdb.integrationTestConfigBuilder()
          .withoutSsl()
          .with("tunnel_method", bastion.getTunnelMethod(SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH, true))
          .build();
      bastion.stopAndClose();

      final Source sshWrappedSource = MySqlSource.sshWrappedSource(new MySqlSource());
      final Exception exception = assertThrows(ConfigErrorException.class, () -> sshWrappedSource.discover(config));

      final String expectedMessage =
          "Timed out while opening a SSH Tunnel. Please double check the given SSH configurations and try again.";
      final String actualMessage = exception.getMessage();
      assertTrue(actualMessage.contains(expectedMessage));
    }
  }

}
