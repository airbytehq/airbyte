/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.vertica;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.integrations.util.HostPortResolver;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.*;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.Test;
import io.airbyte.commons.json.Jsons;
import com.google.common.collect.ImmutableMap;
import io.airbyte.db.jdbc.JdbcUtils;
import org.junit.jupiter.api.extension.ExtendWith;

import javax.sql.DataSource;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertTrue;



public class VerticaSourceAcceptanceTest extends SourceAcceptanceTest {


    private VerticaContainer db;
    private JsonNode config;
    private DataSource dataSource;

    private static final String STREAM_NAME = "id_and_name";

    private static final String STREAM_NAME_MATERIALIZED_VIEW = "test";

    private static final String SCHEMA_NAME = "public";
    private static final String STREAM_NAME1 = "ID_AND_NAME1";
    private static final String STREAM_NAME2 = "ID_AND_NAME2";
    private static final String STREAM_NAME3 = "ID_AND_NAME3";

    public static final String LIMIT_PERMISSION_SCHEMA = "limit_perm_schema";
    public static final String LIMIT_PERMISSION_ROLE = "limit_perm_role";
    public static final String LIMIT_PERMISSION_ROLE_PASSWORD = "test";

    private Database database;

    private ConfiguredAirbyteCatalog configCatalog;

    @Override
    protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
//        db = new VerticaContainer("vertica/vertica-ce:latest");
        db= new VerticaContainer();
        db.start();
        config = getlocalConfig();
        dataSource = DataSourceFactory.create(
                config.get(JdbcUtils.USERNAME_KEY).asText(),
                config.get(JdbcUtils.PASSWORD_KEY).asText(),
                VerticaSource.DRIVER_CLASS,
                String.format(DatabaseDriver.VERTICA.getUrlFormatString(),
                        config.get(JdbcUtils.HOST_KEY).asText(),
                        config.get(JdbcUtils.PORT_KEY).asInt(),
                        config.get(JdbcUtils.SCHEMA_KEY).asText()));

//        System.out.println("dataSource.getConnection().toString()--------"+dataSource.getConnection().toString());
//        System.out.println("dataSource.getConnection().toString()--------"+dataSource.);
//
//        try (final DSLContext dslContext = DSLContextFactory.create(
//                config.get(JdbcUtils.USERNAME_KEY).asText(),
//                config.get(JdbcUtils.PASSWORD_KEY).asText(),
//                DatabaseDriver.VERTICA.getDriverClassName(),
//                String.format(DatabaseDriver.VERTICA.getUrlFormatString(),
//                        db.getHost(),
//                        db.getFirstMappedPort(),
//                        config.get(JdbcUtils.DATABASE_KEY).asText()),
//                SQLDialect.POSTGRES)) {
//            database = new Database(dslContext);
//
//            System.out.println("database setup "+database.toString());
//
//            database.query(ctx -> {
//                ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");
//                ctx.fetch("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
//                ctx.fetch("CREATE TABLE starships(id INTEGER, name VARCHAR(200));");
//                ctx.fetch("INSERT INTO starships (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');");
//                ctx.fetch("CREATE MATERIALIZED VIEW testview AS select * from id_and_name where id = '2';");
//                return null;
//            });
//
            DataSourceFactory.close(dataSource);
//        }
//        configCatalog = getCommonConfigCatalog();


    }

    @Override
    protected String getImageName() {
//        return "vertica/vertica-ce:latest";
        return "airbyte/source-vertica:dev";

//        return "airbytesimplify3x/source-vertica:dev";
    }

    @Override
    protected ConnectorSpecification getSpec() throws Exception {
        try {
            System.out.println("deserilized vaeriosn of config---->"+getConfig().toString());
            System.out.println("connection specifications-->"+Jsons.deserialize(MoreResources.readResource("spec.json"),ConnectorSpecification.class).toString());
        }
        catch (Exception e)
        {
            e.fillInStackTrace();
        }
        return  Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);

    }


    protected JsonNode getlocalConfig() {
        final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
                .put("method", "Standard")
                .build());

        return Jsons.jsonNode(ImmutableMap.builder().put(JdbcUtils.HOST_KEY, "140.236.88.151")
            .put(JdbcUtils.USERNAME_KEY, "airbyte")
            .put(JdbcUtils.PASSWORD_KEY, "airbyte123")
            .put(JdbcUtils.SCHEMA_KEY,  List.of("public"))
            .put(JdbcUtils.PORT_KEY, 5433)
            .put(JdbcUtils.DATABASE_KEY, "airbyte")
            .put("replication_method", replicationMethod)
            .build());
    }

    @Override
    protected JsonNode getConfig() {
        System.out.println("from get configration --->"+config.toString());
        return  config;
    }



    @Override
    protected ConfiguredAirbyteCatalog getConfiguredCatalog() throws Exception {
        return CatalogHelpers.createConfiguredAirbyteCatalog(
                STREAM_NAME,
                SCHEMA_NAME,
                Field.of("id", JsonSchemaType.NUMBER),
                Field.of("name", JsonSchemaType.STRING));
    }

    @Override
    protected JsonNode getState() {
        return Jsons.jsonNode(new HashMap<>());
    }


    @Override
    protected void tearDown(final TestDestinationEnv testEnv) {
        db.close();
    }
    @Test
    public void testCheckPrivilegesForUserWithLessPerm() throws Exception {
        final JsonNode config = getlocalConfig();
    }

    @Test
    public void testCheckPrivilegesForUserWithoutPerm() throws Exception {
        final JsonNode config = getlocalConfig();
    }


    @Override
    protected void verifyCatalog(AirbyteCatalog catalog) throws Exception {
        super.verifyCatalog(catalog);
    }

    private ConfiguredAirbyteCatalog getCommonConfigCatalog() {
        return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
                new ConfiguredAirbyteStream()
                        .withSyncMode(SyncMode.INCREMENTAL)
                        .withCursorField(Lists.newArrayList("id"))
                        .withDestinationSyncMode(DestinationSyncMode.APPEND)
                        .withStream(CatalogHelpers.createAirbyteStream(
                                        STREAM_NAME, SCHEMA_NAME,
                                        Field.of("id", JsonSchemaType.NUMBER),
                                        Field.of("name", JsonSchemaType.STRING))
                                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
                                .withSourceDefinedPrimaryKey(List.of(List.of("id")))),
                new ConfiguredAirbyteStream()
                        .withSyncMode(SyncMode.INCREMENTAL)
                        .withCursorField(Lists.newArrayList("id"))
                        .withDestinationSyncMode(DestinationSyncMode.APPEND)
                        .withStream(CatalogHelpers.createAirbyteStream(
                                        STREAM_NAME2, SCHEMA_NAME,
                                        Field.of("id", JsonSchemaType.NUMBER),
                                        Field.of("name", JsonSchemaType.STRING))
                                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
                                .withSourceDefinedPrimaryKey(List.of(List.of("id")))),
                new ConfiguredAirbyteStream()
                        .withSyncMode(SyncMode.INCREMENTAL)
                        .withCursorField(Lists.newArrayList("id"))
                        .withDestinationSyncMode(DestinationSyncMode.APPEND)
                        .withStream(CatalogHelpers.createAirbyteStream(
                                        STREAM_NAME_MATERIALIZED_VIEW, SCHEMA_NAME,
                                        Field.of("id", JsonSchemaType.NUMBER),
                                        Field.of("name", JsonSchemaType.STRING))
                                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
                                .withSourceDefinedPrimaryKey(List.of(List.of("id"))))));
    }

    @Override
    protected boolean supportsPerStream() {
        return true;
    }

    private JsonNode getConfigDiscoverWithRevokingSchemaPermissions(final String username, final String password, final List<String> schemas) {
        final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
                .put("method", "Standard")
                .build());
        return Jsons.jsonNode(ImmutableMap.builder()
                .put(JdbcUtils.HOST_KEY, HostPortResolver.resolveHost(db))
                .put(JdbcUtils.PORT_KEY, HostPortResolver.resolvePort(db))
                .put(JdbcUtils.DATABASE_KEY, db.getDatabaseName())
                .put(JdbcUtils.SCHEMAS_KEY, Jsons.jsonNode(schemas))
                .put(JdbcUtils.USERNAME_KEY, username)
                .put(JdbcUtils.PASSWORD_KEY, password)
                .put(JdbcUtils.SSL_KEY, false)
                .put("replication_method", replicationMethod)
                .build());
    }


//    @Test
//    public void testDiscoverWithRevokingSchemaPermissions() throws Exception {
////        prepareEnvForUserWithoutPermissions(database);
////        revokeSchemaPermissions(database);
////        config = getConfigDiscoverWithRevokingSchemaPermissions(LIMIT_PERMISSION_ROLE, LIMIT_PERMISSION_ROLE_PASSWORD, List.of(LIMIT_PERMISSION_SCHEMA));
////        runDiscover();
////        final AirbyteCatalog lastPersistedCatalogSecond = getLastPersistedCatalog();
////        final String assertionMessageWithoutPermission = "Expected no streams after discover for user without schema permissions";
//        assertTrue(true, "");
//    }

    private void prepareEnvForUserWithoutPermissions(final Database database) throws SQLException {
        database.query(ctx -> {
            ctx.fetch(String.format("CREATE ROLE %s WITH LOGIN PASSWORD '%s';", LIMIT_PERMISSION_ROLE, LIMIT_PERMISSION_ROLE_PASSWORD));
            ctx.fetch(String.format("CREATE SCHEMA %s;", LIMIT_PERMISSION_SCHEMA));
            ctx.fetch(String.format("GRANT CONNECT ON DATABASE test TO %s;", LIMIT_PERMISSION_ROLE));
            ctx.fetch(String.format("GRANT USAGE ON schema %s TO %s;", LIMIT_PERMISSION_SCHEMA, LIMIT_PERMISSION_ROLE));
            ctx.fetch(String.format("CREATE TABLE %s.id_and_name(id INTEGER, name VARCHAR(200));", LIMIT_PERMISSION_SCHEMA));
            ctx.fetch(String.format("INSERT INTO %s.id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');", LIMIT_PERMISSION_SCHEMA));
            ctx.fetch(String.format("GRANT SELECT ON table %s.id_and_name TO %s;", LIMIT_PERMISSION_SCHEMA, LIMIT_PERMISSION_ROLE));
            return null;
        });
    }

    private void revokeSchemaPermissions(final Database database) throws SQLException {
        database.query(ctx -> {
            ctx.fetch(String.format("REVOKE USAGE ON schema %s FROM %s;", LIMIT_PERMISSION_SCHEMA, LIMIT_PERMISSION_ROLE));
            return null;
        });
    }
}
