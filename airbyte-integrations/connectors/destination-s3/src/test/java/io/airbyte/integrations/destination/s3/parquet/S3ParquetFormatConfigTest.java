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

package io.airbyte.integrations.destination.s3.parquet;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import org.apache.parquet.hadoop.metadata.CompressionCodecName;
import org.junit.jupiter.api.Test;

class S3ParquetFormatConfigTest {

  @Test
  public void testConfigConstruction() {
    JsonNode formatConfig = Jsons.deserialize("{\n"
        + "\t\"compression_codec\": \"GZIP\",\n"
        + "\t\"block_size_mb\": 1,\n"
        + "\t\"max_padding_size_mb\": 1,\n"
        + "\t\"page_size_kb\": 1,\n"
        + "\t\"dictionary_page_size_kb\": 1,\n"
        + "\t\"dictionary_encoding\": false\n"
        + "}");

    S3ParquetFormatConfig config = new S3ParquetFormatConfig(formatConfig);

    // The constructor should automatically convert MB or KB to bytes.
    assertEquals(1024 * 1024, config.getBlockSize());
    assertEquals(1024 * 1024, config.getMaxPaddingSize());
    assertEquals(1024, config.getPageSize());
    assertEquals(1024, config.getDictionaryPageSize());

    assertEquals(CompressionCodecName.GZIP, config.getCompressionCodec());
    assertFalse(config.isDictionaryEncoding());
  }

}
