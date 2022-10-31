package io.airbyte.integrations.destination.iceberg.config;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.CATALOG_NAME;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.HIVE_DATABASE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.HIVE_THRIFT_URI_CONFIG_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.HashMap;
import java.util.Map;
import lombok.AllArgsConstructor;
import lombok.Data;
import org.apache.iceberg.catalog.Catalog;
import org.apache.iceberg.hive.HiveCatalog;

/**
 * @author Leibniz on 2022/10/26.
 */
@Data
@AllArgsConstructor
public class HiveCatalogConfig extends IcebergCatalogConfig {

    private final String thriftUri;
    private final String defaultDatabase;

    public HiveCatalogConfig(JsonNode catalogConfig) {
        this.thriftUri = catalogConfig.get(HIVE_THRIFT_URI_CONFIG_KEY).asText();
        this.defaultDatabase = catalogConfig.get(HIVE_DATABASE_CONFIG_KEY).asText();
    }

    @Override
    public void check() {
        if (!thriftUri.startsWith("thrift://")) {
            throw new IllegalArgumentException(HIVE_THRIFT_URI_CONFIG_KEY + " must start with 'thrift://'");
        }
        //TODO check hive metastore thrift uri is available
    }

    @Override
    public Map<String, String> sparkConfigMap() {
        Map<String, String> configMap = new HashMap<>();
        configMap.put("spark.network.timeout", "300000");
        configMap.put("spark.sql.defaultCatalog", CATALOG_NAME);
        configMap.put("spark.sql.catalog." + CATALOG_NAME, "org.apache.iceberg.spark.SparkCatalog");
        configMap.put("spark.sql.catalog." + CATALOG_NAME + ".type", "hive");
        configMap.put("spark.sql.catalog." + CATALOG_NAME + ".uri", this.thriftUri);
        configMap.put("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions");
        configMap.put("spark.driver.extraJavaOptions", "-Dpackaging.type=jar -Djava.io.tmpdir=/tmp");

        this.storageConfig.appendSparkConfig(configMap, CATALOG_NAME);
        return configMap;
    }

    @Override
    public Catalog genCatalog() {
        HiveCatalog catalog = new HiveCatalog();
        Map<String, String> properties = new HashMap<>();
        properties.put("uri", thriftUri);
        properties.put("warehouse", this.storageConfig.getWarehouseUri());
        this.storageConfig.appendCatalogInitializeProperties(properties);
        catalog.initialize("hive", properties);
        return catalog;
    }
}
