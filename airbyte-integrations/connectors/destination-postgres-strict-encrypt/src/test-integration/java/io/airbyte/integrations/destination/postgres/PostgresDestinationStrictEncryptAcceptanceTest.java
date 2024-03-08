/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.integrations.base.ssh.SshTunnel.TunnelMethod;
import io.airbyte.configoss.StandardCheckConnectionOutput.Status;
import io.airbyte.integrations.destination.postgres.PostgresTestDatabase.BaseImage;
import java.util.HashSet;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

@Disabled("Disabled after DV2 migration. Re-enable with fixtures updated to DV2.")
public class PostgresDestinationStrictEncryptAcceptanceTest extends AbstractPostgresDestinationAcceptanceTest {

  private PostgresTestDatabase testDb;

  protected static final String PASSWORD = "Passw0rd";

  @Override
  protected String getImageName() {
    return "airbyte/destination-postgres-strict-encrypt:dev";
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
  protected void setup(final TestDestinationEnv testEnv, final HashSet<String> TEST_SCHEMAS) throws Exception {
    testDb = PostgresTestDatabase.in(BaseImage.POSTGRES_12, PostgresTestDatabase.ContainerModifier.CERT);
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    testDb.close();
  }

  @Test
  void testStrictSSLUnsecuredNoTunnel() throws Exception {
    final JsonNode config = testDb.configBuilder()
        .with("schema", "public")
        .withDatabase()
        .withResolvedHostAndPort()
        .withCredentials()
        .with("tunnel_method", ImmutableMap.builder().put("tunnel_method", TunnelMethod.NO_TUNNEL.toString()).build())
        .with("ssl_mode", ImmutableMap.builder()
            .put("mode", "prefer")
            .build())
        .build();
    final var actual = runCheck(config);
    assertEquals(Status.FAILED, actual.getStatus());
    assertTrue(actual.getMessage().contains("Unsecured connection not allowed"));
  }

  @Test
  void testStrictSSLSecuredNoTunnel() throws Exception {
    final JsonNode config = testDb.configBuilder()
        .with("schema", "public")
        .withDatabase()
        .withResolvedHostAndPort()
        .withCredentials()
        .with("tunnel_method", ImmutableMap.builder().put("tunnel_method", TunnelMethod.NO_TUNNEL.toString()).build())
        .with("ssl_mode", ImmutableMap.builder()
            .put("mode", "require")
            .build())
        .build();
    final var actual = runCheck(config);
    assertEquals(Status.SUCCEEDED, actual.getStatus());
  }

  @Override
  protected boolean normalizationFromDefinition() {
    return true;
  }

  @Override
  protected boolean dbtFromDefinition() {
    return true;
  }

  @Override
  protected String getDestinationDefinitionKey() {
    return "airbyte/destination-postgres";
  }

  @Override
  protected boolean supportsInDestinationNormalization() {
    return true;
  }

  @Disabled("Custom DBT does not have root certificate created in the Postgres container.")
  public void testCustomDbtTransformations() throws Exception {
    super.testCustomDbtTransformations();
  }

}
