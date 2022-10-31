package io.airbyte.integrations.destination.iceberg.config;

/**
 * @author Leibniz on 2022/10/31.
 */
public enum StorageFormat {
    AVRO("avro"),
    PARQUET("parquet"),
    ORC("orc");

    private final String fileExtension;

    StorageFormat(final String fileExtension) {
        this.fileExtension = fileExtension;
    }

    public String getFileExtension() {
        return fileExtension;
    }
}
