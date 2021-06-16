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

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.S3FormatConfig;
import org.apache.parquet.hadoop.metadata.CompressionCodecName;

public class S3ParquetFormatConfig implements S3FormatConfig {

  private final CompressionCodecName compressionCodec;
  private final int blockSize;
  private final int maxPaddingSize;
  private final int pageSize;
  private final int dictionaryPageSize;
  private final boolean dictionaryEncoding;

  public S3ParquetFormatConfig(JsonNode formatConfig) {
    int blockSizeMb = S3FormatConfig.withDefault(formatConfig, "block_size_mb", S3ParquetConstants.DEFAULT_BLOCK_SIZE_MB);
    int maxPaddingSizeMb = S3FormatConfig.withDefault(formatConfig, "max_padding_size_mb", S3ParquetConstants.DEFAULT_MAX_PADDING_SIZE_MB);
    int pageSizeKb = S3FormatConfig.withDefault(formatConfig, "page_size_kb", S3ParquetConstants.DEFAULT_PAGE_SIZE_KB);
    int dictionaryPageSizeKb =
        S3FormatConfig.withDefault(formatConfig, "dictionary_page_size_kb", S3ParquetConstants.DEFAULT_DICTIONARY_PAGE_SIZE_KB);

    this.compressionCodec = CompressionCodecName
        .valueOf(S3FormatConfig.withDefault(formatConfig, "compression_codec", S3ParquetConstants.DEFAULT_COMPRESSION_CODEC.name()).toUpperCase());
    this.blockSize = blockSizeMb * 1024 * 1024;
    this.maxPaddingSize = maxPaddingSizeMb * 1024 * 1024;
    this.pageSize = pageSizeKb * 1024;
    this.dictionaryPageSize = dictionaryPageSizeKb * 1024;
    this.dictionaryEncoding = S3FormatConfig.withDefault(formatConfig, "dictionary_encoding", S3ParquetConstants.DEFAULT_DICTIONARY_ENCODING);
  }

  @Override
  public S3Format getFormat() {
    return S3Format.PARQUET;
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
    return "S3ParquetFormatConfig{" +
        "compressionCodec=" + compressionCodec + ", " +
        "blockSize=" + blockSize + ", " +
        "maxPaddingSize=" + maxPaddingSize + ", " +
        "pageSize=" + pageSize + ", " +
        "dictionaryPageSize=" + dictionaryPageSize + ", " +
        "dictionaryEncoding=" + dictionaryEncoding + ", " +
        '}';
  }

}
