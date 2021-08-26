package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import java.nio.file.Path;

/**
 * Tests an ssh tunnel wrapped around a postgres source.  Uses cloud postgres instance to
 * test this, not a local docker container database.
 */
public class PostgresSourceSSHTunnelKeyAcceptanceTest extends PostgresSourceAcceptanceTest {

  @Override
  protected void setupEnvironment(TestDestinationEnv environment) throws Exception {
  }
  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.deserialize(IOs.readFile(Path.of("secrets/postgres_source_ssh_tunnel_key_config.json")));
  }
}
