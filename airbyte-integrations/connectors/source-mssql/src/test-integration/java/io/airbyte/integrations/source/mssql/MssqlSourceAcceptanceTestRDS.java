package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.Field;
import org.apache.commons.lang3.RandomStringUtils;
import org.testcontainers.containers.MSSQLServerContainer;
import org.testcontainers.utility.DockerImageName;

import java.nio.file.Path;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;

public class MssqlSourceAcceptanceTestRDS extends SourceAcceptanceTest {

    private static final String SCHEMA_NAME = "dbo";
    private static final String STREAM_NAME = "id_and_name";

    private static MSSQLServerContainer<?> db;
    private JsonNode baseConfig;
    private JsonNode config;

    @Override
    protected String getImageName() {
        return "airbyte/source-mssql:dev";
    }

    @Override
    protected ConnectorSpecification getSpec() throws Exception {
        return Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);
    }

    public JsonNode getStaticConfig() {
        return Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json")));
    }

    @Override
    protected JsonNode getConfig() {
        return config;
    }

    @Override
    protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
        return CatalogHelpers.createConfiguredAirbyteCatalog(
                STREAM_NAME,
                SCHEMA_NAME,
                Field.of("id", Field.JsonSchemaPrimitive.NUMBER),
                Field.of("name", Field.JsonSchemaPrimitive.STRING),
                Field.of("born", Field.JsonSchemaPrimitive.STRING));
    }

    @Override
    protected JsonNode getState() {
        return Jsons.jsonNode(new HashMap<>());
    }

    @Override
    protected List<String> getRegexTests() {
        return Collections.emptyList();
    }

    private Database getDatabase() {
        String additionalParameter = "";
        JsonNode sslMethod = baseConfig.get("ssl_method");
        switch (sslMethod.get("ssl_method").asText()) {
            case "unencrypted" -> additionalParameter = "encrypt=false;";
            case "encrypted_trust_server_certificate" ->
                additionalParameter = "encrypt=true;trustServerCertificate=true;";
        }
        return Databases.createDatabase(
                baseConfig.get("username").asText(),
                baseConfig.get("password").asText(),
                String.format("jdbc:sqlserver://%s:%s;%s",
                        baseConfig.get("host").asText(),
                        baseConfig.get("port").asInt(),
                        additionalParameter),
                "com.microsoft.sqlserver.jdbc.SQLServerDriver",
                null);
    }

    @Override
    protected void setup(TestDestinationEnv testEnv) throws Exception {
        db = new MSSQLServerContainer<>(DockerImageName.parse("airbyte/mssql_ssltest:dev").asCompatibleSubstituteFor("mcr.microsoft.com/mssql/server"))
                .acceptLicense();
        db.start();

        baseConfig = getStaticConfig();
        String dbName = "db_" + RandomStringUtils.randomAlphabetic(10).toLowerCase();

        final Database database = getDatabase();
        database.query(ctx -> {
            ctx.fetch(
                    "DECLARE @command nvarchar(max)\n" +
                            "SET @command = ''\n" +
                            "SELECT  @command = @command\n" +
                            "    + 'ALTER DATABASE [' + [name] + ']  SET single_user with rollback immediate;'+CHAR(13)+CHAR(10)\n" +
                            "    + 'DROP DATABASE [' + [name] +'];'+CHAR(13)+CHAR(10)\n" +
                            "FROM  [master].[sys].[databases]\n" +
                            "where [name] like 'db_%';\n" +
                            "SELECT @command\n" +
                            "EXECUTE sp_executesql @command");

            ctx.fetch(String.format("CREATE DATABASE %s;", dbName));
            ctx.fetch(String.format("ALTER DATABASE %s SET AUTO_CLOSE OFF WITH NO_WAIT;", dbName));
            ctx.fetch(String.format("USE %s;", dbName));
            ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200), born DATETIMEOFFSET(7));");
            ctx.fetch(
                    "INSERT INTO id_and_name (id, name, born) VALUES (1,'picard', '2124-03-04T01:01:01Z'),  (2, 'crusher', '2124-03-04T01:01:01Z'), (3, 'vash', '2124-03-04T01:01:01Z');");
            return null;
        });

        config = Jsons.clone(baseConfig);
        ((ObjectNode) config).put("database", dbName);
    }

    @Override
    protected void tearDown(TestDestinationEnv testEnv) {
        db.stop();
        db.close();
    }
}
