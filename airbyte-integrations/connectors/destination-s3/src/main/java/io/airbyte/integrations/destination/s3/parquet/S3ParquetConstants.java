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

import org.apache.parquet.hadoop.metadata.CompressionCodecName;

public class S3ParquetConstants {

  // Parquet writer
  public static final CompressionCodecName DEFAULT_COMPRESSION_CODEC = CompressionCodecName.UNCOMPRESSED;
  public static final int DEFAULT_BLOCK_SIZE_MB = 128;
  public static final int DEFAULT_MAX_PADDING_SIZE_MB = 8;
  public static final int DEFAULT_PAGE_SIZE_KB = 1024;
  public static final int DEFAULT_DICTIONARY_PAGE_SIZE_KB = 1024;
  public static final boolean DEFAULT_DICTIONARY_ENCODING = true;

}
