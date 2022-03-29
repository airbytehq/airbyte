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

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.*;
import org.junit.jupiter.api.Test;

class AwsDatalakeDestinationTest {

  /*
   * @Test void testGetOutputTableNameWithString() throws Exception { var actual =
   * DynamodbOutputTableHelper.getOutputTableName("test_table", "test_namespace", "test_stream");
   * assertEquals("test_table_test_namespace_test_stream", actual); }
   *
   * @Test void testGetOutputTableNameWithStream() throws Exception { var stream = new
   * AirbyteStream(); stream.setName("test_stream"); stream.setNamespace("test_namespace"); var actual
   * = DynamodbOutputTableHelper.getOutputTableName("test_table", stream);
   * assertEquals("test_table_test_namespace_test_stream", actual); }
   */
  @Test
  void testGetAwsDatalakeDestinationdbConfig() throws Exception {
    JsonNode json = Jsons.deserialize("""
                                      {
                                        "bucket_prefix": "test_prefix",
                                        "region": "test_region",
                                        "auth_mode": "USER",
                                        "bucket_name": "test_bucket",
                                        "aws_access_key_id": "test_access_key",
                                        "aws_account_id": "test_account_id",
                                        "lakeformation_database_name": "test_database",
                                        "aws_secret_access_key": "test_secret"
                                      }""");

    var config = AwsDatalakeDestinationConfig.getAwsDatalakeDestinationConfig(json);

    assertEquals(config.getBucketPrefix(), "test_prefix");
    assertEquals(config.getRegion(), "test_region");
    assertEquals(config.getAccessKeyId(), "test_access_key");
    assertEquals(config.getSecretAccessKey(), "test_secret");
  }
}
