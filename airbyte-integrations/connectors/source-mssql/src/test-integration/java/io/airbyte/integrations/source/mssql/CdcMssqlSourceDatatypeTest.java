/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.standardtest.source.AbstractSourceDatabaseTypeTest;
import io.airbyte.integrations.standardtest.source.TestDataHolder;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import org.testcontainers.containers.MSSQLServerContainer;

public class CdcMssqlSourceDatatypeTest extends AbstractSourceDatabaseTypeTest {

  private MSSQLServerContainer<?> container;
  private JsonNode config;
  private static final String DB_NAME = "comprehensive";
  private static final String SCHEMA_NAME = "dbo";

  private static final String CREATE_TABLE_SQL = "USE " + DB_NAME + "\nCREATE TABLE %1$s(%2$s INTEGER PRIMARY KEY, %3$s %4$s)";

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    container.close();
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-mssql:dev";
  }

  @Override
  protected Database setupDatabase() throws Exception {
    container = new MSSQLServerContainer<>("mcr.microsoft.com/mssql/server:2019-latest").acceptLicense();
    container.addEnv("MSSQL_AGENT_ENABLED", "True"); // need this running for cdc to work
    container.start();

    final Database database = Databases.createDatabase(
        container.getUsername(),
        container.getPassword(),
        String.format("jdbc:sqlserver://%s:%s",
            container.getHost(),
            container.getFirstMappedPort()),
        "com.microsoft.sqlserver.jdbc.SQLServerDriver",
        null);

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", container.getHost())
        .put("port", container.getFirstMappedPort())
        .put("database", DB_NAME)
        .put("username", container.getUsername())
        .put("password", container.getPassword())
        .put("replication_method", "CDC")
        .build());

    executeQuery("CREATE DATABASE " + DB_NAME + ";");
    executeQuery("ALTER DATABASE " + DB_NAME + "\n\tSET ALLOW_SNAPSHOT_ISOLATION ON");
    executeQuery("USE " + DB_NAME + "\n" + "EXEC sys.sp_cdc_enable_db");

    return database;
  }

  @Override
  protected String getNameSpace() {
    return SCHEMA_NAME;
  }

  private void executeQuery(String query) {
    try (Database database = Databases.createDatabase(
        container.getUsername(),
        container.getPassword(),
        String.format("jdbc:sqlserver://%s:%s",
            container.getHost(),
            container.getFirstMappedPort()),
        "com.microsoft.sqlserver.jdbc.SQLServerDriver",
        null)) {
      database.query(
          ctx -> ctx
              .execute(query));
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  protected void setupEnvironment(TestDestinationEnv environment) throws Exception {
    super.setupEnvironment(environment);
    enableCdcOnAllTables();
  }

  @Override
  protected void initTests() {
    // in SQL Server there is no boolean, BIT is the sole boolean-like column
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bit")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "0", "1", "'true'", "'false'")
            .addExpectedValues(null, "false", "true", "true", "false")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("tinyint")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "0", "255")
            .addExpectedValues(null, "0", "255")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("smallint")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "-32768", "32767")
            .addExpectedValues(null, "-32768", "32767")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("int")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "-2147483648", "2147483647")
            .addExpectedValues(null, "-2147483648", "2147483647")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bigint")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "-9223372036854775808", "9223372036854775807")
            .addExpectedValues(null, "-9223372036854775808", "9223372036854775807")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("real")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "power(1e1, 38)*-3.4", "power(1e1, -38)*-1.18", "power(1e1, -38)*1.18", "power(1e1, 38)*3.4")
            .addExpectedValues(null, String.valueOf(Math.pow(10, 38) * -3.4), String.valueOf(Math.pow(10, -38) * -1.18),
                String.valueOf(Math.pow(10, -38) * 1.18), String.valueOf(Math.pow(10, 38) * 3.4))
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("float")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .fullSourceDataType("float(24)")
            .addInsertValues("null", "power(1e1, 38)*-3.4", "power(1e1, -38)*-1.18", "power(1e1, -38)*1.18", "power(1e1, 38)*3.4")
            .addExpectedValues(null, String.valueOf(Math.pow(10, 38) * -3.4), String.valueOf(Math.pow(10, -38) * -1.18),
                String.valueOf(Math.pow(10, -38) * 1.18), String.valueOf(Math.pow(10, 38) * 3.4))
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("float")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .fullSourceDataType("float(53)")
            .addInsertValues("null", "power(1e1, 308)*-1.79", "power(1e1, -308)*-2.23",
                "power(1e1, -308)*2.23", "power(1e1, 308)*1.79")
            .addExpectedValues(null, String.valueOf(Math.pow(10, 308) * -1.79), String.valueOf(Math.pow(10, -308) * -2.23),
                String.valueOf(Math.pow(10, -308) * 2.23), String.valueOf(Math.pow(10, 308) * 1.79))
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("decimal")
            .fullSourceDataType("DECIMAL(5,2)")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("999", "5.1", "0", "null")
            .addExpectedValues("999.00", "5.10", "0.00", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("numeric")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("'99999'", "null")
            .addExpectedValues("99999", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("money")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "'9990000.99'")
            .addExpectedValues(null, "9990000.9900")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("smallmoney")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "'-214748.3648'", "214748.3647")
            .addExpectedValues(null, "-214748.3648", "214748.3647")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("char")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'a'", "'*'", "null")
            .addExpectedValues("a", "*", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("char")
            .fullSourceDataType("char(8)")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'{asb123}'", "'{asb12}'")
            .addExpectedValues("{asb123}", "{asb12} ")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("varchar")
            .fullSourceDataType("varchar(16)")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'a'", "'abc'", "'{asb123}'", "'   '", "''", "null")
            .addExpectedValues("a", "abc", "{asb123}", "   ", "", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("varchar")
            .fullSourceDataType("varchar(max) COLLATE Latin1_General_100_CI_AI_SC_UTF8")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'a'", "'abc'", "N'Миші йдуть на південь, не питай чому;'", "N'櫻花分店'",
                "''", "null", "N'\\xF0\\x9F\\x9A\\x80'")
            .addExpectedValues("a", "abc", "Миші йдуть на південь, не питай чому;", "櫻花分店", "",
                null, "\\xF0\\x9F\\x9A\\x80")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("text")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'a'", "'abc'", "'Some test text 123$%^&*()_'", "''", "null")
            .addExpectedValues("a", "abc", "Some test text 123$%^&*()_", "", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("nchar")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'a'", "'*'", "N'д'", "null")
            .addExpectedValues("a", "*", "д", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("nvarchar")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .fullSourceDataType("nvarchar(max)")
            .addInsertValues("'a'", "'abc'", "N'Миші ççуть на південь, не питай чому;'", "N'櫻花分店'",
                "''", "null", "N'\\xF0\\x9F\\x9A\\x80'")
            .addExpectedValues("a", "abc", "Миші ççуть на південь, не питай чому;", "櫻花分店", "",
                null, "\\xF0\\x9F\\x9A\\x80")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("nvarchar")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .fullSourceDataType("nvarchar(24)")
            .addInsertValues("'a'", "'abc'", "N'Миші йдуть;'", "N'櫻花分店'", "''", "null")
            .addExpectedValues("a", "abc", "Миші йдуть;", "櫻花分店", "", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("ntext")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'a'", "'abc'", "N'Миші йдуть на південь, не питай чому;'", "N'櫻花分店'",
                "''", "null", "N'\\xF0\\x9F\\x9A\\x80'")
            .addExpectedValues("a", "abc", "Миші йдуть на південь, не питай чому;", "櫻花分店", "",
                null, "\\xF0\\x9F\\x9A\\x80")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("xml")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues(
                "CONVERT(XML, N'<?xml version=\"1.0\"?><book><title>Manual</title><chapter>...</chapter></book>')",
                "null", "''")
            .addExpectedValues("<book><title>Manual</title><chapter>...</chapter></book>", null, "")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("date")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'0001-01-01'", "'9999-12-31'", "'1999-01-08'",
                "null")
            // TODO: Debezium is returning DATE/DATETIME from mssql as integers (days or milli/micro/nanoseconds
            // since the epoch)
            // still useable but requires transformation if true date/datetime type required in destination
            // https://debezium.io/documentation/reference/1.4/connectors/sqlserver.html#sqlserver-data-types
            // .addExpectedValues("0001-01-01T00:00:00Z", "9999-12-31T00:00:00Z",
            // "1999-01-08T00:00:00Z", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("smalldatetime")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'1900-01-01'", "'2079-06-06'", "null")
            // TODO: Debezium is returning DATE/DATETIME from mssql as integers (days or milli/micro/nanoseconds
            // since the epoch)
            // still useable but requires transformation if true date/datetime type required in destination
            // https://debezium.io/documentation/reference/1.4/connectors/sqlserver.html#sqlserver-data-types
            // .addExpectedValues("1900-01-01T00:00:00Z", "2079-06-06T00:00:00Z", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("datetime")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'1753-01-01'", "'9999-12-31'", "null")
            // TODO: Debezium is returning DATE/DATETIME from mssql as integers (days or milli/micro/nanoseconds
            // since the epoch)
            // still useable but requires transformation if true date/datetime type required in destination
            // https://debezium.io/documentation/reference/1.4/connectors/sqlserver.html#sqlserver-data-types
            // .addExpectedValues("1753-01-01T00:00:00Z", "9999-12-31T00:00:00Z", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("datetime2")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'0001-01-01'", "'9999-12-31'", "null")
            // TODO: Debezium is returning DATE/DATETIME from mssql as integers (days or milli/micro/nanoseconds
            // since the epoch)
            // still useable but requires transformation if true date/datetime type required in destination
            // https://debezium.io/documentation/reference/1.4/connectors/sqlserver.html#sqlserver-data-types
            // .addExpectedValues("0001-01-01T00:00:00Z", "9999-12-31T00:00:00Z", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("time")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null")
            // TODO: Debezium is returning DATE/DATETIME from mssql as integers (days or milli/micro/nanoseconds
            // since the epoch)
            // still useable but requires transformation if true date/datetime type required in destination
            // https://debezium.io/documentation/reference/1.4/connectors/sqlserver.html#sqlserver-data-types
            .addNullExpectedValue()
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("datetimeoffset")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'0001-01-10 00:00:00 +01:00'", "'9999-01-10 00:00:00 +01:00'", "null")
            // TODO: BUG - seem to be getting back 0001-01-08T00:00:00+01:00 ... this is clearly wrong
            // .addExpectedValues("0001-01-10 00:00:00.0000000 +01:00",
            // "9999-01-10 00:00:00.0000000 +01:00", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    // TODO BUG Returns binary value instead of actual value
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("binary")
            .airbyteType(JsonSchemaPrimitive.STRING)
            // .addInsertValues("CAST( 'A' AS VARBINARY)", "null")
            // .addExpectedValues("A")
            .addInsertValues("null")
            .addNullExpectedValue()
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    // TODO BUG Returns binary value instead of actual value
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("varbinary")
            .fullSourceDataType("varbinary(30)")
            .airbyteType(JsonSchemaPrimitive.STRING)
            // .addInsertValues("CAST( 'ABC' AS VARBINARY)", "null")
            // .addExpectedValues("A")
            .addInsertValues("null")
            .addNullExpectedValue()
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    // TODO BUG: airbyte returns binary representation instead of readable one
    // create table dbo_1_hierarchyid1 (test_column hierarchyid);
    // insert dbo_1_hierarchyid1 values ('/1/1/');
    // select test_column ,test_column.ToString() AS [Node Text],test_column.GetLevel() [Node Level]
    // from dbo_1_hierarchyid1;
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("hierarchyid")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null")
            .addNullExpectedValue()
            // .addInsertValues("null","'/1/1/'")
            // .addExpectedValues(null, "/1/1/")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("sql_variant")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'a'", "'abc'", "N'Миші йдуть на південь, не питай чому;'", "N'櫻花分店'",
                "''", "null", "N'\\xF0\\x9F\\x9A\\x80'")
            // TODO: BUG - These all come through as nulls, Debezium doesn't mention sql_variant at all so
            // assume unsupported
            // .addExpectedValues("a", "abc", "Миші йдуть на південь, не питай чому;", "櫻花分店", "",
            // null, "\\xF0\\x9F\\x9A\\x80")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    // TODO BUG: Airbyte returns binary representation instead of text one.
    // Proper select query example: SELECT test_column.STAsText() from dbo_1_geometry;
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("geometry")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null")
            .addNullExpectedValue()
            // .addInsertValues("geometry::STGeomFromText('LINESTRING (100 100, 20 180, 180 180)', 0)")
            // .addExpectedValues("LINESTRING (100 100, 20 180, 180 180)",
            // "POLYGON ((0 0, 150 0, 150 150, 0 150, 0 0)", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("uniqueidentifier")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'375CFC44-CAE3-4E43-8083-821D2DF0E626'", "null")
            .addExpectedValues("375CFC44-CAE3-4E43-8083-821D2DF0E626", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    // TODO BUG: Airbyte returns binary representation instead of text one.
    // Proper select query example: SELECT test_column.STAsText() from dbo_1_geography;
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("geography")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null")
            .addNullExpectedValue()
            // .addInsertValues("geography::STGeomFromText('LINESTRING(-122.360 47.656, -122.343 47.656 )',
            // 4326)")
            // .addExpectedValues("LINESTRING(-122.360 47.656, -122.343 47.656 )", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

  }

  private void enableCdcOnAllTables() {
    executeQuery("USE " + DB_NAME + "\n"
        + "DECLARE @TableName VARCHAR(100)\n"
        + "DECLARE @TableSchema VARCHAR(100)\n"
        + "DECLARE CDC_Cursor CURSOR FOR\n"
        + "  SELECT * FROM ( \n"
        + "   SELECT Name,SCHEMA_NAME(schema_id) AS TableSchema\n"
        + "   FROM   sys.objects\n"
        + "   WHERE  type = 'u'\n"
        + "   AND is_ms_shipped <> 1\n"
        + "   ) CDC\n"
        + "OPEN CDC_Cursor\n"
        + "FETCH NEXT FROM CDC_Cursor INTO @TableName,@TableSchema\n"
        + "WHILE @@FETCH_STATUS = 0\n"
        + " BEGIN\n"
        + "   DECLARE @SQL NVARCHAR(1000)\n"
        + "   DECLARE @CDC_Status TINYINT\n"
        + "   SET @CDC_Status=(SELECT COUNT(*)\n"
        + "     FROM   cdc.change_tables\n"
        + "     WHERE  Source_object_id = OBJECT_ID(@TableSchema+'.'+@TableName))\n"
        + "   --IF CDC is not enabled on Table, Enable CDC\n"
        + "   IF @CDC_Status <> 1\n"
        + "     BEGIN\n"
        + "       SET @SQL='EXEC sys.sp_cdc_enable_table\n"
        + "         @source_schema = '''+@TableSchema+''',\n"
        + "         @source_name   = ''' + @TableName\n"
        + "                     + ''',\n"
        + "         @role_name     = null;'\n"
        + "       EXEC sp_executesql @SQL\n"
        + "     END\n"
        + "   FETCH NEXT FROM CDC_Cursor INTO @TableName,@TableSchema\n"
        + "END\n"
        + "CLOSE CDC_Cursor\n"
        + "DEALLOCATE CDC_Cursor");
  }

}
