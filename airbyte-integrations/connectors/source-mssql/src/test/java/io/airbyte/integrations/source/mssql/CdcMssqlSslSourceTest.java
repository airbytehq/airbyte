/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import static io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants.SYNC_CHECKPOINT_RECORDS_PROPERTY;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.JdbcConnector;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.BaseImage;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.CertificateKey;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.ContainerModifier;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.Map;
import javax.sql.DataSource;
import org.junit.jupiter.api.TestInstance;
import org.junit.jupiter.api.TestInstance.Lifecycle;
import org.junit.jupiter.api.parallel.Execution;
import org.junit.jupiter.api.parallel.ExecutionMode;

@TestInstance(Lifecycle.PER_METHOD)
@Execution(ExecutionMode.CONCURRENT)
@edu.umd.cs.findbugs.annotations.SuppressWarnings(value = "NP_NULL_ON_SOME_PATH")
public class CdcMssqlSslSourceTest extends CdcMssqlSourceTest {

  @Override
  final protected MsSQLTestDatabase createTestDatabase() {
    final var testdb = MsSQLTestDatabase.in(BaseImage.MSSQL_2022, ContainerModifier.AGENT, ContainerModifier.WITH_SSL_CERTIFICATES);
    return testdb.withWaitUntilAgentRunning()
        .withCdc();
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
    } catch (final UnknownHostException e) {
      throw new RuntimeException(e);
    }
    final String certificate = testdb.getCertificate(CertificateKey.SERVER);
    return testdb.configBuilder()
        .withEncrytedVerifyServerCertificate(certificate, testdb.getContainer().getHost())
        .with(JdbcUtils.HOST_KEY, containerIp)
        .with(JdbcUtils.PORT_KEY, testdb.getContainer().getFirstMappedPort())
        .withDatabase()
        .with(JdbcUtils.USERNAME_KEY, testUserName())
        .with(JdbcUtils.PASSWORD_KEY, testdb.getPassword())
        .withSchemas(modelsSchema(), randomSchema())
        .withCdcReplication()
        .with(SYNC_CHECKPOINT_RECORDS_PROPERTY, 1)
        .build();
  }

}
