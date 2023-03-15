/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.ssh.SshTunnel.TunnelMethod;
import java.io.IOException;
import java.nio.file.Path;

/*
 * SshPasswordRedshiftStagingDestinationAcceptanceTest runs basic Redshift Destination Tests using
 * the S3 Staging mechanism for upload of data and "password" authentication for the SSH bastion
 * configuration.
 */
public class SshPasswordRedshiftStagingDestinationAcceptanceTest extends SshRedshiftDestinationBaseAcceptanceTest {

  @Override
  public TunnelMethod getTunnelMethod() {
    return TunnelMethod.SSH_PASSWORD_AUTH;
  }

  @Override
  public JsonNode getStaticConfig() throws IOException {
    final Path configPath = Path.of("secrets/config_staging.json");
    final String configAsString = IOs.readFile(configPath);
    return Jsons.deserialize(configAsString);
  }

}
