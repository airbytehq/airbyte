package io.airbyte.integrations.destination.cassandra;

import com.datastax.oss.driver.api.core.CqlSession;
import java.net.InetSocketAddress;

public class CassandraSession {

    private final CassandraConfig cassandraConfig;

    public CassandraSession(CassandraConfig cassandraConfig) {
        this.cassandraConfig = cassandraConfig;
    }

    /*
     * Since CqlSession objects are heavy and maintain TCP connections to multiple nodes
     * consider using a singleton or a pool with CqlSession per keyspace.
     * */
    public CqlSession session() {
        return CqlSession.builder()
            .withLocalDatacenter(cassandraConfig.getDatacenter())
            .addContactPoint(new InetSocketAddress(cassandraConfig.getAddress(), cassandraConfig.getPort()))
            .withAuthCredentials(cassandraConfig.getUsername(), cassandraConfig.getPassword())
            .build();
    }

}