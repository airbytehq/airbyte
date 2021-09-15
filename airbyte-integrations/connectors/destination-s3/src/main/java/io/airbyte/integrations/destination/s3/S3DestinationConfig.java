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

package io.airbyte.integrations.destination.s3;

import com.amazonaws.ClientConfiguration;
import com.amazonaws.auth.AWSCredentials;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3Config;

/**
 * This class is similar to {@link io.airbyte.integrations.destination.jdbc.copy.s3.S3Config}. It
 * has an extra {@code bucketPath} parameter, which is necessary for more delicate data syncing to
 * S3.
 */
public class S3DestinationConfig {

  private final String endpoint;
  private final String bucketName;
  private final String bucketPath;
  private final String bucketRegion;
  private final String accessKeyId;
  private final String secretAccessKey;
  private final S3FormatConfig formatConfig;

  public S3DestinationConfig(
                             String endpoint,
                             String bucketName,
                             String bucketPath,
                             String bucketRegion,
                             String accessKeyId,
                             String secretAccessKey,
                             S3FormatConfig formatConfig) {
    this.endpoint = endpoint;
    this.bucketName = bucketName;
    this.bucketPath = bucketPath;
    this.bucketRegion = bucketRegion;
    this.accessKeyId = accessKeyId;
    this.secretAccessKey = secretAccessKey;
    this.formatConfig = formatConfig;
  }

  public static S3DestinationConfig getS3DestinationConfig(JsonNode config) {
    return new S3DestinationConfig(
        config.get("s3_endpoint") == null ? "" : config.get("s3_endpoint").asText(),
        config.get("s3_bucket_name").asText(),
        config.get("s3_bucket_path").asText(),
        config.get("s3_bucket_region").asText(),
        config.get("access_key_id").asText(),
        config.get("secret_access_key").asText(),
        S3FormatConfigs.getS3FormatConfig(config));
  }

  public String getEndpoint() {
    return endpoint;
  }

  public String getBucketName() {
    return bucketName;
  }

  public String getBucketPath() {
    return bucketPath;
  }

  public String getBucketRegion() {
    return bucketRegion;
  }

  public String getAccessKeyId() {
    return accessKeyId;
  }

  public String getSecretAccessKey() {
    return secretAccessKey;
  }

  public S3FormatConfig getFormatConfig() {
    return formatConfig;
  }

  public AmazonS3 getS3Client() {
    final AWSCredentials awsCreds = new BasicAWSCredentials(accessKeyId, secretAccessKey);

    if (endpoint == null || endpoint.isEmpty()) {
      return AmazonS3ClientBuilder.standard()
          .withCredentials(new AWSStaticCredentialsProvider(awsCreds))
          .withRegion(bucketRegion)
          .build();
    }

    ClientConfiguration clientConfiguration = new ClientConfiguration();
    clientConfiguration.setSignerOverride("AWSS3V4SignerType");

    return AmazonS3ClientBuilder
        .standard()
        .withEndpointConfiguration(new AwsClientBuilder.EndpointConfiguration(endpoint, bucketRegion))
        .withPathStyleAccessEnabled(true)
        .withClientConfiguration(clientConfiguration)
        .withCredentials(new AWSStaticCredentialsProvider(awsCreds))
        .build();
  }

  /**
   * @return {@link S3Config} for convenience. The part size should not matter in any use case that
   *         gets an {@link S3Config} from this class. So the default 10 MB is used.
   */
  public S3Config getS3Config() {
    return new S3Config(endpoint, bucketName, accessKeyId, secretAccessKey, bucketRegion, 10);
  }

}
