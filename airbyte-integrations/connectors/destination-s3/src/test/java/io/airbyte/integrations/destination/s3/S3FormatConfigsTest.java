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

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig.Flattening;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@DisplayName("S3FormatConfigs")
public class S3FormatConfigsTest {

  private static final ObjectMapper mapper = new ObjectMapper();

  @Test
  @DisplayName("When CSV format is specified, it returns CSV format config")
  public void testGetCsvS3FormatConfig() {
    ObjectNode stubFormatConfig = mapper.createObjectNode();
    stubFormatConfig.put("format_type", S3Format.CSV.toString());
    stubFormatConfig.put("flattening", Flattening.ROOT_LEVEL.getValue());

    ObjectNode stubConfig = mapper.createObjectNode();
    stubConfig.set("format", stubFormatConfig);
    S3FormatConfig formatConfig = S3FormatConfigs.getS3FormatConfig(stubConfig);
    assertEquals(formatConfig.getFormat(), S3Format.CSV);
    assertTrue(formatConfig instanceof S3CsvFormatConfig);
    S3CsvFormatConfig csvFormatConfig = (S3CsvFormatConfig) formatConfig;
    assertEquals(csvFormatConfig.getFlattening(), Flattening.ROOT_LEVEL);
  }

}
