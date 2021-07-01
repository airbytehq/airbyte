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
import io.airbyte.integrations.standardtest.source.SourceComprehensiveTest;
import io.airbyte.integrations.standardtest.source.TestDataHolder;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import java.sql.SQLException;
import java.util.Optional;
import java.util.stream.Stream;
import org.jooq.Record;
import org.jooq.Result;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.MSSQLServerContainer;

public class CdcMssqlSourceComprehensiveTest extends SourceComprehensiveTest {

  // temp
  private static final Logger LOGGER = LoggerFactory.getLogger(CdcMssqlSourceComprehensiveTest.class);

  private MSSQLServerContainer<?> container;
  private JsonNode config;
  private static final String DB_NAME = "comprehensive";
  private static final String SCHEMA_NAME = "dbo";

  private static final String CREATE_TABLE_SQL ="USE "+DB_NAME+"\nCREATE TABLE %1$s(%2$s INTEGER PRIMARY KEY, %3$s %4$s)";

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
            .airbyteType(JsonSchemaPrimitive.BOOLEAN)
            .addInsertValues("1", "0", "null")
            .addExpectedValues("true", "false", null)
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
            .addExpectedValues(null, String.valueOf(Math.pow(10, 38)*-3.4), String.valueOf(Math.pow(10, -38)*-1.18),
                                     String.valueOf(Math.pow(10, -38)*1.18), String.valueOf(Math.pow(10, 38)*3.4))
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("float")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .fullSourceDataType("float(24)")
            .addInsertValues("null", "power(1e1, 38)*-3.4", "power(1e1, -38)*-1.18", "power(1e1, -38)*1.18", "power(1e1, 38)*3.4")
            .addExpectedValues(null, String.valueOf(Math.pow(10, 38)*-3.4), String.valueOf(Math.pow(10, -38)*-1.18),
                                     String.valueOf(Math.pow(10, -38)*1.18), String.valueOf(Math.pow(10, 38)*3.4))
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("float")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .fullSourceDataType("float(53)")
            .addInsertValues("null", "power(1e1, 308)*-1.79", "power(1e1, -308)*-2.23",
                                     "power(1e1, -308)*2.23", "power(1e1, 308)*1.79")
            .addExpectedValues(null, String.valueOf(Math.pow(10, 308)*-1.79), String.valueOf(Math.pow(10, -308)*-2.23),
                                     String.valueOf(Math.pow(10, -308)*2.23), String.valueOf(Math.pow(10, 308)*1.79))
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("numeric")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .fullSourceDataType("numeric(8,2)")
            .addInsertValues("99999", "5.1", "0", "null")
            // TODO: these get converted to bytes, so we get values back like "AJiWHA=="
//            .addExpectedValues("99999", "5.1", "0", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("decimal")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .fullSourceDataType("decimal(8,2)")
            .addInsertValues("99999", "5.1", "0", "null")
            // TODO: these get converted to bytes, so we get values back like "AJiWHA=="
//            .addExpectedValues("99999", "5.1", "0", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("money")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "-922337203685477.5808", "922337203685477.5807")
            // TODO: these get converted to bytes, so we get values back like "gAAAAAAAAAA="
//            .addExpectedValues(null, "-922337203685477.5808", "922337203685477.5807")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("smallmoney")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "-214748.3648", "214748.3647")
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
            .airbyteType(JsonSchemaPrimitive.STRING)
            .fullSourceDataType("varchar(max)")
            .addInsertValues("null", "'aaaaa1aaabbbbb2bbccccc3cddd4dddee\"5eefff6ffggggg7hhhhhiiiijjjjjkkkklllmmmnnnnnzzzzz{}*&^%$£@£@!'")
            .addExpectedValues(null, "aaaaa1aaabbbbb2bbccccc3cddd4dddee\"5eefff6ffggggg7hhhhhiiiijjjjjkkkklllmmmnnnnnzzzzz{}*&^%$£@£@!")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("nchar")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'a'", "'*'", "'д'", "null")
            .addExpectedValues("a", "*", "д", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("nvarchar")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .fullSourceDataType("nvarchar(max)")
            .addInsertValues("'a'", "'abc'", "'Миші ççуть на південь, не питай чому;'", "'櫻花分店'",
                "''", "null", "'\\xF0\\x9F\\x9A\\x80'")
            .addExpectedValues("a", "abc", "Миші йдуть на південь, не питай чому;", "櫻花分店", "",
                null, "\\xF0\\x9F\\x9A\\x80")
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("nvarchar")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .fullSourceDataType("nvarchar(24)")
            .addInsertValues("'a'", "'abc'", "'Миші йдуть;'", "'櫻花分店'", "''", "null")
            .addExpectedValues("a", "abc", "Миші йдуть;", "櫻花分店 ", "", null)
            .createTablePatternSql(CREATE_TABLE_SQL)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("ntext")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'a'", "'abc'", "'Миші йдуть на південь, не питай чому;'", "'櫻花分店'",
                "''", "null", "'\\xF0\\x9F\\x9A\\x80'")
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
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("date")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues(
                "CONVERT(XML, N'<?xml version=\"1.0\"?><book><title>Manual</title><chapter>...</chapter></book>')",
                "null", "''")
            .addExpectedValues("<book><title>Manual</title><chapter>...</chapter></book>", null, "")
            .build());
//
//    addDataTypeTestData(
//        TestDataHolder.builder()
//            .sourceType("date")
//            .airbyteType(JsonSchemaPrimitive.STRING)
//            .addInsertValues("null", "'2021-01-00'", "'2021-00-00'", "'0000-00-00'")
//            .addExpectedValues(null, null, null, null)
//            .build());
//
//    addDataTypeTestData(
//        TestDataHolder.builder()
//            .sourceType("datetime")
//            .airbyteType(JsonSchemaPrimitive.STRING)
//            .addInsertValues("null", "'0000-00-00 00:00:00'")
//            .addExpectedValues(null, null)
//            .build());
//
//    addDataTypeTestData(
//        TestDataHolder.builder()
//            .sourceType("timestamp")
//            .airbyteType(JsonSchemaPrimitive.STRING)
//            .addInsertValues("null")
//            .addNullExpectedValue()
//            .build());
//
//    addDataTypeTestData(
//        TestDataHolder.builder()
//            .sourceType("time")
//            .airbyteType(JsonSchemaPrimitive.STRING)
//            .addInsertValues("null", "'-838:59:59.000000'", "'00:00:01.000000'")
//            .addExpectedValues(null, "-3020399000000", "1000000")
//            .build());
//
//    addDataTypeTestData(
//        TestDataHolder.builder()
//            .sourceType("varchar")
//            .airbyteType(JsonSchemaPrimitive.STRING)
//            .fullSourceDataType("varchar(256) character set cp1251")
//            .addInsertValues("null", "'тест'")
//            // @TODO stream returns invalid text "С‚РµСЃС‚"
//            // .addExpectedValues(null, "тест")
//            .build());
//
//    addDataTypeTestData(
//        TestDataHolder.builder()
//            .sourceType("varchar")
//            .airbyteType(JsonSchemaPrimitive.STRING)
//            .fullSourceDataType("varchar(256) character set utf16")
//            .addInsertValues("null", "0xfffd")
//            // @TODO streamer returns invalid text "�"
//            // .addExpectedValues(null, "�")
//            .build());
//
//    addDataTypeTestData(
//        TestDataHolder.builder()
//            .sourceType("varchar")
//            .airbyteType(JsonSchemaPrimitive.STRING)
//            .fullSourceDataType("varchar(256)")
//            .addInsertValues("null", "'!\"#$%&\\'()*+,-./:;<=>?\\@[\\]^_\\`{|}~'")
//            .addExpectedValues(null, "!\"#$%&'()*+,-./:;<=>?@[]^_`{|}~")
//            .build());
//
//    addDataTypeTestData(
//        TestDataHolder.builder()
//            .sourceType("varbinary")
//            .airbyteType(JsonSchemaPrimitive.STRING)
//            .fullSourceDataType("varbinary(256)")
//            .addInsertValues("null", "'test'")
//            // @TODO Returns binary value instead of text
//            // .addExpectedValues(null, "test")
//            .build());
//
//    addDataTypeTestData(
//        TestDataHolder.builder()
//            .sourceType("blob")
//            .airbyteType(JsonSchemaPrimitive.STRING)
//            .addInsertValues("null", "'test'")
//            // @TODO Returns binary value instead of text
//            // .addExpectedValues(null, "test")
//            .build());
//
//    addDataTypeTestData(
//        TestDataHolder.builder()
//            .sourceType("mediumtext")
//            .airbyteType(JsonSchemaPrimitive.STRING)
//            .addInsertValues("null", "lpad('0', 16777214, '0')")
//            // @TODO returns null instead of long text
//            // .addExpectedValues(null, StringUtils.leftPad("0", 16777214, "0"))
//            .build());
//
//    addDataTypeTestData(
//        TestDataHolder.builder()
//            .sourceType("tinytext")
//            .airbyteType(JsonSchemaPrimitive.STRING)
//            .addInsertValues("null")
//            .addNullExpectedValue()
//            .build());
//
//    addDataTypeTestData(
//        TestDataHolder.builder()
//            .sourceType("longtext")
//            .airbyteType(JsonSchemaPrimitive.STRING)
//            .addInsertValues("null")
//            .addNullExpectedValue()
//            .build());
//
//    addDataTypeTestData(
//        TestDataHolder.builder()
//            .sourceType("text")
//            .airbyteType(JsonSchemaPrimitive.STRING)
//            .addInsertValues("null")
//            .addNullExpectedValue()
//            .build());
//
//    addDataTypeTestData(
//        TestDataHolder.builder()
//            .sourceType("json")
//            .airbyteType(JsonSchemaPrimitive.STRING)
//            .addInsertValues("null", "'{\"a\": 10, \"b\": 15}'")
//            .addExpectedValues(null, "{\"a\": 10, \"b\": 15}")
//            .build());
//
//    addDataTypeTestData(
//        TestDataHolder.builder()
//            .sourceType("point")
//            .airbyteType(JsonSchemaPrimitive.OBJECT)
//            .addInsertValues("null", "(ST_GeomFromText('POINT(1 1)'))")
//            .build());
//
//    addDataTypeTestData(
//        TestDataHolder.builder()
//            .sourceType("bool")
//            .airbyteType(JsonSchemaPrimitive.STRING)
//            .addInsertValues("null", "1", "127", "-128")
//            // @TODO returns number instead of boolean
//            // .addExpectedValues(null, "true", "false", "false")
//            .build());

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
