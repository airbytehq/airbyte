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

package io.airbyte.integrations.destination.gcs.parquet;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.gcs.GCSFormat;
import io.airbyte.integrations.destination.gcs.GCSFormatConfig;
import org.apache.parquet.hadoop.metadata.CompressionCodecName;

public class GCSParquetFormatConfig implements GCSFormatConfig {

  private final CompressionCodecName compressionCodec;
  private final int blockSize;
  private final int maxPaddingSize;
  private final int pageSize;
  private final int dictionaryPageSize;
  private final boolean dictionaryEncoding;

  public GCSParquetFormatConfig(JsonNode formatConfig) {
    int blockSizeMb = GCSFormatConfig.withDefault(formatConfig, "block_size_mb", GCSParquetConstants.DEFAULT_BLOCK_SIZE_MB);
    int maxPaddingSizeMb = GCSFormatConfig.withDefault(formatConfig, "max_padding_size_mb", GCSParquetConstants.DEFAULT_MAX_PADDING_SIZE_MB);
    int pageSizeKb = GCSFormatConfig.withDefault(formatConfig, "page_size_kb", GCSParquetConstants.DEFAULT_PAGE_SIZE_KB);
    int dictionaryPageSizeKb =
        GCSFormatConfig.withDefault(formatConfig, "dictionary_page_size_kb", GCSParquetConstants.DEFAULT_DICTIONARY_PAGE_SIZE_KB);

    this.compressionCodec = CompressionCodecName
        .valueOf(GCSFormatConfig.withDefault(formatConfig, "compression_codec", GCSParquetConstants.DEFAULT_COMPRESSION_CODEC.name()).toUpperCase());
    this.blockSize = blockSizeMb * 1024 * 1024;
    this.maxPaddingSize = maxPaddingSizeMb * 1024 * 1024;
    this.pageSize = pageSizeKb * 1024;
    this.dictionaryPageSize = dictionaryPageSizeKb * 1024;
    this.dictionaryEncoding = GCSFormatConfig.withDefault(formatConfig, "dictionary_encoding", GCSParquetConstants.DEFAULT_DICTIONARY_ENCODING);
  }

  @Override
  public GCSFormat getFormat() {
    return GCSFormat.PARQUET;
  }

  public CompressionCodecName getCompressionCodec() {
    return compressionCodec;
  }

  public int getBlockSize() {
    return blockSize;
  }

  public int getMaxPaddingSize() {
    return maxPaddingSize;
  }

  public int getPageSize() {
    return pageSize;
  }

  public int getDictionaryPageSize() {
    return dictionaryPageSize;
  }

  public boolean isDictionaryEncoding() {
    return dictionaryEncoding;
  }

  @Override
  public String toString() {
    return "GCSParquetFormatConfig{" +
        "compressionCodec=" + compressionCodec + ", " +
        "blockSize=" + blockSize + ", " +
        "maxPaddingSize=" + maxPaddingSize + ", " +
        "pageSize=" + pageSize + ", " +
        "dictionaryPageSize=" + dictionaryPageSize + ", " +
        "dictionaryEncoding=" + dictionaryEncoding + ", " +
        '}';
  }

}
