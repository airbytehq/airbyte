/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.base.ssh.SshTunnel.TunnelMethod;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import java.io.IOException;
import java.nio.file.Path;
import org.junit.jupiter.api.Disabled;

/*
 * SshKeyRedshiftInsertDestinationAcceptanceTest runs basic Redshift Destination Tests using the SQL
 * Insert mechanism for upload of data and "key" authentication for the SSH bastion configuration.
 */
@Disabled
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
