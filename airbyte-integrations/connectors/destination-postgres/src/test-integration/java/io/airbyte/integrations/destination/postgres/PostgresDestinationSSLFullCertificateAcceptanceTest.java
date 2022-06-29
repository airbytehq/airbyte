/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.JdbcDestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import org.apache.commons.lang3.tuple.Triple;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.DockerImageName;

import java.io.IOException;
import java.sql.SQLException;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

import static io.airbyte.db.PostgresUtils.getCertificate;

public class PostgresDestinationSSLFullCertificateAcceptanceTest extends JdbcDestinationAcceptanceTest {

  private PostgreSQLContainer<?> db;

  protected static Triple<String, String, String> certs;
  private final ExtendedNameTransformer namingResolver = new ExtendedNameTransformer();

  @Override
  protected String getImageName() {
    return "airbyte/destination-postgres:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", db.getHost())
        .put("username", db.getUsername())
        .put("password", db.getPassword())
        .put("schema", "public")
        .put("port", db.getFirstMappedPort())
        .put("database", db.getDatabaseName())
        .put("ssl", true)
        .put("ssl_mode", ImmutableMap.builder()
             .put("mode", "verify-full")
             .put("ca_certificate", certs.getLeft())
             .put("client_certificate", certs.getMiddle())
             .put("client_key", certs.getRight())
             .put("client_key_password", "Passw0rd")
             .build())
        .build());
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", db.getHost())
        .put("username", db.getUsername())
        .put("password", "wrong password")
        .put("schema", "public")
        .put("port", db.getFirstMappedPort())
        .put("database", db.getDatabaseName())
        .put("ssl", false)
        .build());
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv env,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace)
        .stream()
        .map(r -> r.get(JavaBaseConstants.COLUMN_NAME_DATA))
        .collect(Collectors.toList());
  }

  @Override
  protected boolean supportsNormalization() {
    return true;
  }

  @Override
  protected boolean supportsDBT() {
    return true;
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new PostgresTestDataComparator();
  }

  @Override
  protected boolean supportBasicDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportArrayDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportObjectDataTypeTest() {
    return true;
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv env, final String streamName, final String namespace)
      throws Exception {
    final String tableName = namingResolver.getIdentifier(streamName);
    return retrieveRecordsFromTable(tableName, namespace);
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws SQLException {
    try (final DSLContext dslContext = DSLContextFactory.create(
        db.getUsername(),
        db.getPassword(),
        DatabaseDriver.POSTGRESQL.getDriverClassName(),
        db.getJdbcUrl(),
        SQLDialect.POSTGRES)) {
      return new Database(dslContext)
          .query(ctx -> {
            ctx.execute("set time zone 'UTC';");
            return ctx.fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", schemaName, tableName, JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
                .stream()
                .map(this::getJsonFromRecord)
                .collect(Collectors.toList());
          });
    }
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) throws Exception {
    db = new PostgreSQLContainer<>(DockerImageName.parse("postgres:bullseye")
            .asCompatibleSubstituteFor("postgres"));
    db.start();
    certs = getCertificate(db);
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws Exception {
    db.stop();
    db.close();
    removeAllCertificates();
  }

  void removeAllCertificates() throws Exception {
    final Runtime run = Runtime.getRuntime();
    runProcess("rm ca.crt", run);
    runProcess("rm client.pk8", run);
    runProcess("rm client.crt", run);
    runProcess("rm customkeystore", run);
  }

  private static void runProcess(final String cmd, final Runtime run) throws IOException, InterruptedException {
    final Process pr = run.exec(cmd);
    if (!pr.waitFor(30, TimeUnit.SECONDS)) {
      pr.destroy();
      throw new RuntimeException("Timeout while executing: " + cmd);
    }
  }

}
