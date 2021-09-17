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

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;

public class ConfigTestUtils {

  public static JsonNode getBaseConfig(JsonNode formatConfig) {
    return Jsons.deserialize("{\n"
        + "  \"s3_endpoint\": \"some_test-endpoint\",\n"
        + "  \"s3_bucket_name\": \"test-bucket-name\",\n"
        + "  \"s3_bucket_path\": \"test_path\",\n"
        + "  \"s3_bucket_region\": \"us-east-2\",\n"
        + "  \"access_key_id\": \"some-test-key-id\",\n"
        + "  \"secret_access_key\": \"some-test-access-key\",\n"
        + "  \"format\": " + formatConfig
        + "}");
  }

  public static void assertBaseConfig(S3DestinationConfig s3DestinationConfig) {
    assertEquals("some_test-endpoint", s3DestinationConfig.getEndpoint());
    assertEquals("test-bucket-name", s3DestinationConfig.getBucketName());
    assertEquals("test_path", s3DestinationConfig.getBucketPath());
    assertEquals("us-east-2", s3DestinationConfig.getBucketRegion());
    assertEquals("some-test-key-id", s3DestinationConfig.getAccessKeyId());
    assertEquals("some-test-access-key", s3DestinationConfig.getSecretAccessKey());
  }

}
