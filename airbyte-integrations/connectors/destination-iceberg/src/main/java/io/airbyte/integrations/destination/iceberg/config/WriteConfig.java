/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.config;

import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.iceberg.IcebergConstants;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;
import lombok.Data;
import org.apache.spark.sql.Row;

/**
 * Write config for each stream
 *
 * @author Leibniz on 2022/10/26.
 */
@Data
public class WriteConfig implements Serializable {

  private static final NamingConventionTransformer namingResolver = new StandardNameTransformer();
  private static final String AIRBYTE_RAW_TABLE_PREFIX = "airbyte_raw_";
  private static final String AIRBYTE_TMP_TABLE_PREFIX = "_airbyte_tmp_";

  private final String namespace;
  private final String tableName;
  private final String tempTableName;
  private final String fullTableName;
  private final String fullTempTableName;
  private final boolean isAppendMode;
  private final Integer flushBatchSize;

  // TODO perf: use stageFile to do cache, see
  // io.airbyte.integrations.destination.bigquery.BigQueryWriteConfig.addStagedFile
  private final List<Row> dataCache;

  public WriteConfig(String namespace, String streamName, boolean isAppendMode, Integer flushBatchSize) {
    this.namespace = namingResolver.convertStreamName(namespace);
    this.tableName = namingResolver.convertStreamName(AIRBYTE_RAW_TABLE_PREFIX + streamName);
    this.tempTableName = namingResolver.convertStreamName(AIRBYTE_TMP_TABLE_PREFIX + streamName);
    final String tableName = genTableName(namespace, AIRBYTE_RAW_TABLE_PREFIX + streamName);
    final String tempTableName = genTableName(namespace, AIRBYTE_TMP_TABLE_PREFIX + streamName);
    this.fullTableName = tableName;
    this.fullTempTableName = tempTableName;
    this.isAppendMode = isAppendMode;
    this.flushBatchSize = flushBatchSize;
    this.dataCache = new ArrayList<>(flushBatchSize);
  }

  public List<Row> fetchDataCache() {
    List<Row> copied = new ArrayList<>(this.dataCache);
    this.dataCache.clear();
    return copied;
  }

  public boolean addData(Row row) {
    this.dataCache.add(row);
    return this.dataCache.size() >= flushBatchSize;
  }

  private String genTableName(String database, String tmpTableName) {
    return "%s.`%s`.`%s`".formatted(
        IcebergConstants.CATALOG_NAME,
        namingResolver.convertStreamName(database),
        namingResolver.convertStreamName(tmpTableName));
  }

}
