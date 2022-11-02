package io.airbyte.integrations.destination.iceberg.config.format;

import lombok.Getter;

/**
 * @author Leibniz on 2022/10/31.
 */
public enum DataFileFormat {
    AVRO("avro"),
    PARQUET("parquet"),
    ORC("orc");

    @Getter
    private final String formatName;

    DataFileFormat(final String formatName) {
        this.formatName = formatName;
    }
}
