package io.airbyte.integrations.destination.iceberg.config;

import io.airbyte.integrations.destination.iceberg.IcebergConstants;
import java.util.Map;
import lombok.Data;
import org.apache.iceberg.catalog.Catalog;

/**
 * @author Leibniz on 2022/10/26.
 */
@Data
public abstract class IcebergCatalogConfig {

    protected StorageConfig storageConfig;
    protected FormatConfig formatConfig;

    public abstract void check() throws Exception;

    public abstract Map<String, String> sparkConfigMap();

    public abstract Catalog genCatalog();

    public String getDefaultDatabase() {
        return IcebergConstants.DEFAULT_DATABASE;
    }

}
