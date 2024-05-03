/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.singlestore;

import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.testutils.ContainerFactory;
import io.airbyte.cdk.testutils.TestDatabase;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.jooq.SQLDialect;

public class SingleStoreTestDatabase
    extends TestDatabase<AirbyteSingleStoreTestContainer, SingleStoreTestDatabase, SingleStoreTestDatabase.SingleStoreConfigBuilder> {

  public enum BaseImage {

    SINGLESTORE_DEV("ghcr.io/singlestore-labs/singlestoredb-dev:latest");

    public final String reference;

    BaseImage(String reference) {
      this.reference = reference;
    }

  }

  public enum ContainerModifier implements ContainerFactory.NamedContainerModifier<AirbyteSingleStoreTestContainer> {

    CERT(SingleStoreContainerFactory::withCert);

    private Consumer<AirbyteSingleStoreTestContainer> modifer;

    ContainerModifier(final Consumer<AirbyteSingleStoreTestContainer> modifer) {
      this.modifer = modifer;
    }

    @Override
    public Consumer<AirbyteSingleStoreTestContainer> modifier() {
      return modifer;
    }

  }

  static public SingleStoreTestDatabase in(BaseImage baseImage, ContainerModifier... modifiers) {
    final var container = new SingleStoreContainerFactory().shared(baseImage.reference, modifiers);
    return new SingleStoreTestDatabase(container).initialized();
  }

  public SingleStoreTestDatabase(AirbyteSingleStoreTestContainer container) {
    super(container);
  }

  @Override
  protected Stream<Stream<String>> inContainerBootstrapCmd() {
    final var sql = Stream.of(String.format("CREATE DATABASE %s", getDatabaseName()),
        String.format("CREATE USER %s IDENTIFIED BY '%s'", getUserName(), getPassword()),
        String.format("GRANT ALL ON *.* TO %s", getUserName()));
    getContainer().withUsername(getUserName()).withPassword(getPassword()).withDatabaseName(getDatabaseName());
    return Stream.of(singlestoreCmd(sql));
  }

  @Override
  protected Stream<String> inContainerUndoBootstrapCmd() {
    return singlestoreCmd(Stream.of(String.format("DROP USER %s", getUserName()), String.format("DROP DATABASE \\`%s\\`", getDatabaseName())));
  }

  @Override
  public DatabaseDriver getDatabaseDriver() {
    return DatabaseDriver.SINGLESTORE;
  }

  @Override
  public SQLDialect getSqlDialect() {
    return SQLDialect.DEFAULT;
  }

  @Override
  public SingleStoreConfigBuilder configBuilder() {
    return new SingleStoreConfigBuilder(this);
  }

  public Stream<String> singlestoreCmd(Stream<String> sql) {
    return Stream.of("/bin/bash", "-c", String.format("set -o errexit -o pipefail; echo \"%s\" | singlestore -v -v -v --user=root --password=root",
        sql.collect(Collectors.joining("; "))));
  }

  private Certificates cachedCerts;

  public synchronized Certificates getCertificates() {
    if (cachedCerts == null) {
      final String caCert, serverKey, serverCert;
      try {
        caCert = getContainer().execInContainer("/bin/bash", "-c", "cat /certs/ca-cert.pem").getStdout().trim();
        serverKey = getContainer().execInContainer("/bin/bash", "-c", "cat /certs/server-key.pem").getStdout().trim();
        serverCert = getContainer().execInContainer("/bin/bash", "-c", "cat /certs/server-cert.pem").getStdout().trim();
      } catch (IOException e) {
        throw new UncheckedIOException(e);
      } catch (InterruptedException e) {
        throw new RuntimeException(e);
      }
      cachedCerts = new Certificates(caCert, serverKey, serverCert);
    }
    return cachedCerts;
  }

  public record Certificates(String caCertificate,
                             String serverKey,
                             String serverCert) {

  }

  static public class SingleStoreConfigBuilder extends TestDatabase.ConfigBuilder<SingleStoreTestDatabase, SingleStoreConfigBuilder> {

    protected SingleStoreConfigBuilder(SingleStoreTestDatabase testDatabase) {
      super(testDatabase);
    }

  }

}
