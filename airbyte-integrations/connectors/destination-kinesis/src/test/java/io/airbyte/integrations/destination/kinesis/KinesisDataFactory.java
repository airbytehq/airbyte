/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kinesis;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;

public class KinesisDataFactory {

  private KinesisDataFactory() {

  }

  static JsonNode jsonConfig(String endpoint, String region, String accessKey, String privateKey) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("endpoint", endpoint)
        .put("region", region)
        .put("shardCount", 5)
        .put("accessKey", accessKey)
        .put("privateKey", privateKey)
        .put("bufferSize", 100)
        .build());
  }

}
