package io.airbyte.integrations.destination.iceberg.config;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_CATALOG_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_CATALOG_TYPE_CONFIG_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import java.util.Map;
import javax.annotation.Nonnull;

/**
 * @author Leibniz on 2022/10/26.
 */
public interface IcebergCatalogConfig {

    void check(S3Config destinationConfig);

    Map<String, String> sparkConfigMap(S3Config s3Config);

    static IcebergCatalogConfig fromDestinationConfig(@Nonnull final JsonNode config) {
        final JsonNode catalogConfig = config.get(ICEBERG_CATALOG_CONFIG_KEY);
        String catalogType = catalogConfig.get(ICEBERG_CATALOG_TYPE_CONFIG_KEY).asText().toUpperCase();
        switch (catalogType) {
            case "HIVE":
                return new HiveCatalogConfig(catalogConfig);
            //TODO support other catalog types
            default:
                throw new RuntimeException("Unexpected catalog config: " + Jsons.serialize(config));
        }
    }

}
