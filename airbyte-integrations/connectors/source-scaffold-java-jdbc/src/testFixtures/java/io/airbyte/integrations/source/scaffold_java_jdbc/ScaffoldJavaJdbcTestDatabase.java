/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.scaffold_java_jdbc;

import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.testutils.TestDatabase;
import java.util.stream.Stream;
import org.jooq.SQLDialect;
import org.testcontainers.containers.JdbcDatabaseContainer;

public class ScaffoldJavaJdbcTestDatabase
    extends TestDatabase<JdbcDatabaseContainer<?>, ScaffoldJavaJdbcTestDatabase, ScaffoldJavaJdbcTestDatabase.ScaffoldJavaJdbcConfigBuilder> {

  public ScaffoldJavaJdbcTestDatabase(JdbcDatabaseContainer<?> container) {
    // TODO: (optional) consider also implementing a ContainerFactory to share testcontainer instances.
    // Effective use requires parallelizing the tests using JUnit instead of gradle.
    // This is best achieved by adding a `gradle.properties` file containing
    // `testExecutionConcurrency=-1`.
    super(container);
  }

  @Override
  protected Stream<Stream<String>> inContainerBootstrapCmd() {
    // TODO: return a stream of streams of command args to be passed to `execInContainer` calls to set
    // up the test state.
    // This usually involves the execution of CREATE DATABASE and CREATE USER statements as root.
    return Stream.empty();
  }

  @Override
  protected Stream<String> inContainerUndoBootstrapCmd() {
    // TODO: (optional) return a stream of command args to be passed to a `execInContainer` call to
    // clean up the test state.
    return Stream.empty();
  }

  @Override
  public DatabaseDriver getDatabaseDriver() {
    // TODO: return a suitable value.
    return DatabaseDriver.POSTGRESQL;
  }

  @Override
  public SQLDialect getSqlDialect() {
    // TODO: return a suitable value.
    return SQLDialect.DEFAULT;
  }

  @Override
  public ScaffoldJavaJdbcConfigBuilder configBuilder() {
    // TODO: flesh out the ConfigBuilder subclass and return a new instance of it here.
    return new ScaffoldJavaJdbcConfigBuilder(this);
  }

  public static class ScaffoldJavaJdbcConfigBuilder extends TestDatabase.ConfigBuilder<ScaffoldJavaJdbcTestDatabase, ScaffoldJavaJdbcConfigBuilder> {

    public ScaffoldJavaJdbcConfigBuilder(ScaffoldJavaJdbcTestDatabase testDatabase) {
      super(testDatabase);
    }

  }

}
