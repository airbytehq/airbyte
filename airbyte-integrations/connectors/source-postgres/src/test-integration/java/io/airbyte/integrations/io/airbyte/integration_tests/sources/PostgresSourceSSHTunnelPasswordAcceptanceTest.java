package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import java.nio.file.Path;

public class PostgresSourceSSHTunnelPasswordAcceptanceTest extends PostgresSourceAcceptanceTest {

  @Override
  protected void setupEnvironment(TestDestinationEnv environment) throws Exception {
  }
  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.deserialize(IOs.readFile(Path.of("secrets/postgres_source_ssh_tunnel_password_config.json")));
  }

}
