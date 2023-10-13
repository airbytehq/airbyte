/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.params.provider.Arguments.arguments;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.base.DestinationConfig;
import io.airbyte.integrations.base.SerializedAirbyteMessageConsumer;
import io.airbyte.integrations.destination.snowflake.SnowflakeDestination.DestinationType;
import io.airbyte.integrations.destination_async.AsyncStreamConsumer;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.stream.Stream;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

public class SnowflakeBulkLoadDestinationTest {

  @BeforeEach
  public void setup() {
    DestinationConfig.initialize(Jsons.emptyObject());
  }

  private static Stream<Arguments> destinationTypeToConfig() {
    return Stream.of(arguments("bulk_load_config.json", DestinationType.BULK_LOAD_FROM_S3));
  }

  @ParameterizedTest
  @MethodSource("destinationTypeToConfig")
  public void testS3ConfigType(final String configFileName, final DestinationType expectedDestinationType) throws Exception {
    final JsonNode config = Jsons.deserialize(MoreResources.readResource(configFileName), JsonNode.class);
    final DestinationType typeFromConfig = SnowflakeDestinationResolver.getTypeFromConfig(config);
    assertEquals(expectedDestinationType, typeFromConfig);
  }

  @Test
  void testWriteSnowflakeInternal() throws Exception {
    final JsonNode config = Jsons.deserialize(MoreResources.readResource("bulk_load_config.json"), JsonNode.class);
    final SerializedAirbyteMessageConsumer consumer = new SnowflakeDestination(OssCloudEnvVarConsts.AIRBYTE_OSS)
        .getSerializedMessageConsumer(config, new ConfiguredAirbyteCatalog(), null);
    assertEquals(AsyncStreamConsumer.class, consumer.getClass());
  }

}
