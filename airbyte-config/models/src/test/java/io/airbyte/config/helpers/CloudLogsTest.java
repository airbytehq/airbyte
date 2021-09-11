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

package io.airbyte.config.helpers;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

public class CloudLogsTest {

  @Test
  public void createCloudLogClientTestMinio() {
    var configs = Mockito.mock(LogConfigs.class);
    Mockito.when(configs.getS3MinioEndpoint()).thenReturn("minio-endpoint");
    Mockito.when(configs.getAwsAccessKey()).thenReturn("access-key");
    Mockito.when(configs.getAwsSecretAccessKey()).thenReturn("access-key-secret");
    Mockito.when(configs.getS3LogBucket()).thenReturn("test-bucket");
    Mockito.when(configs.getS3LogBucketRegion()).thenReturn("");

    assertEquals(S3Logs.class, CloudLogs.createCloudLogClient(configs).getClass());
  }

  @Test
  public void createCloudLogClientTestAws() {
    var configs = Mockito.mock(LogConfigs.class);
    Mockito.when(configs.getS3MinioEndpoint()).thenReturn("");
    Mockito.when(configs.getAwsAccessKey()).thenReturn("access-key");
    Mockito.when(configs.getAwsSecretAccessKey()).thenReturn("access-key-secret");
    Mockito.when(configs.getS3LogBucket()).thenReturn("test-bucket");
    Mockito.when(configs.getS3LogBucketRegion()).thenReturn("us-east-1");

    assertEquals(S3Logs.class, CloudLogs.createCloudLogClient(configs).getClass());
  }

  @Test
  public void createCloudLogClientTestGcs() {
    var configs = Mockito.mock(LogConfigs.class);
    Mockito.when(configs.getAwsAccessKey()).thenReturn("");
    Mockito.when(configs.getAwsSecretAccessKey()).thenReturn("");
    Mockito.when(configs.getS3LogBucket()).thenReturn("");
    Mockito.when(configs.getS3LogBucketRegion()).thenReturn("");

    Mockito.when(configs.getGcpStorageBucket()).thenReturn("storage-bucket");
    Mockito.when(configs.getGoogleApplicationCredentials()).thenReturn("path/to/google/secret");

    assertEquals(GcsLogs.class, CloudLogs.createCloudLogClient(configs).getClass());
  }

}
