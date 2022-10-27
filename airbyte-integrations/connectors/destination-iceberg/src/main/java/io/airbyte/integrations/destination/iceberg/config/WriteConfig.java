package io.airbyte.integrations.destination.iceberg.config;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;
import lombok.Data;
import org.apache.spark.sql.Row;

/**
 * @author Leibniz on 2022/10/26.
 */
@Data
public class WriteConfig implements Serializable {

    public static final int CACHE_SIZE = 1_000;

    private final String tableName;
    private final String tmpTableName;
    private final boolean isAppendMode;
    private final List<Row> dataCache;

    public WriteConfig(String tableName, String tmpTableName, boolean isAppendMode) {
        this.tableName = tableName;
        this.tmpTableName = tmpTableName;
        this.isAppendMode = isAppendMode;
        this.dataCache = new ArrayList<>(CACHE_SIZE);
    }

    public List<Row> fetchDataCache() {
        List<Row> copied = new ArrayList<>(this.dataCache);
        this.dataCache.clear();
        return copied;
    }

    public boolean addData(Row row) {
        this.dataCache.add(row);
        return this.dataCache.size() >= CACHE_SIZE;
    }
}
