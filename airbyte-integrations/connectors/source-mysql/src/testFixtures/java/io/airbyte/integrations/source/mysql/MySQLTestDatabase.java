/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.testutils.TestDatabase;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.jooq.SQLDialect;
import org.testcontainers.containers.MySQLContainer;

public class MySQLTestDatabase extends
    TestDatabase<MySQLContainer<?>, MySQLTestDatabase, MySQLTestDatabase.MySQLConfigBuilder> {

  public static enum BaseImage {

    MYSQL_8("mysql:8.0"),
    ;

    private final String reference;

    private BaseImage(String reference) {
      this.reference = reference;
    }

  }

  public static enum ContainerModifier {

    MOSCOW_TIMEZONE("withMoscowTimezone"),
    INVALID_TIMEZONE_CEST("withInvalidTimezoneCEST"),
    ROOT_AND_SERVER_CERTIFICATES("withRootAndServerCertificates"),
    CLIENT_CERTITICATE("withClientCertificate"),
    NETWORK("withNetwork"),
    ;

    private final String methodName;

    private ContainerModifier(String methodName) {
      this.methodName = methodName;
    }

  }

  static public MySQLTestDatabase in(BaseImage baseImage, ContainerModifier... methods) {
    String[] methodNames = Stream.of(methods).map(im -> im.methodName).toList().toArray(new String[0]);
    final var container = new MySQLContainerFactory().shared(baseImage.reference, methodNames);
    return new MySQLTestDatabase(container).initialized();
  }

  public MySQLTestDatabase(MySQLContainer<?> container) {
    super(container);
  }

  public MySQLTestDatabase withCdcPermissions() {
    return this
        .with("REVOKE ALL PRIVILEGES, GRANT OPTION FROM '%s';", getUserName())
        .with("GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO '%s';", getUserName());
  }

  public MySQLTestDatabase withoutStrictMode() {
    // This disables strict mode in the DB and allows to insert specific values.
    // For example, it's possible to insert date with zero values "2021-00-00"
    return with("SET @@sql_mode=''");
  }

  static private final int MAX_CONNECTIONS = 1000;

  @Override
  protected Stream<Stream<String>> inContainerBootstrapCmd() {
    return Stream.of(mysqlCmd(Stream.of(
        String.format("SET GLOBAL max_connections=%d", MAX_CONNECTIONS),
        String.format("CREATE DATABASE %s", getDatabaseName()),
        String.format("CREATE USER '%s' IDENTIFIED BY '%s'", getUserName(), getPassword()),
        // Grant privileges also to the container's user, which is not root.
        String.format("GRANT ALL PRIVILEGES ON *.* TO '%s', '%s' WITH GRANT OPTION", getUserName(),
            getContainer().getUsername()))));
  }

  @Override
  protected Stream<String> inContainerUndoBootstrapCmd() {
    return mysqlCmd(Stream.of(
        String.format("DROP USER '%s'", getUserName()),
        String.format("DROP DATABASE %s", getDatabaseName())));
  }

  @Override
  public DatabaseDriver getDatabaseDriver() {
    return DatabaseDriver.MYSQL;
  }

  @Override
  public SQLDialect getSqlDialect() {
    return SQLDialect.MYSQL;
  }

  @Override
  public MySQLConfigBuilder configBuilder() {
    return new MySQLConfigBuilder(this);
  }

  public Stream<String> mysqlCmd(Stream<String> sql) {
    return Stream.of("bash", "-c", String.format(
        "set -o errexit -o pipefail; echo \"%s\" | mysql -v -v -v --user=root --password=test",
        sql.collect(Collectors.joining("; "))));
  }

  static public class MySQLConfigBuilder extends ConfigBuilder<MySQLTestDatabase, MySQLConfigBuilder> {

    protected MySQLConfigBuilder(MySQLTestDatabase testDatabase) {
      super(testDatabase);
    }

    public MySQLConfigBuilder withStandardReplication() {
      return with("replication_method", ImmutableMap.builder().put("method", "STANDARD").build());
    }

    public MySQLConfigBuilder withCdcReplication() {
      return this
          .with("is_test", true)
          .with("replication_method", ImmutableMap.builder()
              .put("method", "CDC")
              .put("initial_waiting_seconds", 5)
              .put("server_time_zone", "America/Los_Angeles")
              .build());
    }

  }

  private String cachedCaCertificate;
  private Certificates cachedCertificates;

  public synchronized String getCaCertificate() {
    if (cachedCaCertificate == null) {
      cachedCaCertificate = catFileInContainer("/var/lib/mysql/ca.pem");
    }
    return cachedCaCertificate;
  }

  public synchronized Certificates getCertificates() {
    if (cachedCertificates == null) {
      cachedCertificates = new Certificates(
          catFileInContainer("/var/lib/mysql/ca.pem"),
          catFileInContainer("/var/lib/mysql/client-cert.pem"),
          catFileInContainer("/var/lib/mysql/client-key.pem"));
    }
    return cachedCertificates;
  }

  public record Certificates(String caCertificate, String clientCertificate, String clientKey) {}

  private String catFileInContainer(String filePath) {
    try {
      return getContainer().execInContainer("sh", "-c", "cat " + filePath).getStdout().trim();
    } catch (IOException e) {
      throw new UncheckedIOException(e);
    } catch (InterruptedException e) {
      throw new RuntimeException(e);
    }
  }

}
