/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.elasticsearch;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import org.junit.jupiter.api.Test;

public class ElasticsearchDestinationStrictEncryptTest {

  @Test
  void testSpec() throws Exception {
    final ConnectorSpecification actual = new ElasticsearchStrictEncryptDestination().spec();
    final ConnectorSpecification expected = Jsons.deserialize(MoreResources.readResource("expected_spec.json"), ConnectorSpecification.class);

    assertEquals(expected, actual);
  }

}
