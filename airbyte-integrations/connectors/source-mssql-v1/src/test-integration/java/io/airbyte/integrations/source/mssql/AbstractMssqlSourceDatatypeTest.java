/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import io.airbyte.cdk.integrations.standardtest.source.AbstractSourceDatabaseTypeTest;
import io.airbyte.cdk.integrations.standardtest.source.TestDataHolder;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.JsonSchemaType;

public abstract class AbstractMssqlSourceDatatypeTest extends AbstractSourceDatabaseTypeTest {

  protected MsSQLTestDatabase testdb;

  @Override
  protected String getNameSpace() {
    return "dbo";
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-mssql-v1:dev";
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    testdb.close();
  }

  protected static final String CREATE_TABLE_SQL = "CREATE TABLE %1$s(%2$s INTEGER PRIMARY KEY, %3$s %4$s)";

  @Override
  protected void initTests() {
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bigint")
            .airbyteType(JsonSchemaType.INTEGER)
            .addInsertValues("-9223372036854775808", "9223372036854775807", "0", "null")
            .addExpectedValues("-9223372036854775808", "9223372036854775807", "0", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("int")
            .airbyteType(JsonSchemaType.INTEGER)
            .addInsertValues("null", "-2147483648", "2147483647")
            .addExpectedValues(null, "-2147483648", "2147483647")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("smallint")
            .airbyteType(JsonSchemaType.INTEGER)
            .addInsertValues("null", "-32768", "32767")
            .addExpectedValues(null, "-32768", "32767")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("tinyint")
            .airbyteType(JsonSchemaType.INTEGER)
            .addInsertValues("null", "0", "255")
            .addExpectedValues(null, "0", "255")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bit")
            .airbyteType(JsonSchemaType.BOOLEAN)
            .addInsertValues("null", "0", "1", "'true'", "'false'")
            .addExpectedValues(null, "false", "true", "true", "false")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("decimal")
            .fullSourceDataType("DECIMAL(5,2)")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("999.33", "null")
            .addExpectedValues("999.33", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("numeric")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("'99999'", "null")
            .addExpectedValues("99999", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("money")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "'9990000.3647'")
            .addExpectedValues(null, "9990000.3647")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("smallmoney")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "'-214748.3648'", "214748.3647")
            .addExpectedValues(null, "-214748.3648", "214748.3647")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("float")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("'123'", "'1234567890.1234567'", "null")
            .addExpectedValues("123.0", "1.2345678901234567E9", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(TestDataHolder.builder()
        .sourceType("real")
        .airbyteType(JsonSchemaType.NUMBER)
        .addInsertValues("'123'", "'1234567890.1234567'", "null")
        .addExpectedValues("123.0", "1.234568E9", null)
        .createTablePatternSql(CREATE_TABLE_SQL)
        .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("date")
            .airbyteType(JsonSchemaType.STRING_DATE)
            .addInsertValues("'0001-01-01'", "'9999-12-31'", "'1999-01-08'", "null")
            .addExpectedValues("0001-01-01", "9999-12-31", "1999-01-08", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("smalldatetime")
            .airbyteType(JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE)
            .addInsertValues("'1900-01-01'", "'2079-06-06'", "null")
            .addExpectedValues("1900-01-01T00:00:00.000000", "2079-06-06T00:00:00.000000", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("datetime")
            .airbyteType(JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE)
            .addInsertValues("'1753-01-01'", "'9999-12-31'", "'9999-12-31T13:00:04'",
                "'9999-12-31T13:00:04.123'", "null")
            .addExpectedValues("1753-01-01T00:00:00.000000", "9999-12-31T00:00:00.000000", "9999-12-31T13:00:04.000000",
                "9999-12-31T13:00:04.123000", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("datetime2")
            .airbyteType(JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE)
            .addInsertValues("'0001-01-01'", "'9999-12-31'", "'9999-12-31T13:00:04.123456'", "null", "'2023-11-08T01:20:11.3733338'")
            .addExpectedValues("0001-01-01T00:00:00.000000", "9999-12-31T00:00:00.000000", "9999-12-31T13:00:04.123456", null,
                "2023-11-08T01:20:11.373333")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("time")
            .airbyteType(JsonSchemaType.STRING_TIME_WITHOUT_TIMEZONE)
            .addInsertValues("null", "'13:00:01'", "'13:00:04Z'", "'13:00:04.123456Z'")
            .addExpectedValues(null, "13:00:01", "13:00:04", "13:00:04.123456")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("datetimeoffset")
            .airbyteType(JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE)
            .addInsertValues("'2001-01-10 00:00:00 +01:00'", "'9999-01-10 00:00:00 +01:00'", "null", "'2024-05-10 19:00:01.604805 +03:00'",
                "'2024-03-02 19:08:07.1234567 +09:00'", "'2024-03-02 19:08:07.12345678 +09:00'")
            .addExpectedValues("2001-01-10T00:00:00.000000+01:00",
                "9999-01-10T00:00:00.000000+01:00", null, "2024-05-10T19:00:01.604805+03:00", "2024-03-02T19:08:07.123456+09:00",
                "2024-03-02T19:08:07.123456+09:00")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("char")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'a'", "'*'", "null")
            .addExpectedValues("a", "*", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("varchar")
            .fullSourceDataType("varchar(max) COLLATE Latin1_General_100_CI_AI_SC_UTF8")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'a'", "'abc'", "N'Миші йдуть на південь, не питай чому;'", "N'櫻花分店'",
                "''", "null", "N'\\xF0\\x9F\\x9A\\x80'")
            .addExpectedValues("a", "abc", "Миші йдуть на південь, не питай чому;", "櫻花分店", "",
                null, "\\xF0\\x9F\\x9A\\x80")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("text")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'a'", "'abc'", "'Some test text 123$%^&*()_'", "''", "null")
            .addExpectedValues("a", "abc", "Some test text 123$%^&*()_", "", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("nchar")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'a'", "'*'", "N'ї'", "null")
            .addExpectedValues("a", "*", "ї", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("nvarchar")
            .fullSourceDataType("nvarchar(max)")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'a'", "'abc'", "N'Миші йдуть на південь, не питай чому;'", "N'櫻花分店'",
                "''", "null", "N'\\xF0\\x9F\\x9A\\x80'")
            .addExpectedValues("a", "abc", "Миші йдуть на південь, не питай чому;", "櫻花分店", "",
                null, "\\xF0\\x9F\\x9A\\x80")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("ntext")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'a'", "'abc'", "N'Миші йдуть на південь, не питай чому;'", "N'櫻花分店'",
                "''", "null", "N'\\xF0\\x9F\\x9A\\x80'")
            .addExpectedValues("a", "abc", "Миші йдуть на південь, не питай чому;", "櫻花分店", "",
                null, "\\xF0\\x9F\\x9A\\x80")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("binary")
            .airbyteType(JsonSchemaType.STRING_BASE_64)
            .addInsertValues("CAST( 'A' AS BINARY(1))", "null")
            .addExpectedValues("QQ==", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("varbinary")
            .fullSourceDataType("varbinary(3)")
            .airbyteType(JsonSchemaType.STRING_BASE_64)
            .addInsertValues("CAST( 'ABC' AS VARBINARY)", "null")
            .addExpectedValues("QUJD", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    // Proper select query example: SELECT test_column.STAsText() from dbo_1_geometry;
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("geometry")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("geometry::STGeomFromText('LINESTRING (100 100, 20 180, 180 180)', 0)",
                "null")
            .addExpectedValues("LINESTRING(100 100, 20 180, 180 180)", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("uniqueidentifier")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'375CFC44-CAE3-4E43-8083-821D2DF0E626'", "null")
            .addExpectedValues("375CFC44-CAE3-4E43-8083-821D2DF0E626", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("xml")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues(
                "'<user><user_id>1</user_id></user>'", "null", "''")
            .addExpectedValues("<user><user_id>1</user_id></user>", null, "")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    // Proper select query example: SELECT test_column.STAsText() from dbo_1_geography;
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("geography")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues(
                "geography::STGeomFromText('LINESTRING(-122.360 47.656, -122.343 47.656 )', 4326)",
                "null")
            .addExpectedValues("LINESTRING(-122.36 47.656, -122.343 47.656)", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    // sql_variant is not supported by debezium, always getting null. So only works for regular sync.
    // The hierarchyid is returned in binary state, but mssql doesn't provide any parcers for it.
    // On a regular sync we do a pre-flight request and then do additional wrap to sql query in case
    // if we have hierarchyid. But this option is not available as we use a third-party tool "Debezium"
    // as a CDC client.
    if (this instanceof MssqlSourceDatatypeTest) {
      // create table dbo_1_hierarchyid1 (test_column hierarchyid);
      // insert dbo_1_hierarchyid1 values ('/1/1/');
      // select test_column ,test_column.ToString() AS [Node Text],test_column.GetLevel() [Node Level]
      // from dbo_1_hierarchyid1;
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType("hierarchyid")
              .airbyteType(JsonSchemaType.STRING)
              .addInsertValues("'/1/1/'", "null")
              .addExpectedValues("/1/1/", null)
              .createTablePatternSql(CREATE_TABLE_SQL)
              .build());

      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType("sql_variant")
              .airbyteType(JsonSchemaType.STRING)
              .addInsertValues("'a'", "'abc'", "N'Миші йдуть на південь, не питай чому;'", "N'櫻花分店'",
                  "''", "null", "N'\\xF0\\x9F\\x9A\\x80'")
              .addExpectedValues("a", "abc", "Миші йдуть на південь, не питай чому;", "櫻花分店", "",
                  null, "\\xF0\\x9F\\x9A\\x80")
              .createTablePatternSql(CREATE_TABLE_SQL)
              .build());

    }

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("int")
            .airbyteType(JsonSchemaType.INTEGER)
            .addInsertValues("null", "1234", "7878")
            .addExpectedValues(null, "1234", "7878")
            .createTablePatternSql("CREATE TABLE %1$s(%2$s INTEGER NULL DEFAULT ((7878)), %3$s %4$s)")
            .build());
  }

}
