/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.uploader.config;

import com.google.cloud.bigquery.BigQuery;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.destination.bigquery.BigQueryUtils;
import io.airbyte.integrations.destination.bigquery.UploadingMethod;
import io.airbyte.integrations.destination.bigquery.config.properties.BigQueryConnectorConfiguration;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.uploader.UploaderType;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.Map;
import lombok.Builder;
import lombok.Getter;

@Builder
@Getter
public class UploaderConfig {

  private BigQueryConnectorConfiguration config;
  /**
   * Taken directly from the {@link ConfiguredAirbyteStream}, except if the namespace was null, we set
   * it to the destination default namespace.
   */
  private ConfiguredAirbyteStream configStream;
  /**
   * Parsed directly from {@link #configStream}.
   */
  private StreamConfig parsedStream;
  private String targetTableName;
  private BigQuery bigQuery;
  private Map<UploaderType, BigQueryRecordFormatter> formatterMap;
  private boolean isDefaultAirbyteTmpSchema;
  private BigQueryUtils bigQueryUtils;

  public boolean isGcsUploadingMode() {
    return bigQueryUtils.getLoadingMethod(config) == UploadingMethod.GCS;
  }

  public UploaderType getUploaderType() {
    return (isGcsUploadingMode() ? UploaderType.CSV : UploaderType.STANDARD);
  }

  public BigQueryRecordFormatter getFormatter() {
    return formatterMap.get(getUploaderType());
  }

}
