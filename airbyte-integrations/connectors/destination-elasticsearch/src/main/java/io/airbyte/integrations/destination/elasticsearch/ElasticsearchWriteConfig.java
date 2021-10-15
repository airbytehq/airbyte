package io.airbyte.integrations.destination.elasticsearch;


import io.airbyte.protocol.models.DestinationSyncMode;

public class ElasticsearchWriteConfig {

    private String namespace;
    private DestinationSyncMode syncMode;

    public String getNamespace() {
        return namespace;
    }

    public ElasticsearchWriteConfig setNamespace(String namespace) {
        this.namespace = namespace;
        return this;
    }

    public DestinationSyncMode getSyncMode() {
        return syncMode;
    }

    public ElasticsearchWriteConfig setSyncMode(DestinationSyncMode syncMode) {
        this.syncMode = syncMode;
        return this;
    }
}
