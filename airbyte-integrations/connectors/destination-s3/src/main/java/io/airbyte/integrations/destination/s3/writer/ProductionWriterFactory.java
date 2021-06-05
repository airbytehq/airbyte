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

package io.airbyte.integrations.destination.s3.writer;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.csv.S3CsvWriter;
import io.airbyte.integrations.destination.s3.parquet.S3ParquetWriter;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.sql.Timestamp;

public class ProductionWriterFactory implements S3WriterFactory {

  @Override
  public S3Writer create(S3DestinationConfig config,
                                  AmazonS3 s3Client,
                                  ConfiguredAirbyteStream configuredStream,
                                  Timestamp uploadTimestamp)
      throws Exception {
    S3Format format = config.getFormatConfig().getFormat();
    if (format == S3Format.CSV) {
      return new S3CsvWriter(config, s3Client, configuredStream, uploadTimestamp);
    }

    if (format == S3Format.PARQUET) {
      return new S3ParquetWriter(config, s3Client, configuredStream, uploadTimestamp);
    }

    throw new RuntimeException("Unexpected S3 destination format: " + format);
  }

}
