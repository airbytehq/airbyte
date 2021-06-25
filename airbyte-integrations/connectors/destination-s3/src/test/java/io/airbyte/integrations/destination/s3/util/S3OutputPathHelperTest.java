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

package io.airbyte.integrations.destination.s3.util;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.protocol.models.AirbyteStream;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

class S3OutputPathHelperTest {

  @Test
  @DisplayName("getOutputPrefix")
  public void testGetOutputPrefix() {
    // No namespace
    assertEquals("bucket_path/stream_name", S3OutputPathHelper
        .getOutputPrefix("bucket_path", new AirbyteStream().withName("stream_name")));

    // With namespace
    assertEquals("bucket_path/namespace/stream_name", S3OutputPathHelper
        .getOutputPrefix("bucket_path",
            new AirbyteStream().withNamespace("namespace").withName("stream_name")));
  }

}
