/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.singlestore;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.integrations.standardtest.source.AbstractSourceDatabaseTypeTest;
import io.airbyte.cdk.integrations.standardtest.source.TestDataHolder;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.integrations.source.singlestore.SingleStoreTestDatabase.BaseImage;
import io.airbyte.protocol.models.JsonSchemaType;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.apache.commons.lang3.RandomStringUtils;
import org.apache.commons.lang3.StringUtils;
import org.junit.jupiter.api.Order;

@Order(1)
public class SingleStoreSourceDatatypeTest extends AbstractSourceDatabaseTypeTest {

  protected SingleStoreTestDatabase testdb;

  @Override
  protected String getNameSpace() {
    return testdb.getDatabaseName();
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    testdb.close();
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-singlestore:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return testdb.integrationTestConfigBuilder().withStandardReplication().build();
  }

  @Override
  protected Database setupDatabase() throws Exception {
    testdb = SingleStoreTestDatabase.in(BaseImage.SINGLESTORE_DEV);
    return testdb.getDatabase();
  }

  @Override
  protected void initTests() {
    addDataTypeTestData(
        TestDataHolder.builder().sourceType("bit").airbyteType(JsonSchemaType.STRING_BASE_64)
            // 1000001 is binary for A
            .addInsertValues("null", "b'1100101'").addExpectedValues(null, "AAAAAAAAAGU=").build());

    // tinyint without width
    addDataTypeTestData(
        TestDataHolder.builder().sourceType("tinyint").airbyteType(JsonSchemaType.INTEGER)
            .addInsertValues("null", "-128", "127").addExpectedValues(null, "-128", "127").build());

    addDataTypeTestData(
        TestDataHolder.builder().sourceType("tinyint").fullSourceDataType("tinyint(1) unsigned")
            .airbyteType(JsonSchemaType.INTEGER).addInsertValues("null", "0", "1", "2", "3")
            .addExpectedValues(null, "0", "1", "2", "3").build());

    addDataTypeTestData(
        TestDataHolder.builder().sourceType("tinyint").fullSourceDataType("tinyint(2)")
            .airbyteType(JsonSchemaType.INTEGER).addInsertValues("null", "-128", "127")
            .addExpectedValues(null, "-128", "127").build());

    addDataTypeTestData(
        TestDataHolder.builder().sourceType("smallint").airbyteType(JsonSchemaType.INTEGER)
            .addInsertValues("null", "-32768", "32767").addExpectedValues(null, "-32768", "32767")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder().sourceType("smallint").airbyteType(JsonSchemaType.INTEGER)
            .fullSourceDataType("smallint").addInsertValues("1").addExpectedValues("1").build());

    addDataTypeTestData(
        TestDataHolder.builder().sourceType("smallint").airbyteType(JsonSchemaType.INTEGER)
            .fullSourceDataType("smallint unsigned").addInsertValues("null", "0", "65535")
            .addExpectedValues(null, "0", "65535").build());

    addDataTypeTestData(
        TestDataHolder.builder().sourceType("mediumint").airbyteType(JsonSchemaType.INTEGER)
            .addInsertValues("null", "-8388608", "8388607")
            .addExpectedValues(null, "-8388608", "8388607").build());

    addDataTypeTestData(
        TestDataHolder.builder().sourceType("mediumint").airbyteType(JsonSchemaType.INTEGER)
            .fullSourceDataType("mediumint").addInsertValues("1").addExpectedValues("1").build());

    addDataTypeTestData(
        TestDataHolder.builder().sourceType("int").airbyteType(JsonSchemaType.INTEGER)
            .addInsertValues("null", "-2147483648", "2147483647")
            .addExpectedValues(null, "-2147483648", "2147483647").build());

    addDataTypeTestData(
        TestDataHolder.builder().sourceType("int").airbyteType(JsonSchemaType.INTEGER)
            .fullSourceDataType("int unsigned").addInsertValues("3428724653")
            .addExpectedValues("3428724653").build());

    addDataTypeTestData(
        TestDataHolder.builder().sourceType("int").airbyteType(JsonSchemaType.INTEGER)
            .fullSourceDataType("int").addInsertValues("1").addExpectedValues("1").build());

    addDataTypeTestData(
        TestDataHolder.builder().sourceType("bigint").airbyteType(JsonSchemaType.INTEGER)
            .addInsertValues("null", "9223372036854775807")
            .addExpectedValues(null, "9223372036854775807").build());

    addDataTypeTestData(
        TestDataHolder.builder().sourceType("float").airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "10.5").addExpectedValues(null, "10.5").build());

    addDataTypeTestData(
        TestDataHolder.builder().sourceType("double").airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "power(10, 308)", "1/power(10, 45)", "10.5")
            .addExpectedValues(null, String.valueOf(Math.pow(10, 308)),
                String.valueOf(1 / Math.pow(10, 45)), "10.5")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder().sourceType("decimal").airbyteType(JsonSchemaType.NUMBER)
            .fullSourceDataType("decimal(10,3)").addInsertValues("0.188", "null")
            .addExpectedValues("0.188", null).build());

    addDataTypeTestData(
        TestDataHolder.builder().sourceType("decimal").airbyteType(JsonSchemaType.INTEGER)
            .fullSourceDataType("decimal(32,0)").addInsertValues("1700000.01", "123")
            .addExpectedValues("1700000", "123").build());

    for (final String type : Set.of("date", "date not null default '0000-00-00'")) {
      addDataTypeTestData(TestDataHolder.builder().sourceType("date").fullSourceDataType(type)
          .airbyteType(JsonSchemaType.STRING_DATE)
          .addInsertValues("'1999-01-08'", "'2021-01-01'", "'2022/11/12'", "'1987.12.01'")
          .addExpectedValues("1999-01-08", "2021-01-01", "2022-11-12", "1987-12-01").build());
    }

    addDataTypeTestData(
        TestDataHolder.builder().sourceType("date").airbyteType(JsonSchemaType.STRING_DATE)
            .addInsertValues("null").addExpectedValues((String) null).build());

    addDataTypeTestData(
        TestDataHolder.builder().sourceType("date").airbyteType(JsonSchemaType.STRING_DATE)
            .addInsertValues("0000-00-00").addExpectedValues("0000-00-00").build());

    for (final String fullSourceType : Set.of("datetime", "datetime not null default now()")) {
      addDataTypeTestData(
          TestDataHolder.builder().sourceType("datetime").fullSourceDataType(fullSourceType)
              .airbyteType(JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE)
              .addInsertValues("'1000-01-01 00:00:01'", "'2005-10-10 23:22:21'",
                  "'2013-09-05T10:10:02'", "'2013-09-06T10:10:02'", "'9999-12-31 23:59:59'")
              .addExpectedValues("1000-01-01T00:00:01", "2005-10-10T23:22:21",
                  "2013-09-05T10:10:02", "2013-09-06T10:10:02", "9999-12-31T23:59:59")
              .build());
    }

    for (final String fullSourceType : Set.of("datetime(6)",
        "datetime(6) not null default now(6)")) {
      addDataTypeTestData(
          TestDataHolder.builder().sourceType("datetime").fullSourceDataType(fullSourceType)
              .airbyteType(JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE)
              .addInsertValues("'1000-01-01 00:00:00.000001'", "'9999-12-31 23:59:59.999999'")
              .addExpectedValues("1000-01-01T00:00:00.000001", "9999-12-31T23:59:59.999999")
              .build());
    }

    addDataTypeTestData(TestDataHolder.builder().sourceType("datetime")
        .airbyteType(JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE).addInsertValues("null")
        .addExpectedValues((String) null).build());

    for (final String fullSourceType : Set.of("timestamp", "timestamp not null default now()")) {
      addDataTypeTestData(
          TestDataHolder.builder().sourceType("timestamp").fullSourceDataType(fullSourceType)
              .airbyteType(JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE)
              .addInsertValues("'1970-01-01 00:00:01'", "'2038-01-19 03:14:07'")
              .addExpectedValues("1970-01-01T00:00:01", "2038-01-19T03:14:07").build());
    }

    for (final String fullSourceType : Set.of("timestamp(6)",
        "timestamp(6) not null default now(6)")) {
      addDataTypeTestData(
          TestDataHolder.builder().sourceType("timestamp").fullSourceDataType(fullSourceType)
              .airbyteType(JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE)
              .addInsertValues("'1970-01-01 00:00:01.000001'", "'2038-01-19 03:14:07.999999'")
              .addExpectedValues("1970-01-01T00:00:01.000001", "2038-01-19T03:14:07.999999")
              .build());
    }

    for (final String fullSourceType : Set.of("time", "time not null default '00:00:00'")) {
      addDataTypeTestData(
          TestDataHolder.builder().sourceType("time").fullSourceDataType(fullSourceType)
              .airbyteType(JsonSchemaType.STRING)
              // JDBC driver can process only "clock"(00:00:00-23:59:59) values.
              .addInsertValues("'-838:59:59'", "'838:59:59'", "'00:00:00'")
              .addExpectedValues("-838:59:59", "838:59:59", "00:00:00").build());
    }

    for (final String fullSourceType : Set.of("time(6)",
        "time(6) not null default '00:00:00.000000'")) {
      addDataTypeTestData(
          TestDataHolder.builder().sourceType("time").fullSourceDataType(fullSourceType)
              .airbyteType(JsonSchemaType.STRING)
              .addInsertValues("'-838:59:59.000000'", "'837:59:59.999999'", "'00:00:00.000000'")
              .addExpectedValues("-838:59:59.000000", "837:59:59.999999", "00:00:00.000000")
              .build());
    }

    addDataTypeTestData(
        TestDataHolder.builder().sourceType("time").airbyteType(JsonSchemaType.STRING)
            // JDBC driver can process only "clock"(00:00:00-23:59:59) values.
            .addInsertValues("null").addExpectedValues((String) null).build());

    addDataTypeTestData(
        TestDataHolder.builder().sourceType("year").airbyteType(JsonSchemaType.INTEGER)
            // S2 converts values in the ranges '0' - '69' to YEAR value in the range 2000 - 2069
            // and '70' - '99' to 1970 - 1999.
            .addInsertValues("null", "'1997'", "'0'", "'50'", "'70'", "'80'", "'99'", "'00'",
                "'000'")
            .addExpectedValues(null, "1997", "2000", "2050", "1970", "1980", "1999", "2000", "2000")
            .build());
    // char types can be string or binary, so they are tested separately
    final Set<String> charTypes = Stream.of(SingleStoreType.CHAR, SingleStoreType.VARCHAR)
        .map(Enum::name).collect(Collectors.toSet());
    for (final String charType : charTypes) {
      addDataTypeTestData(
          TestDataHolder.builder().sourceType(charType).airbyteType(JsonSchemaType.STRING)
              .fullSourceDataType(charType + "(63)")
              .addInsertValues("null", "'Airbyte'", "'!\"#$%&\\'()*+,-./:;<=>?\\@[\\]^_\\`|~'")
              .addExpectedValues(null, "Airbyte", "!\"#$%&'()*+,-./:;<=>?@[]^_`|~").build());
    }
    final Set<String> blobTypes = Stream.of(SingleStoreType.TINYBLOB, SingleStoreType.BLOB,
        SingleStoreType.MEDIUMBLOB, SingleStoreType.LONGBLOB).map(Enum::name)
        .collect(Collectors.toSet());
    for (final String blobType : blobTypes) {
      addDataTypeTestData(
          TestDataHolder.builder().sourceType(blobType).airbyteType(JsonSchemaType.STRING_BASE_64)
              .addInsertValues("null", "'Airbyte'").addExpectedValues(null, "QWlyYnl0ZQ==")
              .build());
    }
    // binary appends '\0' to the end of the string
    addDataTypeTestData(TestDataHolder.builder().sourceType(SingleStoreType.BINARY.name())
        .fullSourceDataType(SingleStoreType.BINARY.name() + "(10)")
        .airbyteType(JsonSchemaType.STRING_BASE_64).addInsertValues("null", "'Airbyte'")
        .addExpectedValues(null, "QWlyYnl0ZQAAAA==").build());
    // varbinary does not append '\0' to the end of the string
    addDataTypeTestData(TestDataHolder.builder().sourceType(SingleStoreType.VARBINARY.name())
        .fullSourceDataType(SingleStoreType.VARBINARY.name() + "(10)")
        .airbyteType(JsonSchemaType.STRING_BASE_64).addInsertValues("null", "'Airbyte'")
        .addExpectedValues(null, "QWlyYnl0ZQ==").build());

    final Set<String> textTypes = Stream.of(SingleStoreType.TINYTEXT, SingleStoreType.TEXT,
        SingleStoreType.MEDIUMTEXT, SingleStoreType.LONGTEXT).map(Enum::name)
        .collect(Collectors.toSet());
    final String randomText = RandomStringUtils.random(50, true, true);
    for (final String textType : textTypes) {
      addDataTypeTestData(
          TestDataHolder.builder().sourceType(textType).airbyteType(JsonSchemaType.STRING)
              .addInsertValues("null", "'Airbyte'", String.format("'%s'", randomText))
              .addExpectedValues(null, "Airbyte", randomText).build());
    }
    addDataTypeTestData(
        TestDataHolder.builder().sourceType("mediumtext").airbyteType(JsonSchemaType.STRING)
            .addInsertValues(getLogString(1048000), "'test'")
            .addExpectedValues(StringUtils.leftPad("0", 1048000, "0"), "test").build());
    addDataTypeTestData(
        TestDataHolder.builder().sourceType("json").airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'{\"a\": 10, \"b\": 15}'", "'{\"fóo\": \"bär\"}'",
                "'{\"春江潮水连海平\":\"海上明月共潮生\"}'")
            .addExpectedValues(null, "{\"a\":10,\"b\":15}", "{\"fóo\":\"bär\"}",
                "{\"春江潮水连海平\":\"海上明月共潮生\"}")
            .build());
    addDataTypeTestData(TestDataHolder.builder().sourceType("enum")
        .fullSourceDataType("ENUM('xs', 's', 'm', 'l', 'xl')").airbyteType(JsonSchemaType.STRING)
        .addInsertValues("null", "'xs'", "'m'").addExpectedValues(null, "xs", "m").build());
    addDataTypeTestData(TestDataHolder.builder().sourceType("set")
        .fullSourceDataType("SET('xs', 's', 'm', 'l', 'xl')").airbyteType(JsonSchemaType.STRING)
        .addInsertValues("null", "'xs,s'", "'m,xl'").addExpectedValues(null, "xs,s", "m,xl")
        .build());
    addDataTypeTestData(
        TestDataHolder.builder().sourceType("decimal").airbyteType(JsonSchemaType.NUMBER)
            .fullSourceDataType("decimal(19,2)").addInsertValues("1700000.01", "'123'")
            .addExpectedValues("1700000.01", "123.0").build());
    addDataTypeTestData(
        TestDataHolder.builder().sourceType("GEOGRAPHYPOINT").airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'POINT(1.5 1.5)'").addExpectedValues("POINT(1.50000003 1.50000000)")
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

}
