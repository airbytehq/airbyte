/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.postgres.PostgresTestDatabase.BaseImage;
import java.util.HashSet;
import org.junit.jupiter.api.Disabled;

@Disabled("Disabled after DV2 migration. Re-enable with fixtures updated to DV2.")
public class PostgresDestinationAcceptanceTest extends AbstractPostgresDestinationAcceptanceTest {

  private PostgresTestDatabase testDb;

  @Override
  protected JsonNode getConfig() {
    return testDb.configBuilder()
        .with("schema", "public")
        .withDatabase()
        .withResolvedHostAndPort()
        .withCredentials()
        .withoutSsl()
        .build();
  }

  @Override
  protected PostgresTestDatabase getTestDb() {
    return testDb;
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv, final HashSet<String> TEST_SCHEMAS) {
    testDb = PostgresTestDatabase.in(BaseImage.POSTGRES_13);
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    testDb.close();
  }

}
