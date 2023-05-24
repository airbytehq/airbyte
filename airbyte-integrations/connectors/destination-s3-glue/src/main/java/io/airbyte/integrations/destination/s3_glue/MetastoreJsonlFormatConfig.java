package io.airbyte.integrations.destination.s3_glue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.s3.jsonl.S3JsonlFormatConfig;
import io.airbyte.integrations.destination.s3.util.NumericType;

public class MetastoreJsonlFormatConfig extends S3JsonlFormatConfig implements MetastoreFormatConfig {

  private String serializationLibrary;

  public MetastoreJsonlFormatConfig(JsonNode formatConfig) {
      super(formatConfig);
      this.serializationLibrary = formatConfig.get(MetastoreConstants.SERIALIZATION_LIBRARY) != null ? formatConfig.get(MetastoreConstants.SERIALIZATION_LIBRARY).asText() : "org.openx.data.jsonserde.JsonSerDe";
  }

  @Override
  public String getInputFormat() {
      return MetastoreConstants.TEXT_INPUT_FORMAT;
  }

  @Override
  public String getOutputFormat() {
      return MetastoreConstants.TEXT_OUTPUT_FORMAT;
  }

  @Override
  public String getSerializationLibrary() {
      return serializationLibrary;
  }

  @Override
  public NumericType getNumericType() { return null; }

  @Override
  public NumericType getDecimalScale() { return null; }
}
