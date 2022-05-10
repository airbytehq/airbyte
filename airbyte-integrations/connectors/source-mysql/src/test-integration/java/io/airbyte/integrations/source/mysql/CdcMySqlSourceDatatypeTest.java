/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.integrations.standardtest.source.AbstractSourceDatabaseTypeTest;
import io.airbyte.integrations.standardtest.source.TestDataHolder;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.JsonSchemaType;
import java.io.File;
import java.io.IOException;
import org.apache.commons.codec.binary.Base64;
import org.apache.commons.io.FileUtils;
import org.apache.commons.lang3.StringUtils;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.MySQLContainer;

public class CdcMySqlSourceDatatypeTest extends AbstractSourceDatabaseTypeTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(CdcMySqlSourceDatatypeTest.class);

  private MySQLContainer<?> container;
  private JsonNode config;

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    container.close();
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-mysql:dev";
  }

  @Override
  protected Database setupDatabase() throws Exception {
    container = new MySQLContainer<>("mysql:8.0");
    container.start();

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", container.getHost())
        .put("port", container.getFirstMappedPort())
        .put("database", container.getDatabaseName())
        .put("username", container.getUsername())
        .put("password", container.getPassword())
        .put("replication_method", MySqlSource.ReplicationMethod.CDC)
        .build());

    final DSLContext dslContext = DSLContextFactory.create(
        config.get("username").asText(),
        config.get("password").asText(),
        DatabaseDriver.MYSQL.getDriverClassName(),
        String.format(DatabaseDriver.MYSQL.getUrlFormatString(),
            config.get("host").asText(),
            config.get("port").asInt(),
            config.get("database").asText()), SQLDialect.MYSQL);
    final Database database = new Database(dslContext);

    // It disable strict mode in the DB and allows to insert specific values.
    // For example, it's possible to insert date with zero values "2021-00-00"
    database.query(ctx -> ctx.fetch("SET @@sql_mode=''"));

    revokeAllPermissions();
    grantCorrectPermissions();

    return database;
  }

  @Override
  protected String getNameSpace() {
    return container.getDatabaseName();
  }

  private void revokeAllPermissions() {
    executeQuery("REVOKE ALL PRIVILEGES, GRANT OPTION FROM " + container.getUsername() + "@'%';");
  }

  private void grantCorrectPermissions() {
    executeQuery(
        "GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO "
            + container.getUsername() + "@'%';");
  }

  private void executeQuery(final String query) {
    try (final DSLContext dslContext = DSLContextFactory.create(
        "root",
        "test",
        DatabaseDriver.MYSQL.getDriverClassName(),
        String.format(DatabaseDriver.MYSQL.getUrlFormatString(),
            container.getHost(),
            container.getFirstMappedPort(),
            container.getDatabaseName()), SQLDialect.MYSQL)) {
      final Database database = new Database(dslContext);
      database.query(
          ctx -> ctx
              .execute(query));
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  protected void initTests() {
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("tinyint")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "-128", "127")
            .addExpectedValues(null, "-128", "127")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("smallint")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "-32768", "32767")
            .addExpectedValues(null, "-32768", "32767")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("smallint")
            .airbyteType(JsonSchemaType.NUMBER)
            .fullSourceDataType("smallint zerofill")
            .addInsertValues("1")
            .addExpectedValues("1")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("mediumint")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "-8388608", "8388607")
            .addExpectedValues(null, "-8388608", "8388607")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("mediumint")
            .airbyteType(JsonSchemaType.NUMBER)
            .fullSourceDataType("mediumint zerofill")
            .addInsertValues("1")
            .addExpectedValues("1")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("int")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "-2147483648", "2147483647")
            .addExpectedValues(null, "-2147483648", "2147483647")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("int")
            .airbyteType(JsonSchemaType.NUMBER)
            .fullSourceDataType("int unsigned")
            .addInsertValues("3428724653")
            .addExpectedValues("3428724653")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("int")
            .airbyteType(JsonSchemaType.NUMBER)
            .fullSourceDataType("int zerofill")
            .addInsertValues("1")
            .addExpectedValues("1")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bigint")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "9223372036854775807")
            .addExpectedValues(null, "9223372036854775807")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("float")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "10.5")
            .addExpectedValues(null, "10.5")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("double")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "power(10, 308)", "1/power(10, 45)", "10.5")
            .addExpectedValues(null, String.valueOf(Math.pow(10, 308)), String.valueOf(1 / Math.pow(10, 45)), "10.5")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("decimal")
            .airbyteType(JsonSchemaType.NUMBER)
            .fullSourceDataType("decimal(10,4)")
            .addInsertValues("0.188", "null")
            .addExpectedValues("0.1880", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("decimal")
            .airbyteType(JsonSchemaType.NUMBER)
            .fullSourceDataType("decimal(19,2)")
            .addInsertValues("1700000.00")
            .addInsertValues("1700000.00")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bit")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "1", "0")
            .addExpectedValues(null, "true", "false")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("date")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'2021-01-01'")
            .addExpectedValues(null, "2021-01-01T00:00:00Z")
            .build());

    // Check Zero-date value for mandatory field
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("date")
            .fullSourceDataType("date not null")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'0000-00-00'")
            .addExpectedValues("1970-01-01T00:00:00Z")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("datetime")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'2005-10-10 23:22:21'")
            .addExpectedValues(null, "2005-10-10T23:22:21.000000Z")
            .build());

    // Check Zero-date value for mandatory field
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("datetime")
            .fullSourceDataType("datetime not null")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'0000-00-00 00:00:00'")
            .addExpectedValues("1970-01-01T00:00:00Z")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("timestamp")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null")
            .addNullExpectedValue()
            .build());

    // Check Zero-date value for mandatory field
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("timestamp")
            .fullSourceDataType("timestamp not null")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'0000-00-00 00:00:00.000000'")
            .addExpectedValues("1970-01-01T00:00:00Z")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("time")
            .airbyteType(JsonSchemaType.STRING)
            // JDBC driver can process only "clock"(00:00:00-23:59:59) values.
            // https://debezium.io/documentation/reference/connectors/mysql.html#mysql-temporal-types
            .addInsertValues("null", "'-23:59:59'", "'00:00:00'")
            .addExpectedValues(null, "1970-01-01T23:59:59Z", "1970-01-01T00:00:00Z")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("varchar")
            .airbyteType(JsonSchemaType.STRING)
            .fullSourceDataType("varchar(256) character set cp1251")
            .addInsertValues("null", "'тест'")
            .addExpectedValues(null, "тест")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("varchar")
            .airbyteType(JsonSchemaType.STRING)
            .fullSourceDataType("varchar(256) character set utf16")
            .addInsertValues("null", "0xfffd")
            .addExpectedValues(null, "�")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("varchar")
            .airbyteType(JsonSchemaType.STRING)
            .fullSourceDataType("varchar(256)")
            .addInsertValues("null", "'!\"#$%&\\'()*+,-./:;<=>?\\@[\\]^_\\`{|}~'")
            .addExpectedValues(null, "!\"#$%&'()*+,-./:;<=>?@[]^_`{|}~")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("varbinary")
            .airbyteType(JsonSchemaType.STRING_BASE_64)
            .fullSourceDataType("varbinary(20000)") //// size should be enough to save test.png
            .addInsertValues("null", "'test'", "'тест'", String.format("FROM_BASE64('%s')", getFileDataInBase64()))
            .addExpectedValues(null, "dGVzdA==", "0YLQtdGB0YI=", getFileDataInBase64())
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("blob")
            .airbyteType(JsonSchemaType.STRING_BASE_64)
            .addInsertValues("null", "'test'", "'тест'", String.format("FROM_BASE64('%s')", getFileDataInBase64()))
            .addExpectedValues(null, "dGVzdA==", "0YLQtdGB0YI=", getFileDataInBase64())
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("mediumtext")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues(getLogString(1048000), "'test'", "'тест'")
            .addExpectedValues(StringUtils.leftPad("0", 1048000, "0"), "test", "тест")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("tinytext")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'test'", "'тест'")
            .addExpectedValues(null, "test", "тест")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("longtext")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'test'", "'тест'")
            .addExpectedValues(null, "test", "тест")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("text")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'test'", "'тест'")
            .addExpectedValues(null, "test", "тест")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("json")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'{\"a\": 10, \"b\": 15}'")
            .addExpectedValues(null, "{\"a\": 10, \"b\": 15}")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("point")
            .airbyteType(JsonSchemaType.OBJECT)
            .addInsertValues("null", "(ST_GeomFromText('POINT(1 1)'))")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bool")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "1", "0")
            .addExpectedValues(null, "true", "false")
            .build());

  }

  private String getLogString(final int length) {
    final int maxLpadLength = 262144;
    final StringBuilder stringBuilder = new StringBuilder("concat(");
    final int fullChunks = length / maxLpadLength;
    for (int i = 1; i <= fullChunks; i++) {
      stringBuilder.append("lpad('0', 262144, '0'),");
    }
    stringBuilder.append("lpad('0', ").append(length % maxLpadLength).append(", '0'))");
    return stringBuilder.toString();
  }

  private String getFileDataInBase64() {
    final File file = new File(getClass().getClassLoader().getResource("test.png").getFile());
    try {
      return Base64.encodeBase64String(FileUtils.readFileToByteArray(file));
    } catch (final IOException e) {
      LOGGER.error(String.format("Fail to read the file: %s. Error: %s", file.getAbsoluteFile(), e.getMessage()));
    }
    return null;
  }

}
