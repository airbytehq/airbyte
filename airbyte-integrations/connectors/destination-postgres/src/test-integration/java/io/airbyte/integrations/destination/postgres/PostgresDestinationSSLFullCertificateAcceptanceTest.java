/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.postgres.PostgresTestDatabase.BaseImage;
import java.util.HashSet;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

public class PostgresDestinationSSLFullCertificateAcceptanceTest extends AbstractPostgresDestinationAcceptanceTest {

  private PostgresTestDatabase testDb;
  private final StandardNameTransformer namingResolver = new StandardNameTransformer();

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
            .put("mode", "verify-ca")
            .put("ca_certificate", testDb.getCertificates().caCertificate())
            // .put("client_certificate", testDb.getCertificates().clientCertificate())
            // .put("client_key", testDb.getCertificates().clientKey())
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

  @Test
  @Disabled
  @Override
  public void testCustomDbtTransformations() {

  }

}
