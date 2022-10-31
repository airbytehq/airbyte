package io.airbyte.integrations.destination.iceberg.config;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.FORMAT_TYPE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.config.IcebergCatalogConfigFactory.getProperty;

import com.fasterxml.jackson.databind.JsonNode;
import lombok.Data;

/**
 * @author Leibniz on 2022/10/31.
 */
@Data
public class FormatConfig {

    private StorageFormat format;

    public static FormatConfig fromJsonNodeConfig(JsonNode formatConfigJson) {
        String formatStr = getProperty(formatConfigJson, FORMAT_TYPE_CONFIG_KEY);
        if (formatStr == null) {
            throw new IllegalArgumentException(FORMAT_TYPE_CONFIG_KEY + " cannot be null");
        }
        return new FormatConfig(formatStr);
    }

    public FormatConfig(String formatStr) {
        this.format = StorageFormat.valueOf(formatStr.toUpperCase());
    }

    //TODO file compression
}
