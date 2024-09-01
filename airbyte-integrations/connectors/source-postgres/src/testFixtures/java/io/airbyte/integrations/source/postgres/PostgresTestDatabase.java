/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static io.airbyte.integrations.source.postgres.PostgresSpecConstants.INVALID_CDC_CURSOR_POSITION_PROPERTY;
import static io.airbyte.integrations.source.postgres.PostgresSpecConstants.RESYNC_DATA_OPTION;

import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.testutils.TestDatabase;
import io.airbyte.commons.json.Jsons;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.util.List;
import java.util.stream.Stream;
import org.jooq.SQLDialect;
import org.testcontainers.containers.PostgreSQLContainer;

public class PostgresTestDatabase extends
    TestDatabase<PostgreSQLContainer<?>, PostgresTestDatabase, PostgresTestDatabase.PostgresConfigBuilder> {

  public static enum BaseImage {

    POSTGRES_16("postgres:16-bullseye", 16),
    POSTGRES_12("postgres:12-bullseye", 12),
    POSTGRES_9("postgres:9-alpine", 9),
    POSTGRES_SSL_DEV("marcosmarxm/postgres-ssl:dev", 16);

    public final String reference;
    public final int majorVersion;

    private BaseImage(String reference, int majorVersion) {
      this.reference = reference;
      this.majorVersion = majorVersion;
    };

  }

  public static enum ContainerModifier {

    ASCII("withASCII"),
    CONF("withConf"),
    NETWORK("withNetwork"),
    SSL("withSSL"),
    WAL_LEVEL_LOGICAL("withWalLevelLogical"),
    CERT("withCert"),
    ;

    private String methodName;

    private ContainerModifier(String methodName) {
      this.methodName = methodName;
    }

  }

  @SuppressWarnings("deprecation")
  static public PostgresTestDatabase in(BaseImage baseImage, ContainerModifier... modifiers) {
    String[] methodNames = Stream.of(modifiers).map(im -> im.methodName).toList().toArray(new String[0]);
    final var container = new PostgresContainerFactory().shared(baseImage.reference, methodNames);
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
      return withCdcReplication("While reading Data", RESYNC_DATA_OPTION);
    }

    public PostgresConfigBuilder withCdcReplication(String LsnCommitBehaviour, String cdcCursorFailBehaviour) {
      return this
          .with("is_test", true)
          .with("replication_method", Jsons.jsonNode(ImmutableMap.builder()
              .put("method", "CDC")
              .put("replication_slot", getTestDatabase().getReplicationSlotName())
              .put("publication", getTestDatabase().getPublicationName())
              .put("initial_waiting_seconds", DEFAULT_CDC_REPLICATION_INITIAL_WAIT.getSeconds())
              .put("lsn_commit_behaviour", LsnCommitBehaviour)
              .put(INVALID_CDC_CURSOR_POSITION_PROPERTY, cdcCursorFailBehaviour)
              .build()));
    }

    public PostgresConfigBuilder withXminReplication() {
      return this.with("replication_method", Jsons.jsonNode(ImmutableMap.builder().put("method", "Xmin").build()));
    }

  }

}
