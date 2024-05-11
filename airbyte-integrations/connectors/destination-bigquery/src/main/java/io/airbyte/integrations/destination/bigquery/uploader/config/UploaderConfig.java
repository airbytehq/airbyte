/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.uploader.config;

import com.google.cloud.bigquery.BigQuery;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import lombok.Builder;
import lombok.Getter;

@Builder
@Getter
public class UploaderConfig {

  private Integer bigQueryClientChunkSize;
  private String datasetLocation;
  private StreamConfig parsedStream;
  private String targetTableName;
  private BigQuery bigQuery;
  private BigQueryRecordFormatter formatter;

}
