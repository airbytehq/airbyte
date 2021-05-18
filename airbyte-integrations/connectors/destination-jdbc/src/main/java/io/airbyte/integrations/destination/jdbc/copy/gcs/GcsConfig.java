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

package io.airbyte.integrations.destination.jdbc.copy.gcs;

import com.fasterxml.jackson.databind.JsonNode;

public class GcsConfig {

  private final String projectId;
  private final String bucketName;
  private final String credentialsJson;

  public GcsConfig(String projectId, String bucketName, String credentialsJson) {
    this.projectId = projectId;
    this.bucketName = bucketName;
    this.credentialsJson = credentialsJson;
  }

  public String getProjectId() {
    return projectId;
  }

  public String getBucketName() {
    return bucketName;
  }

  public String getCredentialsJson() {
    return credentialsJson;
  }

  public static GcsConfig getGcsConfig(JsonNode config) {
    return new GcsConfig(
        config.get("loading_method").get("project_id").asText(),
        config.get("loading_method").get("bucket_name").asText(),
        config.get("loading_method").get("credentials_json").asText());
  }

}
