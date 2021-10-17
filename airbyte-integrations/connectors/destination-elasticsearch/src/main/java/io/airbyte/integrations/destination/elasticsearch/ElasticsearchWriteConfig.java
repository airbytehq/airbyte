package io.airbyte.integrations.destination.elasticsearch;


import io.airbyte.protocol.models.DestinationSyncMode;

import java.util.List;
import java.util.Objects;

public class ElasticsearchWriteConfig {

    private String namespace;
    private DestinationSyncMode syncMode;
    private List<List<String>> primaryKey;

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

    public List<List<String>> getPrimaryKey() {
        return this.primaryKey;
    }
    public ElasticsearchWriteConfig setPrimaryKey(List<List<String>> primaryKey) {
        this.primaryKey = primaryKey;
        return this;
    }

    public boolean hasPrimaryKey() {
        return Objects.nonNull(this.primaryKey) && this.primaryKey.size() > 0;
    }
}
