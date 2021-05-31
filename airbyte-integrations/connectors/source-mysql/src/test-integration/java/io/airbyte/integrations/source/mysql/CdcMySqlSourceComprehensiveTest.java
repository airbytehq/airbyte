package io.airbyte.integrations.source.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.standardtest.source.SourceComprehensiveTest;
import io.airbyte.integrations.standardtest.source.SourceTest;
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
    protected void tearDown(SourceTest.TestDestinationEnv testEnv) {
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
                dataTypeTestBuilder("tinyint", Field.JsonSchemaPrimitive.NUMBER)
                        .addInsertValue("null")
                        .addInsertValue("-128", "127")
                        .build()
        );

        addDataTypeTest(
                dataTypeTestBuilder("smallint", Field.JsonSchemaPrimitive.NUMBER)
                        .addInsertValue("null")
                        .addInsertValue("-32768", "32767")
                        .build()
        );

        addDataTypeTest(
                dataTypeTestBuilder("smallint", Field.JsonSchemaPrimitive.NUMBER)
                        .setFullSourceDataType("smallint zerofill")
                        .addInsertValue("1")
                        .build()
        );

        addDataTypeTest(
                dataTypeTestBuilder("mediumint", Field.JsonSchemaPrimitive.NUMBER)
                        .addInsertValue("null", "-8388608", "8388607")
                        .build()
        );

        addDataTypeTest(
                dataTypeTestBuilder("mediumint", Field.JsonSchemaPrimitive.NUMBER)
                        .setFullSourceDataType("mediumint zerofill")
                        .addInsertValue("1")
                        .build()
        );

        addDataTypeTest(
                dataTypeTestBuilder("int", Field.JsonSchemaPrimitive.NUMBER)
                        .addInsertValue("null", "-2147483648", "2147483647")
                        .build()
        );

        addDataTypeTest(
                dataTypeTestBuilder("int", Field.JsonSchemaPrimitive.NUMBER)
                        .setFullSourceDataType("int zerofill")
                        .addInsertValue("1")
                        .build()
        );

        addDataTypeTest(
                dataTypeTestBuilder("bigint", Field.JsonSchemaPrimitive.NUMBER)
                        .addInsertValue("null", "9223372036854775807")
                        .build()
        );

        addDataTypeTest(
                dataTypeTestBuilder("float", Field.JsonSchemaPrimitive.NUMBER)
                        .addInsertValue("null")
                        .build()
        );

        addDataTypeTest(
                dataTypeTestBuilder("double", Field.JsonSchemaPrimitive.NUMBER)
                        .addInsertValue("null", "power(10, 308)", "1/power(10, 45)")
                        .build()
        );

        addDataTypeTest(
                dataTypeTestBuilder("decimal", Field.JsonSchemaPrimitive.NUMBER)
                        .setFullSourceDataType("decimal(5,2)")
                        .addInsertValue("null")
                        .build()
        );

        addDataTypeTest(
                dataTypeTestBuilder("bit", Field.JsonSchemaPrimitive.NUMBER)
                        .addInsertValue("null", "1", "0")
                        .build()
        );

        addDataTypeTest(
                dataTypeTestBuilder("date", Field.JsonSchemaPrimitive.STRING)
                        .addInsertValue("null", "'2021-01-00'", "'2021-00-00'", "'0000-00-00'")
                        .build()
        );

        addDataTypeTest(
                dataTypeTestBuilder("datetime", Field.JsonSchemaPrimitive.STRING)
                        .addInsertValue("null", "'0000-00-00 00:00:00'")
                        .build()
        );

        addDataTypeTest(
                dataTypeTestBuilder("timestamp", Field.JsonSchemaPrimitive.STRING)
                        .addInsertValue("null")
                        .build()
        );

        addDataTypeTest(
                dataTypeTestBuilder("time", Field.JsonSchemaPrimitive.STRING)
                        .addInsertValue("null", "'-838:59:59.000000'")
                        .build()
        );

        addDataTypeTest(
                dataTypeTestBuilder("varchar", Field.JsonSchemaPrimitive.STRING)
                        .setFullSourceDataType("varchar(256) character set cp1251")
                        .addInsertValue("null", "'тест'")
                        .build()
        );

        addDataTypeTest(
                dataTypeTestBuilder("varchar", Field.JsonSchemaPrimitive.STRING)
                        .setFullSourceDataType("varchar(256) character set utf16")
                        .addInsertValue("null", "0xfffd")
                        .build()
        );

        addDataTypeTest(
                dataTypeTestBuilder("varchar", Field.JsonSchemaPrimitive.STRING)
                        .setFullSourceDataType("varchar(256)")
                        .addInsertValue("null", "'!\"#$%&\\'()*+,-./:;<=>?\\@[\\]^_\\`{|}~'")
                        .build()
        );

        addDataTypeTest(
                dataTypeTestBuilder("varbinary", Field.JsonSchemaPrimitive.STRING)
                        .setFullSourceDataType("varbinary(256)")
                        .addInsertValue("null", "'test'")
                        .build()
        );

        addDataTypeTest(
                dataTypeTestBuilder("blob", Field.JsonSchemaPrimitive.STRING)
                        .addInsertValue("null", "'test'")
                        .build()
        );

        addDataTypeTest(
                dataTypeTestBuilder("mediumtext", Field.JsonSchemaPrimitive.STRING)
                        .addInsertValue("null", "lpad('0', 16777214, '0')")
                        .build()
        );

        addDataTypeTest(
                dataTypeTestBuilder("tinytext", Field.JsonSchemaPrimitive.STRING)
                        .addInsertValue("null")
                        .build()
        );

        addDataTypeTest(
                dataTypeTestBuilder("longtext", Field.JsonSchemaPrimitive.STRING)
                        .addInsertValue("null")
                        .build()
        );

        addDataTypeTest(
                dataTypeTestBuilder("text", Field.JsonSchemaPrimitive.STRING)
                        .addInsertValue("null")
                        .build()
        );

        addDataTypeTest(
                dataTypeTestBuilder("json", Field.JsonSchemaPrimitive.STRING)
                        .addInsertValue("null", "'{\"a\" :10, \"b\": 15}'")
                        .build()
        );

        addDataTypeTest(
                dataTypeTestBuilder("point", Field.JsonSchemaPrimitive.OBJECT)
                        .addInsertValue("null", "(ST_GeomFromText('POINT(1 1)'))")
                        .build()
        );

        addDataTypeTest(
                dataTypeTestBuilder("bool", Field.JsonSchemaPrimitive.STRING)
                        .addInsertValue("null", "1", "127", "-128")
                        .build()
        );

    }
}
