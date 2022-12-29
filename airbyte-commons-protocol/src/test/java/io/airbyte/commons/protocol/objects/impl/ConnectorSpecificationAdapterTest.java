/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.objects.impl;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.protocol.objects.ConnectorSpecification;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.io.Serializable;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.List;
import lombok.EqualsAndHashCode;
import org.junit.jupiter.api.Test;

@EqualsAndHashCode
class TestWrapper implements Serializable {

  @JsonProperty("connectorSpecification")
  private ConnectorSpecification connectionSpecification;

  public ConnectorSpecification getConnectionSpecification() {
    return connectionSpecification;
  }

  public TestWrapper withConnectorSpecification(final ConnectorSpecification connectorSpecification) {
    this.connectionSpecification = connectorSpecification;
    return this;
  }

}

class ConnectorSpecificationAdapterTest {

  @Test
  void serDeRoundTrip() throws URISyntaxException {
    final TestWrapper init = new TestWrapper()
        .withConnectorSpecification(
            new ConnectorSpecificationAdapter(
                new io.airbyte.protocol.models.ConnectorSpecification()
                    .withDocumentationUrl(new URI("https://airbyte.io"))
                    .withChangelogUrl(new URI("https://changelog.io"))
                    .withConnectionSpecification(Jsons.deserialize("{\"test\": \"data\"}"))
                    .withSupportedDestinationSyncModes(List.of(DestinationSyncMode.OVERWRITE, DestinationSyncMode.APPEND_DEDUP))
                    .withSupportsDBT(true)
                    .withSupportsIncremental(true)
                    .withSupportsNormalization(false)));

    final String serialized = Jsons.serialize(init);
    final TestWrapper result = Jsons.deserialize(serialized, TestWrapper.class);

    assertEquals(init, result);
    assertEquals(new URI("https://airbyte.io"), result.getConnectionSpecification().getDocumentationUrl());
  }

  @Test
  void testFieldMapping() throws URISyntaxException {
    final io.airbyte.protocol.models.ConnectorSpecification rawSpec = new io.airbyte.protocol.models.ConnectorSpecification()
        .withDocumentationUrl(new URI("https://doc.com"))
        .withChangelogUrl(new URI("https://change.log"))
        .withConnectionSpecification(Jsons.deserialize("{\"test\": \"data\"}"))
        .withSupportedDestinationSyncModes(List.of(DestinationSyncMode.APPEND, DestinationSyncMode.OVERWRITE, DestinationSyncMode.APPEND_DEDUP))
        .withSupportsDBT(false)
        .withSupportsIncremental(true)
        .withSupportsNormalization(false);

    final ConnectorSpecification spec = new ConnectorSpecificationAdapter(rawSpec);
    assertEquals(rawSpec.getDocumentationUrl(), spec.getDocumentationUrl());
    assertEquals(rawSpec.getChangelogUrl(), spec.getChangelogUrl());
    assertEquals(rawSpec.getConnectionSpecification(), spec.getConnectorSpecification());
    assertEquals(List.of(
        io.airbyte.commons.protocol.objects.DestinationSyncMode.APPEND,
        io.airbyte.commons.protocol.objects.DestinationSyncMode.OVERWRITE,
        io.airbyte.commons.protocol.objects.DestinationSyncMode.APPEND_DEDUP), spec.getSupportedDestinationSyncModes());
    assertEquals(rawSpec.getSupportsDBT(), spec.isSupportingDBT());
    assertEquals(rawSpec.getSupportsIncremental(), spec.isSupportingIncremental());
    assertEquals(rawSpec.getSupportsNormalization(), spec.isSupportingNormalization());
  }

}
