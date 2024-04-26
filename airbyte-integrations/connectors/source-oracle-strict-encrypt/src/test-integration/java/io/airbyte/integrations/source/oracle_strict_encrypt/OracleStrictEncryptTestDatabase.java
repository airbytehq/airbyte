/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle_strict_encrypt;

import static io.airbyte.integrations.source.oracle_strict_encrypt.OracleStrictEncryptJdbcSourceAcceptanceTest.cleanUpTablesAndWait;

import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.testutils.TestDatabase;
import io.airbyte.commons.json.Jsons;
import java.util.List;
import java.util.stream.Stream;
import org.jooq.SQLDialect;

public class OracleStrictEncryptTestDatabase extends
    TestDatabase<AirbyteOracleTestContainer, OracleStrictEncryptTestDatabase, OracleStrictEncryptTestDatabase.OracleStrictEncryptDbConfigBuilder> {

  private final AirbyteOracleTestContainer container;
  private final List<String> schemaNames;

  protected OracleStrictEncryptTestDatabase(final AirbyteOracleTestContainer container, final List<String> schemaNames) {
    super(container);
    this.container = container;
    this.schemaNames = schemaNames;
  }

  @Override
  public String getJdbcUrl() {
    return container.getJdbcUrl();
  }

  @Override
  public String getUserName() {
    return container.getUsername();
  }

  @Override
  public String getPassword() {
    return container.getPassword();
  }

  @Override
  public String getDatabaseName() {
    return container.getDatabaseName();
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
    return DatabaseDriver.ORACLE;
  }

  @Override
  public SQLDialect getSqlDialect() {
    return SQLDialect.DEFAULT;
  }

  @Override
  public OracleStrictEncryptDbConfigBuilder configBuilder() {
    return new OracleStrictEncryptDbConfigBuilder(this)
        .with(JdbcUtils.HOST_KEY, container.getHost())
        .with(JdbcUtils.PORT_KEY, container.getFirstMappedPort())
        .with("sid", container.getSid())
        .with(JdbcUtils.USERNAME_KEY, container.getUsername())
        .with(JdbcUtils.PASSWORD_KEY, container.getPassword())
        .with(JdbcUtils.SCHEMAS_KEY, schemaNames)
        .with(JdbcUtils.ENCRYPTION_KEY, Jsons.jsonNode(ImmutableMap.builder()
            .put("encryption_method", "client_nne")
            .put("encryption_algorithm", "3DES168")
            .build()));
  }

  @Override
  public void close() {
    cleanUpTablesAndWait();
  }

  static public class OracleStrictEncryptDbConfigBuilder extends ConfigBuilder<OracleStrictEncryptTestDatabase, OracleStrictEncryptDbConfigBuilder> {

    protected OracleStrictEncryptDbConfigBuilder(final OracleStrictEncryptTestDatabase testdb) {
      super(testdb);
    }

  }

}
