package io.airbyte.integrations.source.mongodb.internal;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.ReadPreference;
import com.mongodb.ServerAddress;
import com.mongodb.client.MongoClient;
import com.mongodb.client.internal.MongoClientImpl;
import io.airbyte.commons.json.Jsons;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Map;

import static io.airbyte.integrations.source.mongodb.internal.MongoConnectionUtils.DRIVER_NAME;
import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.AUTH_SOURCE_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.CONNECTION_STRING_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.PASSWORD_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.REPLICA_SET_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.USER_CONFIGURATION_KEY;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;

class MongoConnectionUtilsTest {

    @Test
    void testCreateMongoClient() {
        final String authSource = "admin";
        final String host = "host";
        final int port = 1234;
        final String username = "user";
        final String password = "password";
        final String replicaSet = "replica-set";
        final JsonNode config = Jsons.jsonNode(Map.of(
                CONNECTION_STRING_CONFIGURATION_KEY, "mongodb://" + host + ":" + port + "/",
                USER_CONFIGURATION_KEY, username,
                PASSWORD_CONFIGURATION_KEY, password,
                REPLICA_SET_CONFIGURATION_KEY, replicaSet,
                AUTH_SOURCE_CONFIGURATION_KEY, authSource
        ));

        final MongoClient mongoClient = MongoConnectionUtils.createMongoClient(config);

        assertNotNull(mongoClient);
        assertEquals(List.of(new ServerAddress(host, port)), ((MongoClientImpl)mongoClient).getSettings().getClusterSettings().getHosts());
        assertEquals(replicaSet, ((MongoClientImpl)mongoClient).getSettings().getClusterSettings().getRequiredReplicaSetName());
        assertEquals(ReadPreference.secondaryPreferred(), ((MongoClientImpl)mongoClient).getSettings().getReadPreference());
        assertEquals(false, ((MongoClientImpl)mongoClient).getSettings().getRetryWrites());
        assertEquals(true,((MongoClientImpl)mongoClient).getSettings().getSslSettings().isEnabled());
        assertEquals(List.of("sync", DRIVER_NAME), ((MongoClientImpl)mongoClient).getMongoDriverInformation().getDriverNames());
        assertEquals(username, ((MongoClientImpl)mongoClient).getSettings().getCredential().getUserName());
        assertEquals(password, new String(((MongoClientImpl)mongoClient).getSettings().getCredential().getPassword()));
        assertEquals(authSource, ((MongoClientImpl)mongoClient).getSettings().getCredential().getSource());
    }

    @Test
    void testCreateMongoClientWithoutCredentials() {
        final String host = "host";
        final int port = 1234;
        final String replicaSet = "replica-set";
        final JsonNode config = Jsons.jsonNode(Map.of(
                CONNECTION_STRING_CONFIGURATION_KEY, "mongodb://" + host + ":" + port + "/",
                REPLICA_SET_CONFIGURATION_KEY, replicaSet
        ));

        final MongoClient mongoClient = MongoConnectionUtils.createMongoClient(config);

        assertNotNull(mongoClient);
        assertEquals(List.of(new ServerAddress(host, port)), ((MongoClientImpl)mongoClient).getSettings().getClusterSettings().getHosts());
        assertEquals(replicaSet, ((MongoClientImpl)mongoClient).getSettings().getClusterSettings().getRequiredReplicaSetName());
        assertEquals(ReadPreference.secondaryPreferred(), ((MongoClientImpl)mongoClient).getSettings().getReadPreference());
        assertEquals(false, ((MongoClientImpl)mongoClient).getSettings().getRetryWrites());
        assertEquals(true,((MongoClientImpl)mongoClient).getSettings().getSslSettings().isEnabled());
        assertEquals(List.of("sync", DRIVER_NAME), ((MongoClientImpl)mongoClient).getMongoDriverInformation().getDriverNames());
        assertNull(((MongoClientImpl)mongoClient).getSettings().getCredential());
    }

}
