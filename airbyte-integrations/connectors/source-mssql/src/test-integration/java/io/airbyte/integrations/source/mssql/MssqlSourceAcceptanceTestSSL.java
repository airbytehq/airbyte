package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
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

import java.sql.SQLException;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;

public class MssqlSourceAcceptanceTestSSL extends SourceAcceptanceTest {

    private static final String SCHEMA_NAME = "dbo";
    private static final String STREAM_NAME = "id_and_name";

    private static MSSQLServerContainer<?> db;
    private JsonNode config;

    @Override
    protected String getImageName() {
        return "airbyte/source-mssql:dev";
    }

    @Override
    protected ConnectorSpecification getSpec() throws Exception {
        return Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);
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

    private static Database getDatabase(JsonNode baseConfig) {
        return Databases.createDatabase(
                baseConfig.get("username").asText(),
                baseConfig.get("password").asText(),
                String.format("jdbc:sqlserver://%s:%s;encrypt=true;trustServerCertificate=true;",
                        baseConfig.get("host").asText(),
                        baseConfig.get("port").asInt()),
                "com.microsoft.sqlserver.jdbc.SQLServerDriver",
                null);
    }

    // how to interact with the mssql test container manaully.
    // 1. exec into mssql container (not the test container container)
    // 2. /opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P "A_Str0ng_Required_Password"
    @Override
    protected void setup(TestDestinationEnv testEnv) throws SQLException {
        db = new MSSQLServerContainer<>(DockerImageName.parse("airbyte/mssql_ssltest:dev").asCompatibleSubstituteFor("mcr.microsoft.com/mssql/server"))
                .acceptLicense();
        db.start();

        final JsonNode configWithoutDbName = Jsons.jsonNode(ImmutableMap.builder()
                .put("host", db.getHost())
                .put("port", db.getFirstMappedPort())
                .put("username", db.getUsername())
                .put("password", db.getPassword())
                .build());
        final String dbName = "db_" + RandomStringUtils.randomAlphabetic(10).toLowerCase();

        final Database database = getDatabase(configWithoutDbName);
        database.query(ctx -> {
            ctx.fetch(String.format("CREATE DATABASE %s;", dbName));
            ctx.fetch(String.format("USE %s;", dbName));
            ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200), born DATETIMEOFFSET(7));");
            ctx.fetch(
                    "INSERT INTO id_and_name (id, name, born) VALUES (1,'picard', '2124-03-04T01:01:01Z'),  (2, 'crusher', '2124-03-04T01:01:01Z'), (3, 'vash', '2124-03-04T01:01:01Z');");
            return null;
        });

        config = Jsons.clone(configWithoutDbName);
        ((ObjectNode) config).put("database", dbName);
    }

    @Override
    protected void tearDown(TestDestinationEnv testEnv) {
        db.stop();
        db.close();
    }
}
