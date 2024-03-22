/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.tidb;

import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.testutils.ContainerFactory;
import io.airbyte.cdk.testutils.TestDatabase;
import java.util.stream.Stream;
import org.jooq.SQLDialect;
import org.testcontainers.tidb.TiDBContainer;
import org.testcontainers.utility.DockerImageName;

public class TiDBTestDatabase extends
    TestDatabase<TiDBContainer, TiDBTestDatabase, TiDBTestDatabase.TiDBConfigBuilder> {

  protected TiDBTestDatabase(final TiDBContainer container) {
    super(container);
  }

  @Override
  public String withNamespace(String name) {
    return name;
  }

  @Override
  public String getDatabaseName() {
    return getContainer().getDatabaseName();
  }

  @Override
  public String getUserName() {
    return getContainer().getUsername();
  }

  @Override
  public String getPassword() {
    return getContainer().getPassword();
  }

  @Override
  protected Stream<Stream<String>> inContainerBootstrapCmd() {
    return Stream.empty();
  }

  @Override
  protected Stream<String> inContainerUndoBootstrapCmd() {
    return Stream.empty();
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
  public TiDBConfigBuilder configBuilder() {
    return new TiDBConfigBuilder(this);
  }

  static public class TiDBConfigBuilder extends ConfigBuilder<TiDBTestDatabase, TiDBConfigBuilder> {

    protected TiDBConfigBuilder(final TiDBTestDatabase testdb) {
      super(testdb);
    }

  }

  static public TiDBContainer container() {
    var factory = new ContainerFactory<TiDBContainer>() {

      @Override
      protected TiDBContainer createNewContainer(DockerImageName dockerImageName) {
        return new TiDBContainer(dockerImageName).withExposedPorts(4000);
      }

    };
    return factory.exclusive("pingcap/tidb:nightly");
  }

}
