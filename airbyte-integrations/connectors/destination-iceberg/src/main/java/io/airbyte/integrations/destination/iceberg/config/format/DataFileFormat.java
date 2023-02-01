/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.config.format;

import lombok.Getter;

/**
 * @author Leibniz on 2022/10/31.
 */
public enum DataFileFormat {

  AVRO("avro", "Avro"),
  PARQUET("parquet", "Parquet"),
  // ORC("orc"),
  ;

  @Getter
  private final String formatName;
  @Getter
  private final String configValue;

  DataFileFormat(final String formatName, String configValue) {
    this.formatName = formatName;
    this.configValue = configValue;
  }

}
