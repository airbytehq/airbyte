package io.airbyte.integrations.destination.iceberg.config;

import java.util.Map;

/**
 * @author Leibniz on 2022/10/31.
 */
public interface StorageConfig {

    String getWarehouseUri();

    void appendSparkConfig(Map<String, String> sparkConfig, String catalogName);

    void appendCatalogInitializeProperties(Map<String, String> properties);
}
