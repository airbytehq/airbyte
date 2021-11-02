package io.airbyte.integrations.destination.redis;

import com.fasterxml.jackson.databind.JsonNode;

class RedisConfig {

    private final String host;

    private final int port;

    private final String password;

    public RedisConfig(JsonNode jsonNode) {
        this.host = jsonNode.get("host").asText();
        this.port = jsonNode.get("port").asInt(6379);
        this.password = jsonNode.get("password").asText();
    }

    public RedisConfig(String host, int port, String password) {
        this.host = host;
        this.port = port;
        this.password = password;
    }

    public String getHost() {
        return host;
    }

    public int getPort() {
        return port;
    }

    public String getPassword() {
        return password;
    }
}
