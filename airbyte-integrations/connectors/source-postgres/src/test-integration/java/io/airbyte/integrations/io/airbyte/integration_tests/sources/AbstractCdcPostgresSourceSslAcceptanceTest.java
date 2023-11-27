/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase.BaseImage;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase.ContainerModifier;
import java.util.Map;

public abstract class AbstractCdcPostgresSourceSslAcceptanceTest extends CdcPostgresSourceAcceptanceTest {

  protected static final String PASSWORD = "Passw0rd";

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    testdb = PostgresTestDatabase.in(getServerImage(), ContainerModifier.WAL_LEVEL_LOGICAL, ContainerModifier.CERT)
        .with("CREATE TABLE id_and_name(id INTEGER primary key, name VARCHAR(200));")
        .with("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');")
        .with("CREATE TABLE starships(id INTEGER primary key, name VARCHAR(200));")
        .with("INSERT INTO starships (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');")
        .withReplicationSlot()
        .withPublicationForAllTables();
  }

  @Override
  protected JsonNode getConfig() {
    return testdb.integrationTestConfigBuilder()
        .withSchemas(NAMESPACE)
        .withSsl(getCertificateConfiguration())
        .withCdcReplication()
        .build();
  }

  protected abstract BaseImage getServerImage();

  public abstract Map<Object, Object> getCertificateConfiguration();

}
