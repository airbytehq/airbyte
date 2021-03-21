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

package io.airbyte.integrations.destination.redshift;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.AnonymousAWSCredentials;
import com.amazonaws.client.builder.AwsClientBuilder.EndpointConfiguration;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import io.findify.s3mock.S3Mock;
import java.io.IOException;
import java.net.ServerSocket;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

@DisplayName("Redshift Desintation Efficient Upload")
public class RedshiftDestinationEfficientUploadTest {

  private final static String DEFAULT_REGION = "us-west-2";

  private int s3Port;
  private AmazonS3 client;

  @BeforeEach
  void setUp() {
    s3Port = findFreeLocalPort();
    S3Mock api = new S3Mock.Builder().withPort(s3Port).withInMemoryBackend().build();
    api.start();

    var endpoint = new EndpointConfiguration("http://localhost:" + s3Port, DEFAULT_REGION);
    client = AmazonS3ClientBuilder
        .standard()
        // required to overcome S3 default DNS-based bucket access scheme resulting in attempts to connect
        // to addresses like "bucketname.localhost"
        // which requires specific DNS setup.
        .withPathStyleAccessEnabled(true)
        .withEndpointConfiguration(endpoint)
        // this mock implementation ignores authentication/permissions
        .withCredentials(new AWSStaticCredentialsProvider(new AnonymousAWSCredentials()))
        .build();
  }

  @Test
  void multipartUploadTest() {

  }

  @Nested
  @DisplayName("When creating staging bucket")
  class createStagingBucket {

    @Test
    @DisplayName("Should not create if bucket is already present")
    void doNotCreateIfPresentTest() {
      client.createBucket(RedshiftCopyDestination.DEFAULT_AIRBYTE_STAGING_S3_BUCKET);

      // the s3 client will error out when sending a CreateBucketRequest for an existing bucket; a lack of
      // exception means the test is passing
      RedshiftCopyDestination.createS3StagingBucketIfNeeded(client, DEFAULT_REGION);
    }

    @Test
    @DisplayName("Should create if bucket is not present")
    void createIfNotPresentTest() {
      RedshiftCopyDestination.createS3StagingBucketIfNeeded(client, DEFAULT_REGION);

      assertTrue(client.doesBucketExistV2(RedshiftCopyDestination.DEFAULT_AIRBYTE_STAGING_S3_BUCKET));
    }

  }

  @Test
  @DisplayName("Should correctly extract region from Redshift url")
  void extractRegionFromRedshiftUrlTest() {
    var region = RedshiftCopyDestination.extractRegionFromRedshiftUrl("redshift-cluster-1.c5lzdndklo9c.us-east-2.redshift.amazonaws.com");
    assertEquals("us-east-2", region);
  }

  private int findFreeLocalPort() {
    for (int i = 49152; i < 65535; i++) {
      if (isLocalPortFree(i)) {
        return i;
      }
    }
    throw new RuntimeException("no available port");
  }

  private boolean isLocalPortFree(int port) {
    try {
      new ServerSocket(port).close();
      return true;
    } catch (IOException e) {
      return false;
    }
  }

}
