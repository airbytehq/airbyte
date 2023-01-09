/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static io.airbyte.db.PostgresUtils.getCertificate;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.PostgresUtils;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.integrations.util.HostPortResolver;
import java.util.List;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.DockerImageName;

public abstract class AbstractCdcPostgresSourceSslAcceptanceTest extends CdcPostgresSourceAcceptanceTest {

  protected static final String PASSWORD = "Passw0rd";
  protected static PostgresUtils.Certificate certs;

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    container = new PostgreSQLContainer<>(DockerImageName.parse("postgres:bullseye")
        .asCompatibleSubstituteFor("postgres"))
            .withCommand("postgres -c wal_level=logical");
    container.start();

    certs = getCertificate(container);
    /**
     * The publication is not being set as part of the config and because of it
     * {@link io.airbyte.integrations.source.postgres.PostgresSource#isCdc(JsonNode)} returns false, as
     * a result no test in this class runs through the cdc path.
     */
    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "CDC")
        .put("replication_slot", SLOT_NAME_BASE)
        .put("publication", PUBLICATION)
        .put("initial_waiting_seconds", INITIAL_WAITING_SECONDS)
        .build());
    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, HostPortResolver.resolveHost(container))
        .put(JdbcUtils.PORT_KEY, HostPortResolver.resolvePort(container))
        .put(JdbcUtils.DATABASE_KEY, container.getDatabaseName())
        .put(JdbcUtils.SCHEMAS_KEY, List.of(NAMESPACE))
        .put(JdbcUtils.USERNAME_KEY, container.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, container.getPassword())
        .put("replication_method", replicationMethod)
        .put(JdbcUtils.SSL_KEY, true)
        .put("ssl_mode", getCertificateConfiguration())
        .put("is_test", true)
        .build());

    try (final DSLContext dslContext = DSLContextFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.POSTGRESQL.getDriverClassName(),
        String.format(DatabaseDriver.POSTGRESQL.getUrlFormatString(),
            container.getHost(),
            container.getFirstMappedPort(),
            config.get(JdbcUtils.DATABASE_KEY).asText()),
        SQLDialect.POSTGRES)) {
      final Database database = new Database(dslContext);

      /**
       * cdc expects the INCREMENTAL tables to contain primary key checkout
       * {@link io.airbyte.integrations.source.postgres.PostgresSource#removeIncrementalWithoutPk(AirbyteStream)}
       */
      database.query(ctx -> {
        ctx.execute("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");
        ctx.execute("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
        ctx.execute("CREATE TABLE starships(id INTEGER, name VARCHAR(200));");
        ctx.execute("INSERT INTO starships (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');");
        ctx.execute("SELECT pg_create_logical_replication_slot('" + SLOT_NAME_BASE + "', 'pgoutput');");
        ctx.execute("CREATE PUBLICATION " + PUBLICATION + " FOR ALL TABLES;");
        return null;
      });
    }
  }

  public abstract ImmutableMap getCertificateConfiguration();

}
