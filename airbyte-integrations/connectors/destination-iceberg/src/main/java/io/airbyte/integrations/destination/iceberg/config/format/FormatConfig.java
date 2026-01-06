/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.config.format;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.AUTO_COMPACT_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.COMPACT_TARGET_FILE_SIZE_IN_MB_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.FLUSH_BATCH_SIZE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.FORMAT_TYPE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.MERGE_KEYS_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.MERGE_MODE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.PARTITION_KEYS_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.PARTITION_MODE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.AUTO_DATE_PARTITION_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.config.catalog.IcebergCatalogConfigFactory.getProperty;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.ArrayList;
import java.util.List;
import lombok.Data;

/**
 * @author Leibniz on 2022/10/31.
 */
@Data
public class FormatConfig {

  public static final int DEFAULT_FLUSH_BATCH_SIZE = 10000;
  public static final boolean DEFAULT_AUTO_COMPACT = false;
  public static final int DEFAULT_COMPACT_TARGET_FILE_SIZE_IN_MB = 100;
  public static final boolean DEFAULT_MERGE_MODE = false;
  public static final boolean DEFAULT_PARTITION_MODE = false;
  public static final boolean DEFAULT_AUTO_DATE_PARTITION = true;

  private DataFileFormat format;
  private Integer flushBatchSize;
  private boolean autoCompact;
  private Integer compactTargetFileSizeInMb;
  private boolean mergeMode;
  private List<String> mergeKeys;
  private boolean partitionMode;
  private List<String> partitionKeys;
  private boolean autoDatePartition;

  // TODO compression config

  public FormatConfig(JsonNode formatConfigJson) {
    // format
    String formatStr = getProperty(formatConfigJson, FORMAT_TYPE_CONFIG_KEY);
    if (formatStr == null) {
      throw new IllegalArgumentException(FORMAT_TYPE_CONFIG_KEY + " cannot be null");
    }
    this.format = DataFileFormat.valueOf(formatStr.toUpperCase());

    // flushBatchSize
    if (formatConfigJson.has(FLUSH_BATCH_SIZE_CONFIG_KEY)) {
      this.flushBatchSize = formatConfigJson.get(FLUSH_BATCH_SIZE_CONFIG_KEY).asInt(DEFAULT_FLUSH_BATCH_SIZE);
    } else {
      this.flushBatchSize = DEFAULT_FLUSH_BATCH_SIZE;
    }

    // autoCompact
    if (formatConfigJson.has(AUTO_COMPACT_CONFIG_KEY)) {
      this.autoCompact = formatConfigJson.get(AUTO_COMPACT_CONFIG_KEY).asBoolean(DEFAULT_AUTO_COMPACT);
    } else {
      this.autoCompact = DEFAULT_AUTO_COMPACT;
    }

    // compactTargetFileSizeInMb
    if (formatConfigJson.has(COMPACT_TARGET_FILE_SIZE_IN_MB_CONFIG_KEY)) {
      this.compactTargetFileSizeInMb = formatConfigJson.get(COMPACT_TARGET_FILE_SIZE_IN_MB_CONFIG_KEY)
          .asInt(DEFAULT_COMPACT_TARGET_FILE_SIZE_IN_MB);
    } else {
      this.compactTargetFileSizeInMb = DEFAULT_COMPACT_TARGET_FILE_SIZE_IN_MB;
    }

    // mergeMode
    if (formatConfigJson.has(MERGE_MODE_CONFIG_KEY)) {
      this.mergeMode = formatConfigJson.get(MERGE_MODE_CONFIG_KEY).asBoolean(DEFAULT_MERGE_MODE);
    } else {
      this.mergeMode = DEFAULT_MERGE_MODE;
    }

    // mergeKeys
    this.mergeKeys = new ArrayList<>();
    if (formatConfigJson.has(MERGE_KEYS_CONFIG_KEY)) {
      JsonNode mergeKeysNode = formatConfigJson.get(MERGE_KEYS_CONFIG_KEY);
      if (mergeKeysNode.isArray()) {
        for (JsonNode keyNode : mergeKeysNode) {
          this.mergeKeys.add(keyNode.asText());
        }
      }
    }

    // partitionMode
    if (formatConfigJson.has(PARTITION_MODE_CONFIG_KEY)) {
      this.partitionMode = formatConfigJson.get(PARTITION_MODE_CONFIG_KEY).asBoolean(DEFAULT_PARTITION_MODE);
    } else {
      this.partitionMode = DEFAULT_PARTITION_MODE;
    }

    // partitionKeys
    this.partitionKeys = new ArrayList<>();
    if (formatConfigJson.has(PARTITION_KEYS_CONFIG_KEY)) {
      JsonNode partitionKeysNode = formatConfigJson.get(PARTITION_KEYS_CONFIG_KEY);
      if (partitionKeysNode.isArray()) {
        for (JsonNode keyNode : partitionKeysNode) {
          this.partitionKeys.add(keyNode.asText());
        }
      }
    }

    // autoDatePartition - automatically enable date partitioning using cursor field for incremental syncs
    if (formatConfigJson.has(AUTO_DATE_PARTITION_CONFIG_KEY)) {
      this.autoDatePartition = formatConfigJson.get(AUTO_DATE_PARTITION_CONFIG_KEY).asBoolean(DEFAULT_AUTO_DATE_PARTITION);
    } else {
      this.autoDatePartition = DEFAULT_AUTO_DATE_PARTITION;
    }
  }

}
