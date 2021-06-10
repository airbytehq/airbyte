/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.s3;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig.Flattening;
import io.airbyte.integrations.destination.s3.parquet.S3ParquetConstants;
import io.airbyte.integrations.destination.s3.parquet.S3ParquetFormatConfig;
import org.apache.parquet.hadoop.metadata.CompressionCodecName;

public class S3FormatConfigs {

  public static S3FormatConfig getS3FormatConfig(JsonNode config) {
    JsonNode formatConfig = config.get("format");
    S3Format formatType = S3Format.valueOf(formatConfig.get("format_type").asText().toUpperCase());

    if (formatType == S3Format.CSV) {
      Flattening flattening = Flattening.fromValue(formatConfig.get("flattening").asText());
      return new S3CsvFormatConfig(flattening);
    }

    if (formatType == S3Format.PARQUET) {
      CompressionCodecName compressionCodec = CompressionCodecName.valueOf(withDefault(formatConfig, "compression_codec", S3ParquetConstants.DEFAULT_COMPRESSION_CODEC.name()).toUpperCase());
      int blockSize = withDefault(formatConfig, "block_size_mb", S3ParquetConstants.DEFAULT_BLOCK_SIZE_MB);
      int maxPaddingSize = withDefault(formatConfig, "max_padding_size_mb", S3ParquetConstants.DEFAULT_MAX_PADDING_SIZE_MB);
      int pageSize = withDefault(formatConfig, "page_size_kb", S3ParquetConstants.DEFAULT_PAGE_SIZE_KB);
      int dictionaryPageSize = withDefault(formatConfig, "dictionary_page_size_kb", S3ParquetConstants.DEFAULT_DICTIONARY_PAGE_SIZE_KB);
      boolean dictionaryEncoding = withDefault(formatConfig, "dictionary_encoding", S3ParquetConstants.DEFAULT_DICTIONARY_ENCODING);
      return new S3ParquetFormatConfig(compressionCodec, blockSize, maxPaddingSize, pageSize, dictionaryPageSize, dictionaryEncoding);
    }

    throw new RuntimeException("Unexpected output format: " + Jsons.serialize(config));
  }

  private static String withDefault(JsonNode config, String property, String defaultValue) {
    JsonNode value = config.get(property);
    if (value == null || value.isNull()) {
      return defaultValue;
    }
    return value.asText();
  }

  private static int withDefault(JsonNode config, String property, int defaultValue) {
    JsonNode value = config.get(property);
    if (value == null || value.isNull()) {
      return defaultValue;
    }
    return value.asInt();
  }

  private static boolean withDefault(JsonNode config, String property, boolean defaultValue) {
    JsonNode value = config.get(property);
    if (value == null || value.isNull()) {
      return defaultValue;
    }
    return value.asBoolean();
  }

}
