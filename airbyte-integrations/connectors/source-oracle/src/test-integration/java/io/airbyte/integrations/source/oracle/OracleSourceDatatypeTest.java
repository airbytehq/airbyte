/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle;

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
import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.time.Instant;
import java.util.Calendar;
import java.util.Date;
import java.util.List;
import java.util.TimeZone;
import org.jooq.DSLContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.OracleContainer;

public class OracleSourceDatatypeTest extends AbstractSourceDatabaseTypeTest {

  private OracleContainer container;
  private JsonNode config;

  private static final Logger LOGGER = LoggerFactory.getLogger(OracleSourceDatatypeTest.class);

  @Override
  protected Database setupDatabase() throws Exception {
    container = new OracleContainer("epiclabs/docker-oracle-xe-11g");
    container.start();

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", container.getHost())
        .put("port", container.getFirstMappedPort())
        .put("sid", container.getSid())
        .put("username", container.getUsername())
        .put("password", container.getPassword())
        .put("schemas", List.of("TEST"))
        .build());

    final DSLContext dslContext = DSLContextFactory.create(
        config.get("username").asText(),
        config.get("password").asText(),
        DatabaseDriver.ORACLE.getDriverClassName(),
        String.format(DatabaseDriver.ORACLE.getUrlFormatString(),
            config.get("host").asText(),
            config.get("port").asInt(),
            config.get("sid").asText()), null);
    final Database database = new Database(dslContext);
    LOGGER.warn("config: " + config);

    database.query(ctx -> ctx.fetch("CREATE USER test IDENTIFIED BY test DEFAULT TABLESPACE USERS QUOTA UNLIMITED ON USERS"));

    return database;
  }

  @Override
  protected String getIdColumnName() {
    return "ID";
  }

  @Override
  protected String getTestColumnName() {
    return "TEST_COLUMN";
  }

  @Override
  protected String getNameSpace() {
    return "TEST";
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    container.close();
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-oracle:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected void initTests() {

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("CHAR")
            .airbyteType(JsonSchemaType.STRING)
            .fullSourceDataType("CHAR(3 CHAR)")
            .addInsertValues("null", "'a'", "'ab'", "'abc'")
            .addExpectedValues(null, "a  ", "ab ", "abc")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("VARCHAR2")
            .airbyteType(JsonSchemaType.STRING)
            .fullSourceDataType("VARCHAR2(256)")
            .addInsertValues("null", "'тест'", "'⚡ test ��'", "q'[{|}!\"#$%&'()*+,-./:;<=>?@[]^_`~]'")
            .addExpectedValues(null, "тест", "⚡ test ��", "{|}!\"#$%&'()*+,-./:;<=>?@[]^_`~")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("VARCHAR2")
            .airbyteType(JsonSchemaType.STRING)
            .fullSourceDataType("VARCHAR2(256)")
            .addInsertValues("chr(33) || chr(34) || chr(35) || chr(36) || chr(37) || chr(38) || chr(39) || chr(40) || chr(41)")
            .addExpectedValues("!\"#$%&'()")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("NVARCHAR2")
            .airbyteType(JsonSchemaType.STRING)
            .fullSourceDataType("NVARCHAR2(3)")
            .addInsertValues("null", "N'テスト'")
            .addExpectedValues(null, "テスト")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("NUMBER")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "1", "123.45", "power(10, -130)", "9.99999999999999999999 * power(10, 125)")
            .addExpectedValues(null, "1", "123.45", String.valueOf(Math.pow(10, -130)), String.valueOf(9.99999999999999999999 * Math.pow(10, 125)))
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("NUMBER")
            .airbyteType(JsonSchemaType.NUMBER)
            .fullSourceDataType("NUMBER(6,-2)")
            .addInsertValues("123.89")
            .addExpectedValues("100.0")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("FLOAT")
            .airbyteType(JsonSchemaType.NUMBER)
            .fullSourceDataType("FLOAT(5)")
            .addInsertValues("1.34", "126.45")
            .addExpectedValues("1.3", "130.0")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("FLOAT")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("126.45", "126")
            .addExpectedValues("126.45", "126")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("BINARY_FLOAT")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("126.45f", "1.17549E-38f", "3.40282347E+038f", "BINARY_FLOAT_INFINITY")
            .addExpectedValues("126.45", "1.17549E-38", "3.4028235E38", "Infinity")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("BINARY_DOUBLE")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("126.45d", "2.22507485850720E-308", "1.79769313486231E+308d", "BINARY_DOUBLE_INFINITY")
            .addExpectedValues("126.45", "0.0", "1.79769313486231E308", "Infinity")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("DATE")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("to_date('-4700/01/01','syyyy/mm/dd')",
                "to_date('9999/12/31 23:59:59','yyyy/mm/dd hh24:mi:ss')", "null")
            .addExpectedValues("4700-01-01T00:00:00.000000Z", "9999-12-31T23:59:59.000000Z", null)
            // @TODO stream fails when gets Zero date value
            // .addInsertValues("'2021/01/00'", "'2021/00/00'", "'0000/00/00'")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("TIMESTAMP")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("to_timestamp('2020-06-10 06:14:00.742', 'YYYY-MM-DD HH24:MI:SS.FF')",
                "to_timestamp('2020-06-10 06:14:00.742123', 'YYYY-MM-DD HH24:MI:SS.FF')")
            .addExpectedValues("2020-06-10T06:14:00.742000Z", "2020-06-10T06:14:00.742123Z")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("TIMESTAMP")
            .airbyteType(JsonSchemaType.STRING)
            .fullSourceDataType("TIMESTAMP WITH TIME ZONE")
            .addInsertValues("to_timestamp_tz('21-FEB-2009 18:00:00 EST', 'DD-MON-YYYY HH24:MI:SS TZR')",
                "to_timestamp_tz('21-FEB-2009 18:00:00.123456 EST', 'DD-MON-YYYY HH24:MI:SS.FF TZR')",
                "to_timestamp_tz('21-FEB-2009 18:00:00 -5:00', 'DD-MON-YYYY HH24:MI:SS TZH:TZM')",
                "to_timestamp_tz('21-FEB-2009 18:00:00.123456 -5:00', 'DD-MON-YYYY HH24:MI:SS.FF TZH:TZM')")
            .addExpectedValues("2009-02-21 18:00:00.0 EST", "2009-02-21 18:00:00.123456 EST",
                "2009-02-21 18:00:00.0 -5:00", "2009-02-21 18:00:00.123456 -5:00")
            .build());

    final DateFormat utcFormat = new SimpleDateFormat("dd-MMM-yyyy HH:mm:ss.SSSSSS");
    utcFormat.setTimeZone(TimeZone.getTimeZone(Calendar.getInstance().getTimeZone().getID()));
    Date date = null;
    try {
      date = utcFormat.parse("21-Feb-2009 18:00:00.000456");
    } catch (final ParseException e) {
      LOGGER.error("Unparseable date");
      date = Date.from(Instant.parse("2009-02-21T18:00:00.000456Z"));
    }
    final DateFormat currentTFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSSSSS");
    currentTFormat.setTimeZone(TimeZone.getTimeZone("UTC"));
    final String utc = currentTFormat.format(date);
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("TIMESTAMP")
            .airbyteType(JsonSchemaType.STRING)
            .fullSourceDataType("TIMESTAMP WITH LOCAL TIME ZONE")
            .addInsertValues("to_timestamp_tz('21-FEB-2009 18:00:00.000456', 'DD-MON-YYYY HH24:MI:SS.FF')")
            .addExpectedValues(utc + " UTC")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("INTERVAL")
            .airbyteType(JsonSchemaType.STRING)
            .fullSourceDataType("INTERVAL YEAR TO MONTH")
            .addInsertValues("INTERVAL '10-2' YEAR TO MONTH", "INTERVAL '9' MONTH", "null")
            .addExpectedValues("10-2", "0-9", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("BLOB")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("utl_raw.cast_to_raw('some content here')", "null")
            .addExpectedValues("c29tZSBjb250ZW50IGhlcmU=", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("CLOB")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("utl_raw.cast_to_raw('some content here')", "null")
            .addExpectedValues("736F6D6520636F6E74656E742068657265", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("RAW")
            .airbyteType(JsonSchemaType.STRING)
            .fullSourceDataType("RAW(200)")
            .addInsertValues("utl_raw.cast_to_raw('some content here')", "null")
            .addExpectedValues("c29tZSBjb250ZW50IGhlcmU=", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("LONG")
            .airbyteType(JsonSchemaType.STRING)
            .fullSourceDataType("LONG RAW")
            .addInsertValues("utl_raw.cast_to_raw('some content here')", "null")
            .addExpectedValues("c29tZSBjb250ZW50IGhlcmU=", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("XMLTYPE")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("xmltype('<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" +
                "<list_configuration>\n" +
                "<config>1</config>\n" +
                "<config>2</config>\n" +
                "</list_configuration>')")
            .addExpectedValues("<?xml version = '1.0' encoding = 'UTF-8'?>" +
                "<list_configuration>\n" +
                "   <config>1</config>\n" +
                "   <config>2</config>\n" +
                "</list_configuration>")
            .build());
  }

}
