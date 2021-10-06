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

package io.airbyte.integrations.destination.jdbc.copy.s3;

import com.fasterxml.jackson.databind.JsonNode;

public class S3Config {

  private final String endpoint;
  private final String bucketName;
  private final String accessKeyId;
  private final String secretAccessKey;
  private final String region;
  private final Integer partSize;

  public S3Config(String endpoint, String bucketName, String accessKeyId, String secretAccessKey, String region, Integer partSize) {
    this.endpoint = endpoint;
    this.bucketName = bucketName;
    this.accessKeyId = accessKeyId;
    this.secretAccessKey = secretAccessKey;
    this.region = region;
    this.partSize = partSize;
  }

  public String getEndpoint() {
    return endpoint;
  }

  public String getBucketName() {
    return bucketName;
  }

  public String getAccessKeyId() {
    return accessKeyId;
  }

  public String getSecretAccessKey() {
    return secretAccessKey;
  }

  public String getRegion() {
    return region;
  }

  public Integer getPartSize() {
    return partSize;
  }

  public static S3Config getS3Config(JsonNode config) {
    var partSize = S3StreamCopier.DEFAULT_PART_SIZE_MB;
    if (config.get("part_size") != null) {
      partSize = config.get("part_size").asInt();
    }
    return new S3Config(
        config.get("s3_endpoint") == null ? "" : config.get("s3_endpoint").asText(),
        config.get("s3_bucket_name").asText(),
        config.get("access_key_id").asText(),
        config.get("secret_access_key").asText(),
        config.get("s3_bucket_region").asText(),
        partSize);
  }

}
