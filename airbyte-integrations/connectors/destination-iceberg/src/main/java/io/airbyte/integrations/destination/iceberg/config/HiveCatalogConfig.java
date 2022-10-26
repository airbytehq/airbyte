package io.airbyte.integrations.destination.iceberg.config;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.HIVE_THRIFT_URI_CONFIG_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.Map;

/**
 * @author Leibniz on 2022/10/26.
 */
public class HiveCatalogConfig implements IcebergCatalogConfig {

    private final String thriftUri;

    public HiveCatalogConfig(JsonNode catalogConfig) {
        this.thriftUri = catalogConfig.get(HIVE_THRIFT_URI_CONFIG_KEY).asText();
    }

    public HiveCatalogConfig(String thriftUri) {
        this.thriftUri = thriftUri;
    }


    @Override
    public Map<String, Object> sparkConfigMap(S3Config s3Config) {
        return null;
    }
}
