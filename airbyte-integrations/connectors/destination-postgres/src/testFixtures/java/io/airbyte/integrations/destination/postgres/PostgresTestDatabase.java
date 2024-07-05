/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.testutils.ContainerFactory.NamedContainerModifier;
import io.airbyte.cdk.testutils.TestDatabase;
import io.airbyte.commons.json.Jsons;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.util.List;
import java.util.function.Consumer;
import java.util.stream.Stream;
import org.jooq.SQLDialect;
import org.testcontainers.containers.PostgreSQLContainer;

/**
 * TODO: This class is a copy from source-postgres:testFixtures. Eventually merge into a common
 * fixtures module.
 */
public class PostgresTestDatabase extends
    TestDatabase<PostgreSQLContainer<?>, PostgresTestDatabase, PostgresTestDatabase.PostgresConfigBuilder> {

  public enum BaseImage {

    POSTGRES_16("postgres:16-bullseye"),
    POSTGRES_12("postgres:12-bullseye"),
    POSTGRES_13("postgres:13-alpine"),
    POSTGRES_9("postgres:9-alpine"),
    POSTGRES_SSL_DEV("marcosmarxm/postgres-ssl:dev");

    private final String reference;

    private BaseImage(String reference) {
      this.reference = reference;
    };

  }

  public enum ContainerModifier implements NamedContainerModifier<PostgreSQLContainer<?>> {

    ASCII(PostgresContainerFactory::withASCII),
    CONF(PostgresContainerFactory::withConf),
    NETWORK(PostgresContainerFactory::withNetwork),
    SSL(PostgresContainerFactory::withSSL),
    CERT(PostgresContainerFactory::withCert),
    ;

    private Consumer<PostgreSQLContainer<?>> modifer;

    private ContainerModifier(final Consumer<PostgreSQLContainer<?>> modifer) {
      this.modifer = modifer;
    }

    @Override
    public Consumer<PostgreSQLContainer<?>> modifier() {
      return modifer;
    }

  }

  static public PostgresTestDatabase in(BaseImage baseImage, ContainerModifier... modifiers) {
    final var container = new PostgresContainerFactory().shared(baseImage.reference, modifiers);
    return new PostgresTestDatabase(container).initialized();
  }

  public PostgresTestDatabase(PostgreSQLContainer<?> container) {
    super(container);
  }

  @Override
  protected Stream<Stream<String>> inContainerBootstrapCmd() {
    return Stream.of(psqlCmd(Stream.of(
        String.format("CREATE DATABASE %s", getDatabaseName()),
        String.format("CREATE USER %s PASSWORD '%s'", getUserName(), getPassword()),
        String.format("GRANT ALL PRIVILEGES ON DATABASE %s TO %s", getDatabaseName(), getUserName()),
        String.format("ALTER USER %s WITH SUPERUSER", getUserName()))));
  }

  /**
   * Close resources held by this instance. This deliberately avoids dropping the database, which is
   * really expensive in Postgres. This is because a DROP DATABASE in Postgres triggers a CHECKPOINT.
   * Call {@link #dropDatabaseAndUser} to explicitly drop the database and the user.
   */
  @Override
  protected Stream<String> inContainerUndoBootstrapCmd() {
    return Stream.empty();
  }

  /**
   * Drop the database owned by this instance.
   */
  public void dropDatabaseAndUser() {
    execInContainer(psqlCmd(Stream.of(
        String.format("DROP DATABASE %s", getDatabaseName()),
        String.format("DROP OWNED BY %s", getUserName()),
        String.format("DROP USER %s", getUserName()))));
  }

  public Stream<String> psqlCmd(Stream<String> sql) {
    return Stream.concat(
        Stream.of("psql",
            "-d", getContainer().getDatabaseName(),
            "-U", getContainer().getUsername(),
            "-v", "ON_ERROR_STOP=1",
            "-a"),
        sql.flatMap(stmt -> Stream.of("-c", stmt)));
  }

  @Override
  public DatabaseDriver getDatabaseDriver() {
    return DatabaseDriver.POSTGRESQL;
  }

  @Override
  public SQLDialect getSqlDialect() {
    return SQLDialect.POSTGRES;
  }

  private Certificates cachedCerts;

  public synchronized Certificates getCertificates() {
    if (cachedCerts == null) {
      final String caCert, clientKey, clientCert;
      try {
        caCert = getContainer().execInContainer("su", "-c", "cat ca.crt").getStdout().trim();
        clientKey = getContainer().execInContainer("su", "-c", "cat client.key").getStdout().trim();
        clientCert = getContainer().execInContainer("su", "-c", "cat client.crt").getStdout().trim();
      } catch (IOException e) {
        throw new UncheckedIOException(e);
      } catch (InterruptedException e) {
        throw new RuntimeException(e);
      }
      cachedCerts = new Certificates(caCert, clientCert, clientKey);
    }
    return cachedCerts;
  }

  public record Certificates(String caCertificate, String clientCertificate, String clientKey) {}

  @Override
  public PostgresConfigBuilder configBuilder() {
    return new PostgresConfigBuilder(this);
  }

  public String getReplicationSlotName() {
    return withNamespace("debezium_slot");
  }

  public String getPublicationName() {
    return withNamespace("publication");
  }

  public PostgresTestDatabase withReplicationSlot() {
    return this
        .with("SELECT pg_create_logical_replication_slot('%s', 'pgoutput');", getReplicationSlotName())
        .onClose("SELECT pg_drop_replication_slot('%s');", getReplicationSlotName());
  }

  public PostgresTestDatabase withPublicationForAllTables() {
    return this
        .with("CREATE PUBLICATION %s FOR ALL TABLES;", getPublicationName())
        .onClose("DROP PUBLICATION %s CASCADE;", getPublicationName());
  }

  static public class PostgresConfigBuilder extends ConfigBuilder<PostgresTestDatabase, PostgresConfigBuilder> {

    protected PostgresConfigBuilder(PostgresTestDatabase testdb) {
      super(testdb);
    }

    public PostgresConfigBuilder withSchemas(String... schemas) {
      return with(JdbcUtils.SCHEMAS_KEY, List.of(schemas));
    }

    public PostgresConfigBuilder withStandardReplication() {
      return with("replication_method", ImmutableMap.builder().put("method", "Standard").build());
    }

    public PostgresConfigBuilder withCdcReplication() {
      return withCdcReplication("While reading Data");
    }

    public PostgresConfigBuilder withCdcReplication(String LsnCommitBehaviour) {
      return this
          .with("is_test", true)
          .with("replication_method", Jsons.jsonNode(ImmutableMap.builder()
              .put("method", "CDC")
              .put("replication_slot", getTestDatabase().getReplicationSlotName())
              .put("publication", getTestDatabase().getPublicationName())
              .put("initial_waiting_seconds", ConfigBuilder.DEFAULT_CDC_REPLICATION_INITIAL_WAIT.getSeconds())
              .put("lsn_commit_behaviour", LsnCommitBehaviour)
              .build()));
    }

    public PostgresConfigBuilder withXminReplication() {
      return this.with("replication_method", Jsons.jsonNode(ImmutableMap.builder().put("method", "Xmin").build()));
    }

  }

}
