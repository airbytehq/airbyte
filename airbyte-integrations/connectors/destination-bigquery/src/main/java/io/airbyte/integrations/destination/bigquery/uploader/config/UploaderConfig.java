/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.uploader.config;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.BigQuery;
import io.airbyte.integrations.destination.bigquery.BigQueryUtils;
import io.airbyte.integrations.destination.bigquery.UploadingMethod;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.uploader.UploaderType;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.Map;
import lombok.Builder;
import lombok.Getter;

@Builder
@Getter
public class UploaderConfig {

  private JsonNode config;
  private ConfiguredAirbyteStream configStream;
  private String targetTableName;
  private String tmpTableName;
  private BigQuery bigQuery;
  private Map<UploaderType, BigQueryRecordFormatter> formatterMap;
  private boolean isDefaultAirbyteTmpSchema;

  public boolean isGcsUploadingMode() {
    return BigQueryUtils.getLoadingMethod(config) == UploadingMethod.GCS;
  }

  public UploaderType getUploaderType() {
    return (isGcsUploadingMode() ? UploaderType.AVRO : UploaderType.STANDARD);
  }

  public BigQueryRecordFormatter getFormatter() {
    return formatterMap.get(getUploaderType());
  }

}
