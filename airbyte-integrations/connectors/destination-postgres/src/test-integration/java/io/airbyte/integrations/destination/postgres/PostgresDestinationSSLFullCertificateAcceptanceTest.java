/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.integrations.destination.postgres.PostgresTestDatabase.BaseImage;
import java.util.HashSet;
import org.junit.jupiter.api.Disabled;

@Disabled("Disabled after DV2 migration. Re-enable with fixtures updated to DV2.")
public class PostgresDestinationSSLFullCertificateAcceptanceTest extends AbstractPostgresDestinationAcceptanceTest {

  private PostgresTestDatabase testDb;

  @Override
  protected String getImageName() {
    return "airbyte/destination-postgres:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return testDb.configBuilder()
        .with("schema", "public")
        .withDatabase()
        .withResolvedHostAndPort()
        .withCredentials()
        .withSsl(ImmutableMap.builder()
            .put("mode", "verify-ca") // verify-full will not work since the spawned container is only allowed for 127.0.0.1/32 CIDRs
            .put("ca_certificate", testDb.getCertificates().caCertificate())
            .build())
        .build();
  }

  @Override
  protected PostgresTestDatabase getTestDb() {
    return testDb;
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv, HashSet<String> TEST_SCHEMAS) throws Exception {
    testDb = PostgresTestDatabase.in(BaseImage.POSTGRES_12, PostgresTestDatabase.ContainerModifier.CERT);
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws Exception {
    testDb.close();
  }

  @Disabled("Custom DBT does not have root certificate created in the Postgres container.")
  public void testCustomDbtTransformations() throws Exception {
    super.testCustomDbtTransformations();
  }

}
