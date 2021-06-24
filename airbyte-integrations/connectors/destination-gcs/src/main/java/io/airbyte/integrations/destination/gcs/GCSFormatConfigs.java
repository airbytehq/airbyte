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

package io.airbyte.integrations.destination.gcs;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.gcs.csv.GCSCsvFormatConfig;
import io.airbyte.integrations.destination.gcs.parquet.GCSParquetFormatConfig;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class GCSFormatConfigs {

  protected static final Logger LOGGER = LoggerFactory.getLogger(GCSFormatConfigs.class);

  public static GCSFormatConfig getGCSFormatConfig(JsonNode config) {
    JsonNode formatConfig = config.get("format");
    LOGGER.info("GCS format config: {}", formatConfig.toString());
    GCSFormat formatType = GCSFormat.valueOf(formatConfig.get("format_type").asText().toUpperCase());

    switch (formatType) {
      case CSV -> {
        return new GCSCsvFormatConfig(formatConfig);
      }
      case PARQUET -> {
        return new GCSParquetFormatConfig(formatConfig);
      }
      default -> {
        throw new RuntimeException("Unexpected output format: " + Jsons.serialize(config));
      }
    }
  }
}
