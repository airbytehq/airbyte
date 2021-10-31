package io.airbyte.integrations.destination.redis;

import io.airbyte.protocol.models.DestinationSyncMode;

public class RedisStreamConfig {

    private String namespace;

    private final String keyName;

    private final String tmpKeyName;

    private final DestinationSyncMode destinationSyncMode;

    public RedisStreamConfig(String namespace, String keyName, String tmpKeyName,
                             DestinationSyncMode destinationSyncMode) {
        this.namespace = namespace;
        this.keyName = keyName;
        this.tmpKeyName = tmpKeyName;
        this.destinationSyncMode = destinationSyncMode;
    }

    public RedisStreamConfig(String keyName, String tmpKeyName,
                             DestinationSyncMode destinationSyncMode) {
        this.keyName = keyName;
        this.tmpKeyName = tmpKeyName;
        this.destinationSyncMode = destinationSyncMode;
    }

    public String getNamespace() {
        return namespace;
    }

    public String getKeyName() {
        return keyName;
    }

    public String getTmpKeyName() {
        return tmpKeyName;
    }

    public DestinationSyncMode getDestinationSyncMode() {
        return destinationSyncMode;
    }

    @Override
    public String toString() {
        return "RedisStreamConfig{" +
            "namespace='" + namespace + '\'' +
            ", keyName='" + keyName + '\'' +
            ", tmpKeyName='" + tmpKeyName + '\'' +
            ", destinationSyncMode=" + destinationSyncMode +
            '}';
    }
}
