/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.PostgresUtils;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.cdk.testutils.PostgresTestDatabase;
import io.airbyte.commons.json.Jsons;
import java.util.List;

public abstract class AbstractCdcPostgresSourceSslAcceptanceTest extends CdcPostgresSourceAcceptanceTest {

  protected static final String PASSWORD = "Passw0rd";
  protected static PostgresUtils.Certificate certs;

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    testdb = PostgresTestDatabase.make(getServerImageName(), "withWalLevelLogical", "withCert");
    certs = testdb.getCertificate();
    slotName = testdb.withSuffix("debezium_slot");
    publication = testdb.withSuffix("publication");
    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "CDC")
        .put("replication_slot", slotName)
        .put("publication", publication)
        .put("initial_waiting_seconds", INITIAL_WAITING_SECONDS)
        .build());
    config = Jsons.jsonNode(testdb.makeConfigBuilder()
        .put(JdbcUtils.SCHEMAS_KEY, List.of(NAMESPACE))
        .put("replication_method", replicationMethod)
        .put(JdbcUtils.SSL_KEY, true)
        .put("ssl_mode", getCertificateConfiguration())
        .put("is_test", true)
        .build());

    testdb.database.query(ctx -> {
      ctx.execute("CREATE TABLE id_and_name(id INTEGER primary key, name VARCHAR(200));");
      ctx.execute("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
      ctx.execute("CREATE TABLE starships(id INTEGER primary key, name VARCHAR(200));");
      ctx.execute("INSERT INTO starships (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');");
      ctx.execute("SELECT pg_create_logical_replication_slot('" + slotName + "', 'pgoutput');");
      ctx.execute("CREATE PUBLICATION " + publication + " FOR ALL TABLES;");
      return null;
    });
  }

  protected abstract String getServerImageName();

  public abstract ImmutableMap getCertificateConfiguration();

}
