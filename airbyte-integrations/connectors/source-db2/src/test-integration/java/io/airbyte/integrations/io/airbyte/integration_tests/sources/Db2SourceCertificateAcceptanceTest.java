/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.source.db2.Db2Source;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.concurrent.TimeUnit;
import javax.sql.DataSource;
import org.testcontainers.containers.Db2Container;

public class Db2SourceCertificateAcceptanceTest extends SourceAcceptanceTest {

  private static final String SCHEMA_NAME = "SOURCE_INTEGRATION_TEST";
  private static final String STREAM_NAME1 = "ID_AND_NAME1";
  private static final String STREAM_NAME2 = "ID_AND_NAME2";

  private static final String TEST_KEY_STORE_PASS = "Passw0rd";
  private static final String KEY_STORE_FILE_PATH = "clientkeystore.jks";

  private Db2Container db;
  private JsonNode config;
  private DataSource dataSource;

  @Override
  protected String getImageName() {
    return "airbyte/source-db2:dev";
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("ID"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                String.format("%s.%s", SCHEMA_NAME, STREAM_NAME1),
                Field.of("ID", JsonSchemaType.NUMBER),
                Field.of("NAME", JsonSchemaType.STRING))
                .withSupportedSyncModes(
                    Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
            .withStream(CatalogHelpers.createAirbyteStream(
                String.format("%s.%s", SCHEMA_NAME, STREAM_NAME2),
                Field.of("ID", JsonSchemaType.NUMBER),
                Field.of("NAME", JsonSchemaType.STRING))
                .withSupportedSyncModes(
                    Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))));
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    db = new Db2Container("ibmcom/db2:11.5.5.0").withCommand().acceptLicense()
        .withExposedPorts(50000);
    db.start();

    final var certificate = getCertificate();
    try {
      convertAndImportCertificate(certificate);
    } catch (final IOException | InterruptedException e) {
      throw new RuntimeException("Failed to import certificate into Java Keystore");
    }

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, db.getHost())
        .put(JdbcUtils.PORT_KEY, db.getFirstMappedPort())
        .put("db", db.getDatabaseName())
        .put(JdbcUtils.USERNAME_KEY, db.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, db.getPassword())
        .put(JdbcUtils.ENCRYPTION_KEY, Jsons.jsonNode(ImmutableMap.builder()
            .put("encryption_method", "encrypted_verify_certificate")
            .put("ssl_certificate", certificate)
            .put("key_store_password", TEST_KEY_STORE_PASS)
            .build()))
        .build());

    final String jdbcUrl = String.format("jdbc:db2://%s:%s/%s",
        config.get(JdbcUtils.HOST_KEY).asText(),
        db.getMappedPort(50000),
        config.get("db").asText()) + ":sslConnection=true;sslTrustStoreLocation=" + KEY_STORE_FILE_PATH +
        ";sslTrustStorePassword=" + TEST_KEY_STORE_PASS + ";";

    dataSource = DataSourceFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        Db2Source.DRIVER_CLASS,
        jdbcUrl);

    try {
      final JdbcDatabase database = new DefaultJdbcDatabase(dataSource);

      final String createSchemaQuery = String.format("CREATE SCHEMA %s", SCHEMA_NAME);
      final String createTableQuery1 = String
          .format("CREATE TABLE %s.%s (ID INTEGER, NAME VARCHAR(200))", SCHEMA_NAME, STREAM_NAME1);
      final String createTableQuery2 = String
          .format("CREATE TABLE %s.%s (ID INTEGER, NAME VARCHAR(200))", SCHEMA_NAME, STREAM_NAME2);
      final String insertIntoTableQuery1 = String
          .format("INSERT INTO %s.%s (ID, NAME) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash')",
              SCHEMA_NAME, STREAM_NAME1);
      final String insertIntoTableQuery2 = String
          .format("INSERT INTO %s.%s (ID, NAME) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash')",
              SCHEMA_NAME, STREAM_NAME2);

      database.execute(createSchemaQuery);
      database.execute(createTableQuery1);
      database.execute(createTableQuery2);
      database.execute(insertIntoTableQuery1);
      database.execute(insertIntoTableQuery2);
    } finally {
      DataSourceFactory.close(dataSource);
    }
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    new File("certificate.pem").delete();
    new File("certificate.der").delete();
    new File(KEY_STORE_FILE_PATH).delete();
    db.close();
  }

  /* Helpers */

  private String getCertificate() throws IOException, InterruptedException {
    db.execInContainer("su", "-", "db2inst1", "-c", "gsk8capicmd_64 -keydb -create -db \"server.kdb\" -pw \"" + TEST_KEY_STORE_PASS + "\" -stash");
    db.execInContainer("su", "-", "db2inst1", "-c", "gsk8capicmd_64 -cert -create -db \"server.kdb\" -pw \"" + TEST_KEY_STORE_PASS
        + "\" -label \"mylabel\" -dn \"CN=testcompany\" -size 2048 -sigalg SHA256_WITH_RSA");
    db.execInContainer("su", "-", "db2inst1", "-c", "gsk8capicmd_64 -cert -extract -db \"server.kdb\" -pw \"" + TEST_KEY_STORE_PASS
        + "\" -label \"mylabel\" -target \"server.arm\" -format ascii -fips");

    db.execInContainer("su", "-", "db2inst1", "-c", "db2 update dbm cfg using SSL_SVR_KEYDB /database/config/db2inst1/server.kdb");
    db.execInContainer("su", "-", "db2inst1", "-c", "db2 update dbm cfg using SSL_SVR_STASH /database/config/db2inst1/server.sth");
    db.execInContainer("su", "-", "db2inst1", "-c", "db2 update dbm cfg using SSL_SVR_LABEL mylabel");
    db.execInContainer("su", "-", "db2inst1", "-c", "db2 update dbm cfg using SSL_VERSIONS TLSV12");
    db.execInContainer("su", "-", "db2inst1", "-c", "db2 update dbm cfg using SSL_SVCENAME 50000");
    db.execInContainer("su", "-", "db2inst1", "-c", "db2set -i db2inst1 DB2COMM=SSL");
    db.execInContainer("su", "-", "db2inst1", "-c", "db2stop force");
    db.execInContainer("su", "-", "db2inst1", "-c", "db2start");
    return db.execInContainer("su", "-", "db2inst1", "-c", "cat server.arm").getStdout();
  }

  private static void convertAndImportCertificate(final String certificate) throws IOException, InterruptedException {
    final Runtime run = Runtime.getRuntime();
    try (final PrintWriter out = new PrintWriter("certificate.pem", StandardCharsets.UTF_8)) {
      out.print(certificate);
    }
    runProcess("openssl x509 -outform der -in certificate.pem -out certificate.der", run);
    runProcess(
        "keytool -import -alias rds-root -keystore " + KEY_STORE_FILE_PATH + " -file certificate.der -storepass " + TEST_KEY_STORE_PASS
            + " -noprompt",
        run);
  }

  private static void runProcess(final String cmd, final Runtime run) throws IOException, InterruptedException {
    final Process pr = run.exec(cmd);
    if (!pr.waitFor(30, TimeUnit.SECONDS)) {
      pr.destroy();
      throw new RuntimeException("Timeout while executing: " + cmd);
    }
  }

}
