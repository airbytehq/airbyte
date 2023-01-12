/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.aws_datalake;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
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
