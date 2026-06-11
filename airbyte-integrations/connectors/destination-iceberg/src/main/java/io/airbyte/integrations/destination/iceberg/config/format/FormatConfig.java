/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.config.format;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.AUTO_COMPACT_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.COMPACT_TARGET_FILE_SIZE_IN_MB_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.FLUSH_BATCH_SIZE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.FORMAT_TYPE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.PARTITION_AWARE_MERGE_STREAMS_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.PARTITION_KEYS_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.PARTITION_MODE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.AUTO_DATE_PARTITION_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.config.catalog.IcebergCatalogConfigFactory.getProperty;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import lombok.Data;

/**
 * @author Leibniz on 2022/10/31.
 */
@Data
public class FormatConfig {

  public static final int DEFAULT_FLUSH_BATCH_SIZE = 10000;
  public static final boolean DEFAULT_AUTO_COMPACT = false;
  public static final int DEFAULT_COMPACT_TARGET_FILE_SIZE_IN_MB = 100;
  public static final boolean DEFAULT_PARTITION_MODE = false;
  public static final boolean DEFAULT_AUTO_DATE_PARTITION = true;

  private DataFileFormat format;
  private Integer flushBatchSize;
  private boolean autoCompact;
  private Integer compactTargetFileSizeInMb;
  // Lowercased stream names that opted into partition-aware merge (identity partition keys added to
  // the merge ON clause). Opt-in per table; defaults to off.
  private Set<String> partitionAwareMergeStreams;
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

    // partitionAwareMergeStreams: per-table opt-in (list of stream/table names) to add identity
    // partition keys into the merge ON clause for partition pruning. Stored lowercased to match the
    // stream-name normalization used when writing.
    this.partitionAwareMergeStreams = new HashSet<>();
    if (formatConfigJson.has(PARTITION_AWARE_MERGE_STREAMS_CONFIG_KEY)) {
      JsonNode node = formatConfigJson.get(PARTITION_AWARE_MERGE_STREAMS_CONFIG_KEY);
      if (node.isArray()) {
        for (JsonNode streamNode : node) {
          String streamName = streamNode.asText();
          if (streamName != null && !streamName.isBlank()) {
            this.partitionAwareMergeStreams.add(streamName.toLowerCase());
          }
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
