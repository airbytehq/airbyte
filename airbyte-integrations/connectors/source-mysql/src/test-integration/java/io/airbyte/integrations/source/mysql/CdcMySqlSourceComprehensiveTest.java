package io.airbyte.integrations.source.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.standardtest.source.DataTypeTest;
import io.airbyte.integrations.standardtest.source.SourceComprehensiveTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.Field;
import org.jooq.SQLDialect;
import org.testcontainers.containers.MySQLContainer;

public class CdcMySqlSourceComprehensiveTest extends SourceComprehensiveTest {

    private MySQLContainer<?> container;
    private JsonNode config;

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

        final Database database = Databases.createDatabase(
                config.get("username").asText(),
                config.get("password").asText(),
                String.format("jdbc:mysql://%s:%s/%s",
                        config.get("host").asText(),
                        config.get("port").asText(),
                        config.get("database").asText()),
                "com.mysql.cj.jdbc.Driver",
                SQLDialect.MYSQL);

        // It disable strict mode in the DB and allows to insert specific values.
        // For example, it's possible to insert date with zero values "2021-00-00"
        database.query(ctx -> ctx.fetch("SET @@sql_mode=''"));

        revokeAllPermissions();
        grantCorrectPermissions();

        return database;
    }

    private void revokeAllPermissions() {
        executeQuery("REVOKE ALL PRIVILEGES, GRANT OPTION FROM " + container.getUsername() + "@'%';");
    }

    private void grantCorrectPermissions() {
        executeQuery(
                "GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO "
                        + container.getUsername() + "@'%';");
    }

    private void executeQuery(String query) {
        try (Database database = Databases.createDatabase(
                "root",
                "test",
                String.format("jdbc:mysql://%s:%s/%s",
                        container.getHost(),
                        container.getFirstMappedPort(),
                        container.getDatabaseName()),
                MySqlSource.DRIVER_CLASS,
                SQLDialect.MYSQL)) {
            database.query(
                    ctx -> ctx
                            .execute(query));
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    protected void initTests() {
        addDataTypeTest(
                DataTypeTest.builder("tinyint", Field.JsonSchemaPrimitive.NUMBER)
                        .addInsertValue("null")
                        .addInsertValue("-128", "127")
                        .build()
        );

        addDataTypeTest(
                DataTypeTest.builder("smallint", Field.JsonSchemaPrimitive.NUMBER)
                        .addInsertValue("null")
                        .addInsertValue("-32768", "32767")
                        .build()
        );

        addDataTypeTest(
                DataTypeTest.builder("smallint", Field.JsonSchemaPrimitive.NUMBER)
                        .fullSourceDataType("smallint zerofill")
                        .addInsertValue("1")
                        .build()
        );

        addDataTypeTest(
                DataTypeTest.builder("mediumint", Field.JsonSchemaPrimitive.NUMBER)
                        .addInsertValue("null", "-8388608", "8388607")
                        .build()
        );

        addDataTypeTest(
                DataTypeTest.builder("mediumint", Field.JsonSchemaPrimitive.NUMBER)
                        .fullSourceDataType("mediumint zerofill")
                        .addInsertValue("1")
                        .build()
        );

        addDataTypeTest(
                DataTypeTest.builder("int", Field.JsonSchemaPrimitive.NUMBER)
                        .addInsertValue("null", "-2147483648", "2147483647")
                        .build()
        );

        addDataTypeTest(
                DataTypeTest.builder("int", Field.JsonSchemaPrimitive.NUMBER)
                        .fullSourceDataType("int zerofill")
                        .addInsertValue("1")
                        .build()
        );

        addDataTypeTest(
                DataTypeTest.builder("bigint", Field.JsonSchemaPrimitive.NUMBER)
                        .addInsertValue("null", "9223372036854775807")
                        .build()
        );

        addDataTypeTest(
                DataTypeTest.builder("float", Field.JsonSchemaPrimitive.NUMBER)
                        .addInsertValue("null")
                        .build()
        );

        addDataTypeTest(
                DataTypeTest.builder("double", Field.JsonSchemaPrimitive.NUMBER)
                        .addInsertValue("null", "power(10, 308)", "1/power(10, 45)")
                        .build()
        );

        addDataTypeTest(
                DataTypeTest.builder("decimal", Field.JsonSchemaPrimitive.NUMBER)
                        .fullSourceDataType("decimal(5,2)")
                        .addInsertValue("null")
                        .build()
        );

        addDataTypeTest(
                DataTypeTest.builder("bit", Field.JsonSchemaPrimitive.NUMBER)
                        .addInsertValue("null", "1", "0")
                        .build()
        );

        addDataTypeTest(
                DataTypeTest.builder("date", Field.JsonSchemaPrimitive.STRING)
                        .addInsertValue("null", "'2021-01-00'", "'2021-00-00'", "'0000-00-00'")
                        .build()
        );

        addDataTypeTest(
                DataTypeTest.builder("datetime", Field.JsonSchemaPrimitive.STRING)
                        .addInsertValue("null", "'0000-00-00 00:00:00'")
                        .build()
        );

        addDataTypeTest(
                DataTypeTest.builder("timestamp", Field.JsonSchemaPrimitive.STRING)
                        .addInsertValue("null")
                        .build()
        );

        addDataTypeTest(
                DataTypeTest.builder("time", Field.JsonSchemaPrimitive.STRING)
                        .addInsertValue("null", "'-838:59:59.000000'")
                        .build()
        );

        addDataTypeTest(
                DataTypeTest.builder("varchar", Field.JsonSchemaPrimitive.STRING)
                        .fullSourceDataType("varchar(256) character set cp1251")
                        .addInsertValue("null", "'тест'")
                        .build()
        );

        addDataTypeTest(
                DataTypeTest.builder("varchar", Field.JsonSchemaPrimitive.STRING)
                        .fullSourceDataType("varchar(256) character set utf16")
                        .addInsertValue("null", "0xfffd")
                        .build()
        );

        addDataTypeTest(
                DataTypeTest.builder("varchar", Field.JsonSchemaPrimitive.STRING)
                        .fullSourceDataType("varchar(256)")
                        .addInsertValue("null", "'!\"#$%&\\'()*+,-./:;<=>?\\@[\\]^_\\`{|}~'")
                        .build()
        );

        addDataTypeTest(
                DataTypeTest.builder("varbinary", Field.JsonSchemaPrimitive.STRING)
                        .fullSourceDataType("varbinary(256)")
                        .addInsertValue("null", "'test'")
                        .build()
        );

        addDataTypeTest(
                DataTypeTest.builder("blob", Field.JsonSchemaPrimitive.STRING)
                        .addInsertValue("null", "'test'")
                        .build()
        );

        addDataTypeTest(
                DataTypeTest.builder("mediumtext", Field.JsonSchemaPrimitive.STRING)
                        .addInsertValue("null", "lpad('0', 16777214, '0')")
                        .build()
        );

        addDataTypeTest(
                DataTypeTest.builder("tinytext", Field.JsonSchemaPrimitive.STRING)
                        .addInsertValue("null")
                        .build()
        );

        addDataTypeTest(
                DataTypeTest.builder("longtext", Field.JsonSchemaPrimitive.STRING)
                        .addInsertValue("null")
                        .build()
        );

        addDataTypeTest(
                DataTypeTest.builder("text", Field.JsonSchemaPrimitive.STRING)
                        .addInsertValue("null")
                        .build()
        );

        addDataTypeTest(
                DataTypeTest.builder("json", Field.JsonSchemaPrimitive.STRING)
                        .addInsertValue("null", "'{\"a\" :10, \"b\": 15}'")
                        .build()
        );

        addDataTypeTest(
                DataTypeTest.builder("point", Field.JsonSchemaPrimitive.OBJECT)
                        .addInsertValue("null", "(ST_GeomFromText('POINT(1 1)'))")
                        .build()
        );

        addDataTypeTest(
                DataTypeTest.builder("bool", Field.JsonSchemaPrimitive.STRING)
                        .addInsertValue("null", "1", "127", "-128")
                        .build()
        );

    }
}
