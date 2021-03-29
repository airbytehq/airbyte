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

import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.AnonymousAWSCredentials;
import com.amazonaws.client.builder.AwsClientBuilder.EndpointConfiguration;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import io.findify.s3mock.S3Mock;
import java.io.IOException;
import java.net.ServerSocket;

public class InMemLocalS3 {

  public static int setUpLocalS3AndGetPort() {
    var freeLocalPort = findFreeLocalPort();
    S3Mock api = new S3Mock.Builder().withPort(freeLocalPort).withInMemoryBackend().build();
    api.start();
    return freeLocalPort;
  }

  public static AmazonS3 getLocalS3Client(int port, String region) {
    var endpoint = new EndpointConfiguration("http://localhost:" + port, region);
    return AmazonS3ClientBuilder
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

  private static int findFreeLocalPort() {
    for (int i = 49152; i < 65535; i++) {
      if (isLocalPortFree(i)) {
        // There is a potential race condition here where another thread grabs the port just as it's freed,
        // but before it can be
        // bound to our local S3.
        return i;
      }
    }
    throw new RuntimeException("no available port");
  }

  private static boolean isLocalPortFree(int port) {
    try {
      new ServerSocket(port).close();
      return true;
    } catch (IOException e) {
      return false;
    }
  }

}
