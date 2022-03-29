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

package io.airbyte.integrations.destination.aws_datalake;

import com.fasterxml.jackson.databind.JsonNode;

public class AwsDatalakeDestinationConfig {

  private final String awsAccountId;
  private final String region;
  private final String authMode;
  private final String accessKeyId;
  private final String secretAccessKey;
  private final String bucketName;
  private final String prefix;
  private final String databaseName;

  public AwsDatalakeDestinationConfig(String awsAccountId,
                                      String region,
                                      String authMode,
                                      String accessKeyId,
                                      String secretAccessKey,
                                      String bucketName,
                                      String prefix,
                                      String databaseName) {
    this.awsAccountId = awsAccountId;
    this.region = region;
    this.authMode = authMode;
    this.accessKeyId = accessKeyId;
    this.secretAccessKey = secretAccessKey;
    this.bucketName = bucketName;
    this.prefix = prefix;
    this.databaseName = databaseName;
  }

  public static AwsDatalakeDestinationConfig getAwsDatalakeDestinationConfig(JsonNode config) {
    var optAuthMode = config.get("AuthMode");
    return new AwsDatalakeDestinationConfig(config.get("AwsAccountId").asText(), config.get("Region").asText(),
        optAuthMode == null ? "" : optAuthMode.asText(), config.get("AccessKeyId").asText(),
        config.get("SecretAccessKey").asText(), config.get("BucketName").asText(), config.get("Prefix").asText(),
        config.get("DatabaseName").asText());
  }

  public String getAwsAccountId() {
    return awsAccountId;
  }

  public String getRegion() {
    return region;
  }

  public String getAuthMode() {
    return authMode;
  }

  public String getAccessKeyId() {
    return accessKeyId;
  }

  public String getSecretAccessKey() {
    return secretAccessKey;
  }

  public String getBucketName() {
    return bucketName;
  }

  public String getPrefix() {
    return prefix;
  }

  public String getDatabaseName() {
    return databaseName;
  }

}
