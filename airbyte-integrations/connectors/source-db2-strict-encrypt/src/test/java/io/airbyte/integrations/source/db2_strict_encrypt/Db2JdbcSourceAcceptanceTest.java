/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.db2_strict_encrypt;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableSet;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.db2.Db2Source;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.sql.JDBCType;
import java.util.Collections;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.Db2Container;

class Db2JdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest {

  private static final String TEST_KEY_STORE_PASS = "Passw0rd";
  private static final String KEY_STORE_FILE_PATH = "clientkeystore.jks";

  private static Set<String> TEST_TABLES = Collections.emptySet();
  private static String certificate;
  private static Db2Container db;
  private JsonNode config;

  @BeforeAll
  static void init() throws IOException, InterruptedException {
    db = new Db2Container("ibmcom/db2:11.5.5.0").acceptLicense();
    db.start();

    certificate = getCertificate();
    try {
      convertAndImportCertificate(certificate);
    } catch (final IOException | InterruptedException e) {
      throw new RuntimeException("Failed to import certificate into Java Keystore");
    }

    // Db2 transforms names to upper case, so we need to use upper case name to retrieve data later.
    SCHEMA_NAME = "JDBC_INTEGRATION_TEST1";
    SCHEMA_NAME2 = "JDBC_INTEGRATION_TEST2";
    TEST_SCHEMAS = ImmutableSet.of(SCHEMA_NAME, SCHEMA_NAME2);
    TABLE_NAME = "ID_AND_NAME";
    TABLE_NAME_WITH_SPACES = "ID AND NAME";
    TABLE_NAME_WITHOUT_PK = "ID_AND_NAME_WITHOUT_PK";
    TABLE_NAME_COMPOSITE_PK = "FULL_NAME_COMPOSITE_PK";
    TABLE_NAME_WITHOUT_CURSOR_TYPE = "TABLE_NAME_WITHOUT_CURSOR_TYPE";
    TABLE_NAME_WITH_NULLABLE_CURSOR_TYPE = "TABLE_NAME_WITH_NULLABLE_CURSOR_TYPE";
    TEST_TABLES = ImmutableSet
        .of(TABLE_NAME, TABLE_NAME_WITHOUT_PK, TABLE_NAME_COMPOSITE_PK);
    COL_ID = "ID";
    COL_NAME = "NAME";
    COL_UPDATED_AT = "UPDATED_AT";
    COL_FIRST_NAME = "FIRST_NAME";
    COL_LAST_NAME = "LAST_NAME";
    COL_LAST_NAME_WITH_SPACE = "LAST NAME";
    // In Db2 PK columns must be declared with NOT NULL statement.
    COLUMN_CLAUSE_WITH_PK = "id INTEGER NOT NULL, name VARCHAR(200), updated_at DATE";
    COLUMN_CLAUSE_WITH_COMPOSITE_PK = "first_name VARCHAR(200) NOT NULL, last_name VARCHAR(200) NOT NULL, updated_at DATE";
    // There is no IF EXISTS statement for a schema in Db2.
    // The schema name must be in the catalog when attempting the DROP statement; otherwise an error is
    // returned.
    DROP_SCHEMA_QUERY = "DROP SCHEMA %s RESTRICT";
    CREATE_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "CREATE TABLE %s (%s boolean)";
    INSERT_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "INSERT INTO %s VALUES(true)";
  }

  @BeforeEach
  public void setup() throws Exception {
    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", db.getHost())
        .put("port", db.getFirstMappedPort())
        .put("db", db.getDatabaseName())
        .put("username", db.getUsername())
        .put("password", db.getPassword())
        .put("encryption", Jsons.jsonNode(ImmutableMap.builder()
            .put("encryption_method", "encrypted_verify_certificate")
            .put("ssl_certificate", certificate)
            .put("key_store_password", TEST_KEY_STORE_PASS)
            .build()))
        .build());

    super.setup();
  }

  @AfterEach
  public void clean() throws Exception {
    // In Db2 before dropping a schema, all objects that were in that schema must be dropped or moved to
    // another schema.
    for (final String tableName : TEST_TABLES) {
      final String dropTableQuery = String
          .format("DROP TABLE IF EXISTS %s.%s", SCHEMA_NAME, tableName);
      super.database.execute(connection -> connection.createStatement().execute(dropTableQuery));
    }
    for (int i = 2; i < 10; i++) {
      final String dropTableQuery = String
          .format("DROP TABLE IF EXISTS %s.%s%s", SCHEMA_NAME, TABLE_NAME, i);
      super.database.execute(connection -> connection.createStatement().execute(dropTableQuery));
    }
    super.database.execute(connection -> connection.createStatement().execute(String
        .format("DROP TABLE IF EXISTS %s.%s", SCHEMA_NAME,
            sourceOperations.enquoteIdentifier(connection, TABLE_NAME_WITH_SPACES))));
    super.database.execute(connection -> connection.createStatement().execute(String
        .format("DROP TABLE IF EXISTS %s.%s", SCHEMA_NAME,
            sourceOperations.enquoteIdentifier(connection, TABLE_NAME_WITH_SPACES + 2))));
    super.database.execute(connection -> connection.createStatement().execute(String
        .format("DROP TABLE IF EXISTS %s.%s", SCHEMA_NAME2,
            sourceOperations.enquoteIdentifier(connection, TABLE_NAME))));
    super.database.execute(connection -> connection.createStatement().execute(String
        .format("DROP TABLE IF EXISTS %s.%s", SCHEMA_NAME,
            sourceOperations.enquoteIdentifier(connection, TABLE_NAME_WITHOUT_CURSOR_TYPE))));
    super.database.execute(connection -> connection.createStatement().execute(String
        .format("DROP TABLE IF EXISTS %s.%s", SCHEMA_NAME,
            sourceOperations.enquoteIdentifier(connection, TABLE_NAME_WITH_NULLABLE_CURSOR_TYPE))));
    super.tearDown();
  }

  @AfterAll
  static void cleanUp() {
    new File("certificate.pem").delete();
    new File("certificate.der").delete();
    new File(KEY_STORE_FILE_PATH).delete();
    db.close();
  }

  @Override
  public boolean supportsSchemas() {
    return true;
  }

  @Override
  public JsonNode getConfig() {
    return Jsons.clone(config);
  }

  @Override
  public String getDriverClass() {
    return Db2StrictEncryptSource.DRIVER_CLASS;
  }

  @Override
  public AbstractJdbcSource<JDBCType> getJdbcSource() {
    return new Db2Source();
  }

  @Override
  public Source getSource() {
    return new Db2StrictEncryptSource();
  }

  @Test
  void testSpec() throws Exception {
    final ConnectorSpecification actual = source.spec();
    final ConnectorSpecification expected =
        Jsons.deserialize(MoreResources.readResource("expected_spec.json"), ConnectorSpecification.class);

    assertEquals(expected, actual);
  }

  /* Helpers */

  private static String getCertificate() throws IOException, InterruptedException {
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
