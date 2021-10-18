package io.airbyte.integrations.destination.cassandra;

import com.fasterxml.jackson.databind.JsonNode;

/*
 * Immutable configuration class for storing cassandra related config.
 * */
public class CassandraConfig {

    private final String keyspace;

    private final String username;

    private final String password;

    private final String address;

    private final int port;

    private final String datacenter;

    private int replicationFactor = 2;

    private boolean namespacesEnabled = true;

    public CassandraConfig(String keyspace, String username, String password, String address, int port,
                           String datacenter, int replicationFactor, boolean namespacesEnabled) {
        this.keyspace = keyspace;
        this.username = username;
        this.password = password;
        this.address = address;
        this.port = port;
        this.datacenter = datacenter;
        this.replicationFactor = replicationFactor;
        this.namespacesEnabled = namespacesEnabled;
    }

    public CassandraConfig(JsonNode config) {
        this.keyspace = config.get("keyspace").asText();
        this.username = config.get("username").asText();
        this.password = config.get("password").asText();
        this.address = config.get("address").asText();
        this.port = config.get("port").asInt();
        this.datacenter = config.get("datacenter").asText();
    }

    public String getKeyspace() {
        return keyspace;
    }

    public String getUsername() {
        return username;
    }

    public String getPassword() {
        return password;
    }

    public String getAddress() {
        return address;
    }

    public int getPort() {
        return port;
    }

    public String getDatacenter() {
        return datacenter;
    }

    public int getReplicationFactor() {
        return replicationFactor;
    }

    public boolean isNamespacesEnabled() {
        return namespacesEnabled;
    }

    @Override
    public String toString() {
        return "CassandraConfig{" +
            "keyspace='" + keyspace + '\'' +
            ", username='" + username + '\'' +
            ", password='" + password + '\'' +
            ", address='" + address + '\'' +
            ", port=" + port +
            ", datacenter='" + datacenter + '\'' +
            ", replicationFactor=" + replicationFactor +
            ", namespacesEnabled=" + namespacesEnabled +
            '}';
    }
}
