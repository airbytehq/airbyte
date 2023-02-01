/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.mysql.cj.MysqlType;
import io.airbyte.db.Database;
import io.airbyte.integrations.standardtest.source.AbstractSourceDatabaseTypeTest;
import io.airbyte.integrations.standardtest.source.TestDataHolder;
import io.airbyte.protocol.models.JsonSchemaType;
import java.io.File;
import java.io.IOException;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.apache.commons.codec.binary.Base64;
import org.apache.commons.io.FileUtils;
import org.apache.commons.lang3.RandomStringUtils;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.MySQLContainer;

public abstract class AbstractMySqlSourceDatatypeTest extends AbstractSourceDatabaseTypeTest {

  protected static final Logger LOGGER = LoggerFactory.getLogger(AbstractMySqlSourceDatatypeTest.class);

  protected MySQLContainer<?> container;
  protected JsonNode config;

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-mysql:dev";
  }

  @Override
  protected abstract Database setupDatabase() throws Exception;

  @Override
  protected String getNameSpace() {
    return container.getDatabaseName();
  }

  @Override
  protected void initTests() {
    // bit defaults to bit(1), which is equivalent to boolean
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bit")
            .airbyteType(JsonSchemaType.BOOLEAN)
            .addInsertValues("null", "1", "0")
            .addExpectedValues(null, "true", "false")
            .build());

    // bit(1) is equivalent to boolean
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bit")
            .fullSourceDataType("bit(1)")
            .airbyteType(JsonSchemaType.BOOLEAN)
            .addInsertValues("null", "1", "0")
            .addExpectedValues(null, "true", "false")
            .build());

    // bit(>1) is binary
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bit")
            .fullSourceDataType("bit(7)")
            .airbyteType(JsonSchemaType.STRING_BASE_64)
            // 1000001 is binary for A
            .addInsertValues("null", "b'1000001'")
            // QQo= is base64 encoding in charset UTF-8 for A
            .addExpectedValues(null, "QQ==")
            .build());

    // tinyint without width
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("tinyint")
            .airbyteType(JsonSchemaType.INTEGER)
            .addInsertValues("null", "-128", "127")
            .addExpectedValues(null, "-128", "127")
            .build());

    // tinyint(1) is equivalent to boolean
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("tinyint")
            .fullSourceDataType("tinyint(1)")
            .airbyteType(JsonSchemaType.BOOLEAN)
            .addInsertValues("null", "1", "0")
            .addExpectedValues(null, "true", "false")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("tinyint")
            .fullSourceDataType("tinyint(1) unsigned")
            .airbyteType(JsonSchemaType.INTEGER)
            .addInsertValues("null", "0", "1", "2", "3")
            .addExpectedValues(null, "0", "1", "2", "3")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("tinyint")
            .fullSourceDataType("tinyint(2)")
            .airbyteType(JsonSchemaType.INTEGER)
            .addInsertValues("null", "-128", "127")
            .addExpectedValues(null, "-128", "127")
            .build());

    final Set<String> booleanTypes = Set.of("BOOLEAN", "BOOL");
    for (final String booleanType : booleanTypes) {
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType(booleanType)
              .airbyteType(JsonSchemaType.BOOLEAN)
              // MySql booleans are tinyint(1), and only 1 is true
              .addInsertValues("null", "1", "0")
              .addExpectedValues(null, "true", "false")
              .build());
    }

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("smallint")
            .airbyteType(JsonSchemaType.INTEGER)
            .addInsertValues("null", "-32768", "32767")
            .addExpectedValues(null, "-32768", "32767")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("smallint")
            .airbyteType(JsonSchemaType.INTEGER)
            .fullSourceDataType("smallint zerofill")
            .addInsertValues("1")
            .addExpectedValues("1")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("smallint")
            .airbyteType(JsonSchemaType.INTEGER)
            .fullSourceDataType("smallint unsigned")
            .addInsertValues("null", "0", "65535")
            .addExpectedValues(null, "0", "65535")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("mediumint")
            .airbyteType(JsonSchemaType.INTEGER)
            .addInsertValues("null", "-8388608", "8388607")
            .addExpectedValues(null, "-8388608", "8388607")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("mediumint")
            .airbyteType(JsonSchemaType.INTEGER)
            .fullSourceDataType("mediumint zerofill")
            .addInsertValues("1")
            .addExpectedValues("1")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("int")
            .airbyteType(JsonSchemaType.INTEGER)
            .addInsertValues("null", "-2147483648", "2147483647")
            .addExpectedValues(null, "-2147483648", "2147483647")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("int")
            .airbyteType(JsonSchemaType.INTEGER)
            .fullSourceDataType("int unsigned")
            .addInsertValues("3428724653")
            .addExpectedValues("3428724653")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("int")
            .airbyteType(JsonSchemaType.INTEGER)
            .fullSourceDataType("int zerofill")
            .addInsertValues("1")
            .addExpectedValues("1")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bigint")
            .airbyteType(JsonSchemaType.INTEGER)
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
            .fullSourceDataType("decimal(10,3)")
            .addInsertValues("0.188", "null")
            .addExpectedValues("0.188", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("decimal")
            .airbyteType(JsonSchemaType.NUMBER)
            .fullSourceDataType("decimal(19,2)")
            .addInsertValues("1700000.01")
            .addExpectedValues("1700000.01")
            .build());

    for (final String type : Set.of("date", "date not null default '0000-00-00'")) {
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType("date")
              .fullSourceDataType(type)
              .airbyteType(JsonSchemaType.STRING_DATE)
              .addInsertValues("'1999-01-08'", "'2021-01-01'")
              .addExpectedValues("1999-01-08", "2021-01-01")
              .build());
    }

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("date")
            .airbyteType(JsonSchemaType.STRING_DATE)
            .addInsertValues("null")
            .addExpectedValues((String) null)
            .build());

    for (final String fullSourceType : Set.of("datetime", "datetime not null default now()")) {
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType("datetime")
              .fullSourceDataType(fullSourceType)
              .airbyteType(JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE)
              .addInsertValues("'2005-10-10 23:22:21'", "'2013-09-05T10:10:02'", "'2013-09-06T10:10:02'")
              .addExpectedValues("2005-10-10T23:22:21.000000", "2013-09-05T10:10:02.000000", "2013-09-06T10:10:02.000000")
              .build());
    }

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("datetime")
            .airbyteType(JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE)
            .addInsertValues("null")
            .addExpectedValues((String) null)
            .build());

    addTimestampDataTypeTest();

    for (final String fullSourceType : Set.of("time", "time not null default '00:00:00'")) {
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType("time")
              .fullSourceDataType(fullSourceType)
              .airbyteType(JsonSchemaType.STRING_TIME_WITHOUT_TIMEZONE)
              // JDBC driver can process only "clock"(00:00:00-23:59:59) values.
              .addInsertValues("'-22:59:59'", "'23:59:59'", "'00:00:00'")
              .addExpectedValues("22:59:59.000000", "23:59:59.000000", "00:00:00.000000")
              .build());

    }

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("time")
            .airbyteType(JsonSchemaType.STRING_TIME_WITHOUT_TIMEZONE)
            // JDBC driver can process only "clock"(00:00:00-23:59:59) values.
            .addInsertValues("null")
            .addExpectedValues((String) null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("year")
            .airbyteType(JsonSchemaType.STRING)
            // MySQL converts values in the ranges '0' - '69' to YEAR value in the range 2000 - 2069
            // and '70' - '99' to 1970 - 1999.
            .addInsertValues("null", "'1997'", "'0'", "'50'", "'70'", "'80'", "'99'")
            .addExpectedValues(null, "1997", "2000", "2050", "1970", "1980", "1999")
            .build());

    // char types can be string or binary, so they are tested separately
    final Set<String> charTypes = Stream.of(MysqlType.CHAR, MysqlType.VARCHAR)
        .map(Enum::name)
        .collect(Collectors.toSet());
    for (final String charType : charTypes) {
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType(charType)
              .airbyteType(JsonSchemaType.STRING)
              .fullSourceDataType(charType + "(63)")
              .addInsertValues("null", "'Airbyte'", "'!\"#$%&\\'()*+,-./:;<=>?\\@[\\]^_\\`{|}~'")
              .addExpectedValues(null, "Airbyte", "!\"#$%&'()*+,-./:;<=>?@[]^_`{|}~")
              .build());

      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType(charType)
              .airbyteType(JsonSchemaType.STRING)
              .fullSourceDataType(charType + "(63) character set utf16")
              .addInsertValues("0xfffd")
              .addExpectedValues("�")
              .build());

      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType(charType)
              .airbyteType(JsonSchemaType.STRING)
              .fullSourceDataType(charType + "(63) character set cp1251")
              .addInsertValues("'тест'")
              .addExpectedValues("тест")
              .build());

      // when charset is binary, return binary in base64 encoding in charset UTF-8
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType(charType)
              .airbyteType(JsonSchemaType.STRING_BASE_64)
              .fullSourceDataType(charType + "(7) character set binary")
              .addInsertValues("null", "'Airbyte'")
              .addExpectedValues(null, "QWlyYnl0ZQ==")
              .build());
    }

    final Set<String> blobTypes = Stream
        .of(MysqlType.TINYBLOB, MysqlType.BLOB, MysqlType.MEDIUMBLOB, MysqlType.LONGBLOB)
        .map(Enum::name)
        .collect(Collectors.toSet());
    for (final String blobType : blobTypes) {
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType(blobType)
              .airbyteType(JsonSchemaType.STRING_BASE_64)
              .addInsertValues("null", "'Airbyte'")
              .addExpectedValues(null, "QWlyYnl0ZQ==")
              .build());
    }

    // binary appends '\0' to the end of the string
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType(MysqlType.BINARY.name())
            .fullSourceDataType(MysqlType.BINARY.name() + "(10)")
            .airbyteType(JsonSchemaType.STRING_BASE_64)
            .addInsertValues("null", "'Airbyte'")
            .addExpectedValues(null, "QWlyYnl0ZQAAAA==")
            .build());

    // varbinary does not append '\0' to the end of the string
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType(MysqlType.VARBINARY.name())
            .fullSourceDataType(MysqlType.VARBINARY.name() + "(10)")
            .airbyteType(JsonSchemaType.STRING_BASE_64)
            .addInsertValues("null", "'Airbyte'")
            .addExpectedValues(null, "QWlyYnl0ZQ==")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType(MysqlType.VARBINARY.name())
            .airbyteType(JsonSchemaType.STRING_BASE_64)
            .fullSourceDataType(MysqlType.VARBINARY.name() + "(20000)") // size should be enough to save test.png
            .addInsertValues("null", "'test'", "'тест'", String.format("FROM_BASE64('%s')", getFileDataInBase64()))
            .addExpectedValues(null, "dGVzdA==", "0YLQtdGB0YI=", getFileDataInBase64())
            .build());

    final Set<String> textTypes = Stream
        .of(MysqlType.TINYTEXT, MysqlType.TEXT, MysqlType.MEDIUMTEXT, MysqlType.LONGTEXT)
        .map(Enum::name)
        .collect(Collectors.toSet());
    final String randomText = RandomStringUtils.random(50, true, true);
    for (final String textType : textTypes) {
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType(textType)
              .airbyteType(JsonSchemaType.STRING)
              .addInsertValues("null", "'Airbyte'", String.format("'%s'", randomText))
              .addExpectedValues(null, "Airbyte", randomText)
              .build());
    }

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("mediumtext")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues(getLogString(1048000), "'test'")
            .addExpectedValues(StringUtils.leftPad("0", 1048000, "0"), "test")
            .build());

    addJsonDataTypeTest();

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("enum")
            .fullSourceDataType("ENUM('xs', 's', 'm', 'l', 'xl')")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'xs'", "'m'")
            .addExpectedValues(null, "xs", "m")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("set")
            .fullSourceDataType("SET('xs', 's', 'm', 'l', 'xl')")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'xs,s'", "'m,xl'")
            .addExpectedValues(null, "xs,s", "m,xl")
            .build());

  }

  protected void addJsonDataTypeTest() {
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("json")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'{\"a\": 10, \"b\": 15}'", "'{\"fóo\": \"bär\"}'", "'{\"春江潮水连海平\": \"海上明月共潮生\"}'")
            .addExpectedValues(null, "{\"a\": 10, \"b\": 15}", "{\"fóo\": \"bär\"}", "{\"春江潮水连海平\": \"海上明月共潮生\"}")
            .build());
  }

  protected void addTimestampDataTypeTest() {
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("timestamp")
            .airbyteType(JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE)
            .addInsertValues("null", "'2021-01-00'", "'2021-00-00'", "'0000-00-00'", "'2022-08-09T10:17:16.161342Z'")
            .addExpectedValues(null, null, null, null, "2022-08-09T10:17:16.000000Z")
            .build());
  }

  private String getLogString(final int length) {
    final int maxLpadLength = 262144;
    final StringBuilder stringBuilder = new StringBuilder("concat(");
    final int fullChunks = length / maxLpadLength;
    stringBuilder.append("lpad('0', 262144, '0'),".repeat(fullChunks));
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
