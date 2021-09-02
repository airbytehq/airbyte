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

package io.airbyte.integrations.destination.dynamodb;

import com.fasterxml.jackson.databind.JsonNode;

public class DynamodbDestinationConfig {

  private final String endpoint;
  private final String tableName;
  private final String accessKeyId;
  private final String secretAccessKey;
  private final String region;

  public DynamodbDestinationConfig(
                                   String endpoint,
                                   String tableName,
                                   String region,
                                   String accessKeyId,
                                   String secretAccessKey) {
    this.endpoint = endpoint;
    this.tableName = tableName;
    this.region = region;
    this.accessKeyId = accessKeyId;
    this.secretAccessKey = secretAccessKey;
  }

  public static DynamodbDestinationConfig getDynamodbDestinationConfig(JsonNode config) {
    return new DynamodbDestinationConfig(
        config.get("dynamodb_endpoint") == null ? "" : config.get("dynamodb_endpoint").asText(),
        config.get("dynamodb_table_name").asText(),
        config.get("dynamodb_region").asText(),
        config.get("access_key_id").asText(),
        config.get("secret_access_key").asText());
  }

  public String getEndpoint() {
    return endpoint;
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

  public String getTableName() {
    return tableName;
  }

}
