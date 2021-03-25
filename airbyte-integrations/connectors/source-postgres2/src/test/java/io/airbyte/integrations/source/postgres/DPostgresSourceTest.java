package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import org.apache.commons.lang3.RandomStringUtils;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

import java.sql.SQLException;
import java.util.Properties;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;

import static org.junit.jupiter.api.Assertions.*;

class DPostgresSourceTest {

    @Test
    public void testIt() throws Exception {
        final String slotName = "repl_slot_one";

        final PostgreSQLContainer<?> container = new PostgreSQLContainer<>("postgres:13-alpine")
                .withCopyFileToContainer(MountableFile.forClasspathResource("postgresql.conf"), "/etc/postgresql/postgresql.conf")
                .withCommand("postgres -c config_file=/etc/postgresql/postgresql.conf");

        container.start();

        final JsonNode config = Jsons.jsonNode(ImmutableMap.builder()
                .put("host", container.getHost())
                .put("port", container.getFirstMappedPort())
                .put("database", container.getDatabaseName())
                .put("username", container.getUsername())
                .put("password", container.getPassword())
                .build());

        final Database database = Databases.createDatabase(
                config.get("username").asText(),
                config.get("password").asText(),
                String.format("jdbc:postgresql://%s:%s/%s",
                        config.get("host").asText(),
                        config.get("port").asText(),
                        config.get("database").asText()),
                "org.postgresql.Driver",
                SQLDialect.POSTGRES);

        database.query(ctx -> {
            ctx.execute("SELECT pg_create_logical_replication_slot('" + slotName + "', 'pgoutput');");
            ctx.fetch("CREATE TABLE id_and_name(id INTEGER PRIMARY KEY, name VARCHAR(200));"); // trying without primary key didn't seem to work, which surprised me
            ctx.fetch("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
            ctx.fetch("CREATE TABLE starships(id INTEGER, name VARCHAR(200));");
            ctx.fetch("INSERT INTO starships (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');");
            return null;
        });


        /////////

        final Properties props = new Properties();
        props.setProperty("name", "engine");
        props.setProperty("plugin.name", "pgoutput");
        props.setProperty("connector.class", "io.debezium.connector.postgresql.PostgresConnector");
        props.setProperty("offset.storage", "org.apache.kafka.connect.storage.FileOffsetBackingStore");
        props.setProperty("offset.storage.file.filename", "/tmp/offsets-" + RandomStringUtils.randomAlphabetic(5) + ".dat");
        props.setProperty("offset.flush.interval.ms", "1000"); // todo: make this longer

        // https://debezium.io/documentation/reference/configuration/avro.html
        props.setProperty("key.converter.schemas.enable", "false");
        props.setProperty("value.converter.schemas.enable", "false");

        // https://debezium.io/documentation/reference/configuration/event-flattening.html
        props.setProperty("delete.handling.mode", "rewrite");
        props.setProperty("drop.tombstones", "false");
        props.setProperty("transforms.unwrap.type", "io.debezium.transforms.ExtractNewRecordState");

//        props.setProperty("table.include.list", "public.id_and_name"); // todo
        props.setProperty("database.include.list", container.getDatabaseName());
        props.setProperty("name", "orders-postgres-connector");
        props.setProperty("include_schema_changes", "true");
        props.setProperty("database.server.name", "orders"); // todo
        props.setProperty("database.hostname", "localhost");
        props.setProperty("database.port", String.valueOf(container.getFirstMappedPort()));
        props.setProperty("database.user", container.getUsername());
        props.setProperty("database.password", container.getPassword());
        props.setProperty("database.dbname", container.getDatabaseName());
        props.setProperty("database.history", "io.debezium.relational.history.FileDatabaseHistory"); // todo: any reason not to use in memory version and
        // reload from
        props.setProperty("database.history.file.filename", "/tmp/debezium/dbhistory-" + RandomStringUtils.randomAlphabetic(5) +".dat");

        props.setProperty("slot.name", slotName);

        props.setProperty("snapshot.mode", "exported"); // can use never if we want to manage full refreshes ourselves

        /////////

        BlockingQueue<JsonNode> queue = new LinkedBlockingQueue<>();
        AtomicReference<Throwable> thrownError = new AtomicReference<>();
        AtomicBoolean completed = new AtomicBoolean(false);
        ExecutorService executor = Executors.newSingleThreadExecutor();

        assertTrue(true);

        // Create the engine with this configuration ...
        try(AutoCloseableIterator<JsonNode> iterator = DPostgresSource.getIterator(props, queue, completed, thrownError, executor)) {
            Thread.sleep(5000);

            System.out.println("inserting");
            database.query(ctx -> {
                ctx.fetch("INSERT INTO id_and_name (id, name) VALUES (4,'picard2'),  (5, 'crusher2'), (6, 'vash2');");
                return null;
            });

            Thread.sleep(5000);

            System.out.println("inserting");
            database.query(ctx -> {
                ctx.fetch("INSERT INTO id_and_name (id, name) VALUES (7,'picard3'),  (8, 'crusher3'), (9, 'vash3');");
                return null;
            });

            System.out.println("Starting iteration...");
            while(iterator.hasNext()) {
                System.out.println("iterator.next() = " + iterator.next());
            }
        } catch (Exception e) {
            throw new RuntimeException(e);
        }

        assertTrue(true);


        database.close();

    }

}