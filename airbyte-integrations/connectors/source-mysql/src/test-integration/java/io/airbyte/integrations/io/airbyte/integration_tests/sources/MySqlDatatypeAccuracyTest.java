/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.mysql.cj.MysqlType;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.integrations.standardtest.source.TestDataHolder;
import io.airbyte.integrations.source.mysql.MySQLContainerFactory;
import io.airbyte.integrations.source.mysql.MySQLTestDatabase;
import io.airbyte.protocol.models.JsonSchemaType;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

public class MySqlDatatypeAccuracyTest extends AbstractMySqlSourceDatatypeTest {

  @Override
  protected JsonNode getConfig() {
    return testdb.integrationTestConfigBuilder()
        .withoutSsl()
        .withStandardReplication()
        .build();
  }

  @Override
  protected Database setupDatabase() {
    final var sharedContainer = new MySQLContainerFactory().shared("mysql:8.0");
    testdb = new MySQLTestDatabase(sharedContainer)
        .withConnectionProperty("zeroDateTimeBehavior", "convertToNull")
        .initialized()
        .withoutStrictMode();
    return testdb.getDatabase();
  }

  private final Map<String, List<String>> charsetsCollationsMap = Map.of(
      "UTF8", Arrays.asList("UTF8_bin", "UTF8_general_ci"),
      "UTF8MB4", Arrays.asList("UTF8MB4_general_ci", "utf8mb4_0900_ai_ci"),
      "UTF16", Arrays.asList("UTF16_bin", "UTF16_general_ci"),
      "binary", Arrays.asList("binary"),
      "CP1250", Arrays.asList("CP1250_general_ci", "cp1250_czech_cs"));

  @Override
  public boolean testCatalog() {
    return true;
  }

  @Override
  protected void initTests() {
    for (final MysqlType mst : MysqlType.values()) {
      switch (mst) {
        case DECIMAL -> {
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.INTEGER)
                  .fullSourceDataType("%s(10,0)".formatted(mst.getName()))
                  .build());

          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.NUMBER)
                  .fullSourceDataType("%s(%d,30)".formatted(mst.getName(), mst.getPrecision()))
                  .build());
        }
        case DECIMAL_UNSIGNED -> {
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.INTEGER)
                  .fullSourceDataType("DECIMAL(32,0) UNSIGNED")
                  .build());

          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.NUMBER)
                  .fullSourceDataType("DECIMAL(%d,30) UNSIGNED".formatted(mst.getPrecision()))
                  .build());
        }
        case TINYINT -> {
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.BOOLEAN)
                  .fullSourceDataType("%s(1)".formatted(mst.getName()))
                  .build());
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.INTEGER)
                  .fullSourceDataType("%s(%d)".formatted(mst.getName(), mst.getPrecision()))
                  .build());
        }
        case TINYINT_UNSIGNED -> {
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.INTEGER)
                  .fullSourceDataType("TINYINT(1) UNSIGNED")
                  .build());
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.INTEGER)
                  .fullSourceDataType("TINYINT(%d) UNSIGNED".formatted(mst.getPrecision()))
                  .build());
        }
        case BOOLEAN -> {
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.BOOLEAN)
                  .fullSourceDataType("%s".formatted(mst.getName()))
                  .build());
        }
        case SMALLINT, BIGINT, MEDIUMINT, INT -> {
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.INTEGER)
                  .fullSourceDataType("%s(1)".formatted(mst.getName()))
                  .build());
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.INTEGER)
                  .fullSourceDataType("%s(%d)".formatted(mst.getName(), mst.getPrecision()))
                  .build());
        }
        case SMALLINT_UNSIGNED -> {
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.INTEGER)
                  .fullSourceDataType("SMALLINT(1) UNSIGNED")
                  .build());
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.INTEGER)
                  .fullSourceDataType("SMALLINT(%d) UNSIGNED".formatted(mst.getPrecision()))
                  .build());
        }
        case INT_UNSIGNED -> {
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.INTEGER)
                  .fullSourceDataType("INT(1) UNSIGNED")
                  .build());
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.INTEGER)
                  .fullSourceDataType("INT(%d) UNSIGNED".formatted(mst.getPrecision()))
                  .build());
        }
        case FLOAT -> {
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.NUMBER)
                  .fullSourceDataType("%s(0)".formatted(mst.getName()))
                  .build());
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.NUMBER)
                  .fullSourceDataType("%s(24)".formatted(mst.getName()))
                  .build());
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.NUMBER)
                  .fullSourceDataType("%s(25)".formatted(mst.getName()))
                  .build());
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.NUMBER)
                  .fullSourceDataType("%s(53)".formatted(mst.getName()))
                  .build());
        }
        case FLOAT_UNSIGNED -> {
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.NUMBER)
                  .fullSourceDataType("FLOAT(0) UNSIGNED")
                  .build());
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.NUMBER)
                  .fullSourceDataType("FLOAT(24) UNSIGNED")
                  .build());
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.NUMBER)
                  .fullSourceDataType("FLOAT(25) UNSIGNED")
                  .build());
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.NUMBER)
                  .fullSourceDataType("FLOAT(53) UNSIGNED")
                  .build());

        }
        case DOUBLE -> {
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.NUMBER)
                  .fullSourceDataType("DOUBLE PRECISION")
                  .build());
        }
        case DOUBLE_UNSIGNED -> {
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.NUMBER)
                  .fullSourceDataType("DOUBLE PRECISION UNSIGNED")
                  .build());
        }
        case TIMESTAMP -> {
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE)
                  .fullSourceDataType("%s(0)".formatted(mst.getName()))
                  .build());
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE)
                  .fullSourceDataType("%s(6)".formatted(mst.getName()))
                  .build());
        }
        case BIGINT_UNSIGNED -> {
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.INTEGER)
                  .fullSourceDataType("BIGINT(1) UNSIGNED")
                  .build());
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.INTEGER)
                  .fullSourceDataType("BIGINT(%d) UNSIGNED".formatted(mst.getPrecision()))
                  .build());
        }
        case MEDIUMINT_UNSIGNED -> {
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.INTEGER)
                  .fullSourceDataType("MEDIUMINT(1) UNSIGNED")
                  .build());
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.INTEGER)
                  .fullSourceDataType("MEDIUMINT(%d) UNSIGNED".formatted(mst.getPrecision()))
                  .build());
        }
        case DATE -> {
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.STRING_DATE)
                  .fullSourceDataType("%s".formatted(mst.getName()))
                  .build());
        }
        case TIME -> {
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.STRING_TIME_WITHOUT_TIMEZONE)
                  .fullSourceDataType("%s".formatted(mst.getName()))
                  .build());
        }
        case DATETIME -> {
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE)
                  .fullSourceDataType("%s".formatted(mst.getName()))
                  .build());
        }
        case YEAR -> {
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.INTEGER)
                  .fullSourceDataType("%s".formatted(mst.getName()))
                  .build());
        }
        case VARCHAR -> {
          for (final Entry entry : charsetsCollationsMap.entrySet()) {
            List<String> collations = (List<String>) entry.getValue();
            final var airbyteType = (entry.getKey() == "binary") ? JsonSchemaType.STRING_BASE_64 : JsonSchemaType.STRING;
            for (final String collation : collations) {
              addDataTypeTestData(
                  TestDataHolder.builder()
                      .sourceType(mst.name())
                      .airbyteType(airbyteType)
                      .fullSourceDataType("%s(0) CHARACTER SET %s COLLATE %s".formatted(mst.getName(), entry.getKey(), collation))
                      .build());
              addDataTypeTestData(
                  TestDataHolder.builder()
                      .sourceType(mst.name())
                      .airbyteType(airbyteType)
                      .fullSourceDataType("%s(60000) CHARACTER SET %s COLLATE %s".formatted(mst.getName(), entry.getKey(), collation))
                      .build());
            }
          }
        }
        case VARBINARY -> {
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.STRING_BASE_64)
                  .fullSourceDataType("%s(1)".formatted(mst.getName()))
                  .build());
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.STRING_BASE_64)
                  .fullSourceDataType("%s(65000)".formatted(mst.getName()))
                  .build());
        }
        case BIT -> {
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.BOOLEAN)
                  .fullSourceDataType("%s(1)".formatted(mst.getName()))
                  .build());
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.STRING_BASE_64)
                  .fullSourceDataType("%s(64)".formatted(mst.getName()))
                  .build());

        }
        case JSON -> {
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.STRING)
                  .fullSourceDataType("%s".formatted(mst.getName()))
                  .build());
        }
        case ENUM, SET -> {
          for (final Entry entry : charsetsCollationsMap.entrySet()) {
            List<String> collations = (List<String>) entry.getValue();
            for (final String collation : collations) {
              addDataTypeTestData(
                  TestDataHolder.builder()
                      .sourceType(mst.name())
                      .airbyteType(JsonSchemaType.STRING)
                      .fullSourceDataType(
                          "%s('value1', 'value2', 'value3') CHARACTER SET %s COLLATE %s".formatted(mst.getName(), entry.getKey(), collation))
                      .build());
            }
          }
        }
        case TINYBLOB, MEDIUMBLOB, LONGBLOB, GEOMETRY -> {
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.STRING_BASE_64)
                  .fullSourceDataType("%s".formatted(mst.getName()))
                  .build());
        }
        case TINYTEXT, MEDIUMTEXT, LONGTEXT -> {
          for (final Entry entry : charsetsCollationsMap.entrySet()) {
            final var airbyteType = (entry.getKey() == "binary") ? JsonSchemaType.STRING_BASE_64 : JsonSchemaType.STRING;
            List<String> collations = (List<String>) entry.getValue();
            for (final String collation : collations) {
              addDataTypeTestData(
                  TestDataHolder.builder()
                      .sourceType(mst.name())
                      .airbyteType(airbyteType)
                      .fullSourceDataType("%s CHARACTER SET %s COLLATE %s".formatted(mst.getName(), entry.getKey(), collation))
                      .build());
            }
          }
        }
        case BLOB -> {
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.STRING_BASE_64)
                  .fullSourceDataType("%s(0)".formatted(mst.getName()))
                  .build());
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.STRING_BASE_64)
                  .fullSourceDataType("%s(65000)".formatted(mst.getName()))
                  .build());
        }
        case TEXT -> {
          for (final Entry entry : charsetsCollationsMap.entrySet()) {
            final var airbyteType = (entry.getKey() == "binary") ? JsonSchemaType.STRING_BASE_64 : JsonSchemaType.STRING;
            List<String> collations = (List<String>) entry.getValue();
            for (final String collation : collations) {
              addDataTypeTestData(
                  TestDataHolder.builder()
                      .sourceType(mst.name())
                      .airbyteType(airbyteType)
                      .fullSourceDataType("%s(0) CHARACTER SET %s COLLATE %s".formatted(mst.getName(), entry.getKey(), collation))
                      .build());
              addDataTypeTestData(
                  TestDataHolder.builder()
                      .sourceType(mst.name())
                      .airbyteType(airbyteType)
                      .fullSourceDataType("%s(65000) CHARACTER SET %s COLLATE %s".formatted(mst.getName(), entry.getKey(), collation))
                      .build());
            }
          }
        }
        case CHAR -> {
          for (final Entry entry : charsetsCollationsMap.entrySet()) {
            final var airbyteType = (entry.getKey() == "binary") ? JsonSchemaType.STRING_BASE_64 : JsonSchemaType.STRING;
            List<String> collations = (List<String>) entry.getValue();
            for (final String collation : collations) {
              addDataTypeTestData(
                  TestDataHolder.builder()
                      .sourceType(mst.name())
                      .airbyteType(airbyteType)
                      .fullSourceDataType("%s(0) CHARACTER SET %s COLLATE %s".formatted(mst.getName(), entry.getKey(), collation))
                      .build());
              addDataTypeTestData(
                  TestDataHolder.builder()
                      .sourceType(mst.name())
                      .airbyteType(airbyteType)
                      .fullSourceDataType("%s(255) CHARACTER SET %s COLLATE %s".formatted(mst.getName(), entry.getKey(), collation))
                      .build());
            }
          }
        }
        case BINARY -> {
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.STRING_BASE_64)
                  .fullSourceDataType("%s(0)".formatted(mst.getName()))
                  .build());
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(mst.name())
                  .airbyteType(JsonSchemaType.STRING_BASE_64)
                  .fullSourceDataType("%s(255)".formatted(mst.getName()))
                  .build());
        }
        case NULL, UNKNOWN -> {
          // no-op
        }
        default -> throw new IllegalStateException("Unexpected value: " + mst);
      }
    }
  }

}
