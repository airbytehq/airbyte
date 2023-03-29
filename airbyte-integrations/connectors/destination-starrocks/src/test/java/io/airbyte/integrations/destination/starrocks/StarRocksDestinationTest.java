package io.airbyte.integrations.destination.starrocks;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.spy;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.io.IOException;
import java.time.Instant;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class StarRocksDestinationTest {
  private JsonNode config;
  @BeforeEach
  void setup() throws IOException {
    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("fe_host", "localhost")
        .put("http_port", 8030)
        .put("query_port", 9030)
        .put("database", "airbyte")
        .put("username", "root")
        .put("password", "")
        .build());
  }

  @Test
  void testSpec() throws Exception {
    final StarRocksDestination dest = spy(StarRocksDestination.class);
    final ConnectorSpecification actual = dest.spec();

    final String resourceString = MoreResources.readResource("spec.json");
    final ConnectorSpecification expected = Jsons.deserialize(resourceString, ConnectorSpecification.class);

    assertEquals(expected, actual);
  }


  // generate some messages. Taken from the postgres destination test
  private List<AirbyteMessage> generateTestMessages(final String namespace, final String streamName, final int start, final int end) {
    return IntStream.range(start, end)
        .boxed()
        .map(i -> new AirbyteMessage()
            .withType(AirbyteMessage.Type.RECORD)
            .withRecord(new AirbyteRecordMessage()
                .withStream(streamName)
                .withNamespace(namespace)
                .withEmittedAt(Instant.now().toEpochMilli())
                .withData(Jsons.jsonNode(ImmutableMap.of("id", i, "name", "human " + i)))))
        .collect(Collectors.toList());
  }
}