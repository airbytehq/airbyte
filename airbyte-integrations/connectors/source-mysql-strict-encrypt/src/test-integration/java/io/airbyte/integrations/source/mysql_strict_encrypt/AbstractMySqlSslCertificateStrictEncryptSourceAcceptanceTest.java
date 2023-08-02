/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql_strict_encrypt;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.MySqlUtils;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.ssh.SshHelpers;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.testcontainers.containers.MySQLContainer;

public abstract class AbstractMySqlSslCertificateStrictEncryptSourceAcceptanceTest extends MySqlStrictEncryptSourceAcceptanceTest {

  protected static MySqlUtils.Certificate certs;
  protected static final String PASSWORD = "Passw0rd";

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {

    container = new MySQLContainer<>("mysql:8.0");
    container.start();
    addTestData(container);
    certs = MySqlUtils.getCertificate(container, true);

    final var sslMode = getSslConfig();
    final var innerContainerAddress = SshHelpers.getInnerContainerAddress(container);
    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "STANDARD")
        .build());
    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, innerContainerAddress.left)
        .put(JdbcUtils.PORT_KEY, innerContainerAddress.right)
        .put(JdbcUtils.DATABASE_KEY, container.getDatabaseName())
        .put(JdbcUtils.USERNAME_KEY, container.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, container.getPassword())
        .put(JdbcUtils.SSL_KEY, true)
        .put(JdbcUtils.SSL_MODE_KEY, sslMode)
        .put("replication_method", replicationMethod)
        .build());
  }

  public abstract ImmutableMap getSslConfig();

  private void addTestData(final MySQLContainer container) throws Exception {
    final var outerContainerAddress = SshHelpers.getOuterContainerAddress(container);
    try (final DSLContext dslContext = DSLContextFactory.create(
        container.getUsername(),
        container.getPassword(),
        DatabaseDriver.MYSQL.getDriverClassName(),
        String.format("jdbc:mysql://%s:%s/%s",
            outerContainerAddress.left,
            outerContainerAddress.right,
            container.getDatabaseName()),
        SQLDialect.MYSQL)) {
      final Database database = new Database(dslContext);

      database.query(ctx -> {
        ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");
        ctx.fetch(
            "INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
        ctx.fetch("CREATE TABLE starships(id INTEGER, name VARCHAR(200));");
        ctx.fetch(
            "INSERT INTO starships (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');");
        return null;
      });
    }
  }

}
