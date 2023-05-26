package io.airbyte.integrations.destination.s3_glue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.s3.jsonl.S3JsonlFormatConfig;
import io.airbyte.integrations.destination.s3.util.NumericType;

public class MetastoreJsonlFormatConfig extends S3JsonlFormatConfig implements MetastoreFormatConfig {

  private String serializationLibrary;

  private NumericType numericType;

  private Integer decimalScale;

  public MetastoreJsonlFormatConfig(JsonNode formatConfig) {
      super(formatConfig);
      final JsonNode numericConfig = formatConfig.get(MetastoreConstants.NUMERIC_ARG_NAME);
      this.serializationLibrary = formatConfig.get(MetastoreConstants.SERIALIZATION_LIBRARY) != null ? formatConfig.get(MetastoreConstants.SERIALIZATION_LIBRARY).asText() : "org.openx.data.jsonserde.JsonSerDe";
      this.numericType = numericConfig.get(MetastoreConstants.NUMERIC_TYPE_ARG_NAME) != null ? NumericType.fromValue(numericConfig.get(MetastoreConstants.NUMERIC_TYPE_ARG_NAME).asText()) : NumericType.DOUBLE;
      this.decimalScale = numericConfig.get(MetastoreConstants.DECIMAL_SCALE_ARG_NAME) != null ? numericConfig.get(MetastoreConstants.DECIMAL_SCALE_ARG_NAME).asInt() : 2;
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
  public String getNumericType() {
      if (this.numericType == NumericType.DECIMAL) {
          return String.format("decimal(38,%s)", this.decimalScale);
      } else {
          return this.numericType.toString().toLowerCase();
      }
  }

  @Override
  public NumericType getDecimalScale() { return null; }
}
