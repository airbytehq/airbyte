/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.config.format;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.AUTO_COMPACT_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.COMPACT_TARGET_FILE_SIZE_IN_MB_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.FLUSH_BATCH_SIZE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.FORMAT_TYPE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.config.catalog.IcebergCatalogConfigFactory.getProperty;

import com.fasterxml.jackson.databind.JsonNode;
import lombok.Data;

/**
 * @author Leibniz on 2022/10/31.
 */
@Data
public class FormatConfig {

  public static final int DEFAULT_FLUSH_BATCH_SIZE = 10000;
  public static final boolean DEFAULT_AUTO_COMPACT = false;
  public static final int DEFAULT_COMPACT_TARGET_FILE_SIZE_IN_MB = 100;

  private DataFileFormat format;
  private Integer flushBatchSize;
  private boolean autoCompact;
  private Integer compactTargetFileSizeInMb;

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
  }

}
