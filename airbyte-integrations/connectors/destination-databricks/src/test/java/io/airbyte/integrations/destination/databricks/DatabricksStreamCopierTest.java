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

package io.airbyte.integrations.destination.databricks;

import static org.junit.jupiter.api.Assertions.*;

import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import java.util.UUID;
import org.junit.jupiter.api.Test;

class DatabricksStreamCopierTest {

  @Test
  public void testGetStagingS3DestinationConfig() {
    String bucketPath = UUID.randomUUID().toString();
    S3DestinationConfig config = new S3DestinationConfig("", "", bucketPath, "", "", "", null);
    String stagingFolder = UUID.randomUUID().toString();
    S3DestinationConfig stagingConfig = DatabricksStreamCopier.getStagingS3DestinationConfig(config, stagingFolder);
    assertEquals(String.format("%s/%s", bucketPath, stagingFolder), stagingConfig.getBucketPath());
  }

}
