package io.airbyte.integrations.destination.cassandra;

import com.datastax.oss.driver.api.core.CqlSession;
import java.net.InetSocketAddress;
import java.util.concurrent.ConcurrentHashMap;

class SessionManager {

    private static final ConcurrentHashMap<CassandraConfig, CqlSession> sessions;

    static {
        sessions = new ConcurrentHashMap<>();
        // register shutdown hook in order to close the sessions/connects to the cassandra cluster
        Runtime.getRuntime().addShutdownHook(new Thread(() -> sessions.forEach((k, v) -> v.close())));
    }

    private SessionManager() {

    }

    /*
     * CqlSession objects are heavyweight and can hold several tcp connections
     * to the Cassandra cluster, for that reason it is better if sessions are reused
     * per configuration. Sessions are thread-safe and can be accessed from different threads.
     *
     * */
    public static CqlSession initSession(CassandraConfig cassandraConfig) {
        var cachedSession = sessions.get(cassandraConfig);
        if (cachedSession != null) {
            return cachedSession;
        } else {
            var session = CqlSession.builder()
                .withLocalDatacenter(cassandraConfig.getDatacenter())
                .addContactPoint(new InetSocketAddress(cassandraConfig.getAddress(), cassandraConfig.getPort()))
                .withAuthCredentials(cassandraConfig.getUsername(), cassandraConfig.getPassword())
                .build();
            sessions.put(cassandraConfig, session);
            return session;
        }
    }

}