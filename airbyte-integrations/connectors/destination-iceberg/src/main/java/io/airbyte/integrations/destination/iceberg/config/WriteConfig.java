/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.config;

import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.iceberg.IcebergConstants;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;
import lombok.Data;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.types.StructType;

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
  private final boolean mergeMode;
  private final List<String> mergeKeys;
  private final boolean partitionMode;
  private final List<String> partitionKeys;
  private final boolean datePartitionMode;
  private final String datePartitionSourceColumn;

  // TODO perf: use stageFile to do cache, see
  // io.airbyte.integrations.destination.bigquery.BigQueryWriteConfig.addStagedFile
  private final StructType schema;
  // Store JSON strings instead of Rows to allow Spark to parse them with the
  // schema
  private final List<String> dataCache;

  // Backward-compatible constructor (without merge params)
  public WriteConfig(String namespace, String streamName, boolean isAppendMode, Integer flushBatchSize,
      StructType schema) {
    this(namespace, streamName, isAppendMode, flushBatchSize, schema, false, new ArrayList<>(), false,
        new ArrayList<>(), false, null);
  }

  // Constructor without date partition params (for backward compatibility)
  public WriteConfig(String namespace, String streamName, boolean isAppendMode, Integer flushBatchSize,
      StructType schema, boolean mergeMode, List<String> mergeKeys, boolean partitionMode, List<String> partitionKeys) {
    this(namespace, streamName, isAppendMode, flushBatchSize, schema, mergeMode, mergeKeys, partitionMode,
        partitionKeys, false, null);
  }

  public WriteConfig(String namespace, String streamName, boolean isAppendMode, Integer flushBatchSize,
      StructType schema, boolean mergeMode, List<String> mergeKeys, boolean partitionMode, List<String> partitionKeys,
      boolean datePartitionMode, String datePartitionSourceColumn) {
    this.namespace = namingResolver.convertStreamName(namespace);
    this.tableName = namingResolver.convertStreamName(AIRBYTE_RAW_TABLE_PREFIX + streamName);
    this.tempTableName = namingResolver.convertStreamName(AIRBYTE_TMP_TABLE_PREFIX + streamName);
    final String tableName = genTableName(namespace, AIRBYTE_RAW_TABLE_PREFIX + streamName);
    final String tempTableName = genTableName(namespace, AIRBYTE_TMP_TABLE_PREFIX + streamName);
    this.fullTableName = tableName;
    this.fullTempTableName = tempTableName;
    this.isAppendMode = isAppendMode;
    this.flushBatchSize = flushBatchSize;
    this.mergeMode = mergeMode;
    this.mergeKeys = mergeKeys != null ? new ArrayList<>(mergeKeys) : new ArrayList<>();
    this.partitionMode = partitionMode;
    this.partitionKeys = partitionKeys != null ? new ArrayList<>(partitionKeys) : new ArrayList<>();
    this.datePartitionMode = datePartitionMode;
    this.datePartitionSourceColumn = datePartitionSourceColumn;
    this.schema = schema;
    this.dataCache = new ArrayList<>(flushBatchSize);
  }

  /**
   * Helper method to determine if merge should be performed
   */
  public boolean shouldMerge() {
    return mergeMode && mergeKeys != null && !mergeKeys.isEmpty();
  }

  /**
   * Helper method to determine if partition should be performed
   */
  public boolean shouldPartition() {
    return partitionMode && partitionKeys != null && !partitionKeys.isEmpty();
  }

  /**
   * Helper method to determine if date-based hierarchical partitioning should be performed
   */
  public boolean shouldDatePartition() {
    return datePartitionMode && datePartitionSourceColumn != null && !datePartitionSourceColumn.isEmpty();
  }

  public List<String> fetchDataCache() {
    List<String> copied = new ArrayList<>(this.dataCache);
    this.dataCache.clear();
    return copied;
  }

  public boolean addData(String json) {
    this.dataCache.add(json);
    return this.dataCache.size() >= flushBatchSize;
  }

  private String genTableName(String database, String tmpTableName) {
    return "%s.`%s`.`%s`".formatted(
        IcebergConstants.CATALOG_NAME,
        namingResolver.convertStreamName(database),
        namingResolver.convertStreamName(tmpTableName));
  }

}
