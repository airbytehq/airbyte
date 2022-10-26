package io.airbyte.integrations.destination.iceberg.config;

/**
 * @author Leibniz on 2022/10/26.
 */
public class WriteConfig {

    private final String tableName;
    private final String tmpTableName;
    private final boolean isAppendMode;

    public WriteConfig(String tableName, String tmpTableName, boolean isAppendMode) {
        this.tableName = tableName;
        this.tmpTableName = tmpTableName;
        this.isAppendMode = isAppendMode;
    }
}
