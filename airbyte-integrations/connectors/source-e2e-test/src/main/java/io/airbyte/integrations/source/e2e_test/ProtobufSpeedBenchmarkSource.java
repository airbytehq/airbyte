/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.BaseConnector;
import io.airbyte.cdk.integrations.base.ProtobufSource;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.protos.AirbyteMessage;

/**
 * This source is optimized for creating records very fast. It optimizes for speed over flexibility.
 */
public class ProtobufSpeedBenchmarkSource extends BaseConnector implements ProtobufSource {

  @Override
  public AirbyteConnectionStatus check(final JsonNode jsonConfig) {
    try {
      final SpeedBenchmarkConfig sourceConfig = SpeedBenchmarkConfig.parseFromConfig(jsonConfig);
      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED).withMessage("Source config: " + sourceConfig);
    } catch (final Exception e) {
      return new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage(e.getMessage());
    }
  }

  @Override
  public AirbyteCatalog discover(final JsonNode jsonConfig) throws Exception {
    final SpeedBenchmarkConfig sourceConfig = SpeedBenchmarkConfig.parseFromConfig(jsonConfig);
    return sourceConfig.getCatalog();
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(final JsonNode jsonConfig, final ConfiguredAirbyteCatalog catalog, final JsonNode state)
      throws Exception {
    final SpeedBenchmarkConfig sourceConfig = SpeedBenchmarkConfig.parseFromConfig(jsonConfig);
    return AutoCloseableIterators.fromIterator(new ProtobufSpeedBenchmarkGeneratorIterator(sourceConfig.maxRecords()));
  }

  public static void main(String[] args) {
    ProtobufSpeedBenchmarkSource source = new ProtobufSpeedBenchmarkSource();

    String config = """
                    {
                      "type": "BENCHMARK",
                      "schema": "FIVE_STRING_COLUMNS",
                      "terminationCondition": {
                        "type": "MAX_RECORDS",
                        "max": "100"
                      }
                    }
                    """;

    try (AutoCloseableIterator<AirbyteMessage> it = source.read(Jsons.deserialize(config), null, null)) {
      while (it.hasNext()) {
        AirbyteMessage next = it.next();
        System.out.println(next);
      }
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

}
