/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.JdbcConnector;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.CertificateKey;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.Map;
import javax.sql.DataSource;
import org.testcontainers.containers.MSSQLServerContainer;
import org.testcontainers.utility.DockerImageName;

public class CdcMssqlSslSourceTest extends CdcMssqlSourceTest {

  CdcMssqlSslSourceTest() {
    super();
  }

  protected MSSQLServerContainer<?> createContainer() {
    MsSQLContainerFactory containerFactory = new MsSQLContainerFactory();
    MSSQLServerContainer<?> container =
        containerFactory.createNewContainer(DockerImageName.parse("mcr.microsoft.com/mssql/server:2022-latest"));
    containerFactory.withSslCertificates(container);
    return container;
  }

  @Override
  final protected MsSQLTestDatabase createTestDatabase() {
    final var testdb = new MsSQLTestDatabase(privateContainer);
    return testdb
        .withConnectionProperty("encrypt", "true")
        .withConnectionProperty("databaseName", testdb.getDatabaseName())
        .withConnectionProperty("trustServerCertificate", "true")
        .initialized()
        .withSnapshotIsolation()
        .withCdc()
        .withWaitUntilAgentRunning();
  }

  @Override
  protected DataSource createTestDataSource() {
    return DataSourceFactory.create(
        testUserName(),
        testdb.getPassword(),
        testdb.getDatabaseDriver().getDriverClassName(),
        testdb.getJdbcUrl(),
        Map.of("encrypt", "true", "databaseName", testdb.getDatabaseName(), "trustServerCertificate", "true"),
        JdbcConnector.CONNECT_TIMEOUT_DEFAULT);
  }

  @Override
  protected JsonNode config() {
    final String containerIp;
    try {
      containerIp = InetAddress.getByName(testdb.getContainer().getHost())
          .getHostAddress();
    } catch (UnknownHostException e) {
      throw new RuntimeException(e);
    }
    String certificate = testdb.getCertificate(CertificateKey.SERVER);
    return testdb.configBuilder()
        .withEncrytedVerifyServerCertificate(certificate, testdb.getContainer().getHost())
        .with(JdbcUtils.HOST_KEY, containerIp)
        .with(JdbcUtils.PORT_KEY, testdb.getContainer().getFirstMappedPort())
        .withDatabase()
        .with(JdbcUtils.USERNAME_KEY, testUserName())
        .with(JdbcUtils.PASSWORD_KEY, testdb.getPassword())
        .withSchemas(modelsSchema(), randomSchema())
        .withCdcReplication()
        .build();
  }

}
