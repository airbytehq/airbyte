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

package io.airbyte.integrations.destination.gcs.util;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;

public class ConfigTestUtils {

  public static JsonNode getBaseConfig(JsonNode formatConfig) {
    return Jsons.deserialize("{\n"
        + "  \"gcs_bucket_name\": \"test-bucket-name\",\n"
        + "  \"gcs_bucket_path\": \"test_path\",\n"
        + "  \"gcs_bucket_region\": \"us-east-2\","
        + "  \"credential\": {\n"
        + "    \"credential_type\": \"HMAC_KEY\",\n"
        + "    \"hmac_key_access_id\": \"some_hmac_key\",\n"
        + "    \"hmac_key_secret\": \"some_key_secret\"\n"
        + "  },"
        + "  \"format\": " + formatConfig
        + "}");

  }

  public static void assertBaseConfig(GcsDestinationConfig gcsDestinationConfig) {
    assertEquals("test-bucket-name", gcsDestinationConfig.getBucketName());
    assertEquals("test_path", gcsDestinationConfig.getBucketPath());
    assertEquals("us-east-2", gcsDestinationConfig.getBucketRegion());
  }

}
