package io.airbyte.integrations.destination.redshift;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.ssh.SshTunnel.TunnelMethod;
import java.io.IOException;
import java.nio.file.Path;

/*
 * SshKeyRedshiftInsertDestinationAcceptanceTest runs basic Redshift Destination Tests using the SQL Insert
 * mechanism for upload of data and "key" authentication for the SSH bastion configuration.
 *
 * Check Google Secrets for a new secret config called "SECRET_DESTINATION-REDSHIFT-BASTION__KEY". Place the contents
 * in your secrets directory under 'redshift-bastion-key-pair.pem'
 */
public class SshKeyRedshiftInsertDestinationAcceptanceTest extends SshRedshiftDestinationBaseAcceptanceTest {

  @Override
  public TunnelMethod getTunnelMethod() {
    return TunnelMethod.SSH_KEY_AUTH;
  }

  public JsonNode getStaticConfig() throws IOException {
    final Path configPath = Path.of("secrets/config.json");
    final String configAsString = IOs.readFile(configPath);
    return Jsons.deserialize(configAsString);
  }
}
