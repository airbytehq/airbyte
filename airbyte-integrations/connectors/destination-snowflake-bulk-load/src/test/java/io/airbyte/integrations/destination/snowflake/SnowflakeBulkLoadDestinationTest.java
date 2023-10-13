/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.params.provider.Arguments.arguments;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.cdk.integrations.base.DestinationConfig;
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer;
import io.airbyte.cdk.integrations.destination_async.AsyncStreamConsumer;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConnectorSpecification;

import java.util.stream.Stream;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

import static org.junit.jupiter.api.Assertions.assertEquals;


public class SnowflakeBulkLoadDestinationTest {

  @BeforeEach
  public void setup() {
    DestinationConfig.initialize(Jsons.emptyObject());
  }

  @Test
  void testGetSpec() throws Exception {
    System.out.println(new SnowflakeBulkLoadDestination().spec().getConnectionSpecification());
    assertEquals(Jsons.deserialize(MoreResources.readResource("expected_spec.json"), ConnectorSpecification.class),
        new SnowflakeBulkLoadDestination().spec());
  }

}
