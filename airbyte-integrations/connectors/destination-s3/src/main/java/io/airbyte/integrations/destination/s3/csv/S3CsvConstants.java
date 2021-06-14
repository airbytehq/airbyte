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

package io.airbyte.integrations.destination.s3.csv;

public class S3CsvConstants {

  // These parameters are used by {@link StreamTransferManager}.
  // See this doc about how they affect memory usage:
  // https://alexmojaki.github.io/s3-stream-upload/javadoc/apidocs/alex/mojaki/s3upload/StreamTransferManager.html
  // Total memory = (numUploadThreads + queueCapacity) * partSize + numStreams * (partSize + 6MB)
  // = 31 MB at current configurations
  public static final int DEFAULT_UPLOAD_THREADS = 2;
  public static final int DEFAULT_QUEUE_CAPACITY = 2;
  public static final int DEFAULT_PART_SIZE_MB = 5;
  public static final int DEFAULT_NUM_STREAMS = 1;

}
