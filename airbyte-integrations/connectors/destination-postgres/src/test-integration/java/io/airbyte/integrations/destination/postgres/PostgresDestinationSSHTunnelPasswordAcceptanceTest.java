package io.airbyte.integrations.destination.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import java.nio.file.Path;

public class PostgresDestinationSSHTunnelPasswordAcceptanceTest extends PostgresDestinationSSHTunnelKeyAcceptanceTest {

  /**
   * Configured to use an ssh tunnel with password authentication.
   */
  @Override
  protected JsonNode getConfig() {
    return Jsons.deserialize(IOs.readFile(Path.of("secrets/postgres_destination_ssh_tunnel_password_config.json")));
  }

  /**
   * Configured to fail, similar to the standard test suite.
   */
  protected JsonNode getFailCheckConfig() {
    JsonNode config = Jsons.deserialize(IOs.readFile(Path.of("secrets/postgres_destination_ssh_tunnel_password_config.json")));
    ((ObjectNode) config).put("password", "invalidvalue");
    return config;
  }


}
