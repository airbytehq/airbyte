/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.integrations.destination.postgres.PostgresDestination;
import io.airbyte.integrations.destination.postgres.PostgresTestDatabase;
import io.airbyte.integrations.destination.postgres.PostgresTestDatabase.BaseImage;
import javax.sql.DataSource;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;

// TODO: This test is added to ensure coverage missed by disabling DATs. Redundant when DATs
// enabled.
public class PostgresStrictEncryptTypingDedupingTest extends AbstractPostgresTypingDedupingTest {

  protected static PostgresTestDatabase testContainer;

  @BeforeAll
  public static void setupPostgres() {
    // Postgres-13 is alpine image and SSL conf is failing to load, intentionally using 12:bullseye
    testContainer = PostgresTestDatabase.in(BaseImage.POSTGRES_12, PostgresTestDatabase.ContainerModifier.CERT);
  }

  @AfterAll
  public static void teardownPostgres() {
    testContainer.close();
  }

  @Override
  protected ObjectNode getBaseConfig() {
    return (ObjectNode) testContainer.configBuilder()
        .with("schema", "public")
        .withDatabase()
        .withResolvedHostAndPort()
        .withCredentials()
        .withSsl(ImmutableMap.builder()
            .put("mode", "verify-ca") // verify-full will not work since the spawned container is only allowed for 127.0.0.1/32 CIDRs
            .put("ca_certificate", testContainer.getCertificates().caCertificate())
            .build())
        .build();
  }

  @Override
  protected DataSource getDataSource(final JsonNode config) {
    // Intentionally ignore the config and rebuild it.
    // The config param has the resolved (i.e. in-docker) host/port.
    // We need the unresolved host/port since the test wrapper code is running from the docker host
    // rather than in a container.
    return new PostgresDestination().getDataSource(testContainer.configBuilder()
        .with("schema", "public")
        .withDatabase()
        .withHostAndPort()
        .withCredentials()
        .withoutSsl()
        .build());
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-postgres-strict-encrypt:dev";
  }

}
