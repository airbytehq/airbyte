package io.airbyte.integrations.source.mongodb;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.ConnectionString;
import com.mongodb.MongoClientSettings;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import io.airbyte.commons.exceptions.ConnectionErrorException;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.mongodb.MongoDatabase;
import io.airbyte.db.mongodb.MongoUtils;
import io.airbyte.integrations.source.relationaldb.CursorInfo;
import org.bson.BsonType;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.net.InetAddress;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

public abstract class AbstractMongoDbSourceTest {

    private JsonNode airbyteSourceConfig;

    private MongoDbSource source;

    @BeforeEach
    void setup() throws Exception {
        source = new MongoDbSource();
        doSetup();

        // Generate the configuration AFTER performing all other setup to ensure that
        // any Docker containers have been created for host/port information.
        airbyteSourceConfig = createConfiguration(Optional.empty(), Optional.empty());
    }

    @AfterEach
    void cleanup() throws Exception {
        source.close();
        doCleanup();
    }

    @Test
    void testToDatabaseConfig() {
        final String authSource = "admin";
        final String password = "password";
        final String username = "username";
        final JsonNode airbyteSourceConfig = createConfiguration(Optional.of(username), Optional.of(password));
        final JsonNode databaseConfig = getSource().toDatabaseConfig(airbyteSourceConfig);

        assertNotNull(databaseConfig);
        assertEquals(String.format(MongoUtils.MONGODB_SERVER_URL,
                String.format("%s:%s@", username, password),
                getHost(), getFirstMappedPort(),
                getDatabaseName(), authSource, false), databaseConfig.get("connectionString").asText());
        assertEquals(getDatabaseName(), databaseConfig.get(JdbcUtils.DATABASE_KEY).asText());
    }

    @Test
    void testGetCheckOperations() throws Exception {
        final MongoDatabase database = getSource().createDatabase(getConfiguration());
        final List<CheckedConsumer<MongoDatabase, Exception>> checkedConsumerList =
                getSource().getCheckOperations(getConfiguration());
        assertNotNull(checkedConsumerList);

        for (CheckedConsumer<MongoDatabase, Exception> mongoDatabaseExceptionCheckedConsumer : checkedConsumerList) {
            assertDoesNotThrow(() -> mongoDatabaseExceptionCheckedConsumer.accept(database));
        }
    }

    @Test
    void testGetCheckOperationsWithFailure() throws Exception {
        final JsonNode airbyteSourceConfig = createConfiguration(Optional.of("username"), Optional.of("password"));

        final MongoDatabase database = getSource().createDatabase(airbyteSourceConfig);
        final List<CheckedConsumer<MongoDatabase, Exception>> checkedConsumerList =
                getSource().getCheckOperations(airbyteSourceConfig);
        assertNotNull(checkedConsumerList);

        for (CheckedConsumer<MongoDatabase, Exception> mongoDatabaseExceptionCheckedConsumer : checkedConsumerList) {
            assertThrows(ConnectionErrorException.class, () -> mongoDatabaseExceptionCheckedConsumer.accept(database));
        }
    }

    @Test
    void testGetExcludedInternalNameSpaces() {
        assertEquals(0, getSource().getExcludedInternalNameSpaces().size());
    }

    @Test
    void testFullRefresh() throws Exception {
        final List<JsonNode> results = new ArrayList<>();
        final MongoDatabase database = getSource().createDatabase(getConfiguration());

        final AutoCloseableIterator<JsonNode> stream = getSource().queryTableFullRefresh(database, List.of(),
                null, getCollectionName(), null, null);
        stream.forEachRemaining(results::add);

        assertNotNull(results);
        assertEquals(getDataSetSize(), results.size());
    }

    @Test
    void testIncrementalRefresh() throws Exception {
        final Integer currentCursorValue = Double.valueOf(getDataSetSize() * .10).intValue();
        final CursorInfo cursor = new CursorInfo(getCursorField(), "0",
                getCursorField(), String.valueOf(currentCursorValue));
        final List<JsonNode> results = new ArrayList<>();
        final MongoDatabase database = getSource().createDatabase(getConfiguration());

        final AutoCloseableIterator<JsonNode> stream =
                getSource().queryTableIncremental(database, List.of(),
                        null, getCollectionName(), cursor, BsonType.INT32);
        stream.forEachRemaining(results::add);

        assertNotNull(results);
        assertEquals(getDataSetSize() - (currentCursorValue + 1), results.size());
    }

    protected abstract void doSetup() throws Exception;

    protected abstract void doCleanup() throws Exception;

    protected abstract String createConnectionString(final String databaseName);

    protected abstract String getCollectionName();

    protected abstract String getDatabaseName();

    protected abstract Integer getDataSetSize();

    protected abstract Integer getFirstMappedPort();

    protected abstract String getHost();

    protected abstract String getCursorField();

    protected abstract String getMongoDbVersion();

    protected abstract void generateDataSet(final MongoClient client);

    protected JsonNode getConfiguration() { return airbyteSourceConfig; }
    protected MongoDbSource getSource() { return source; }

    protected JsonNode createConfiguration(final Optional<String> username, final Optional<String> password) {
        final Map<String, Object> config = new HashMap<>();
        final Map<String, Object> baseConfig = Map.of(
                JdbcUtils.DATABASE_KEY, getDatabaseName(),
                MongoUtils.INSTANCE_TYPE, Map.of(
                        JdbcUtils.HOST_KEY, getHost(),
                        MongoUtils.INSTANCE, MongoUtils.MongoInstanceType.STANDALONE.getType(),
                        JdbcUtils.PORT_KEY, getFirstMappedPort()),
                MongoUtils.AUTH_SOURCE, "admin",
                JdbcUtils.TLS_KEY, "false");

        config.putAll(baseConfig);
        username.ifPresent(u -> config.put(MongoUtils.USER, u));
        password.ifPresent(p -> config.put(JdbcUtils.PASSWORD_KEY, p));
        return Jsons.deserialize(Jsons.serialize(config));
    }

    protected MongoClient createMongoClient(final String databaseName) {
        return MongoClients.create(MongoClientSettings
                .builder()
                .applyConnectionString(new ConnectionString(createConnectionString(databaseName)))
                .inetAddressResolver(host -> List.of(InetAddress.getLocalHost()))
                .build());
    }
}
