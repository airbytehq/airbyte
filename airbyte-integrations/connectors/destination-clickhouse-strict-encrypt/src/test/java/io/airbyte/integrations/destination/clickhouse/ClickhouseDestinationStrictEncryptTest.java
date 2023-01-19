/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import org.junit.jupiter.api.Test;

class ClickhouseDestinationStrictEncryptTest {

  @Test
  void testGetSpec() throws Exception {
    System.out.println(new ClickhouseDestinationStrictEncrypt().spec().getConnectionSpecification());
    assertEquals(Jsons.deserialize(MoreResources.readResource("expected_spec.json"), ConnectorSpecification.class),
        new ClickhouseDestinationStrictEncrypt().spec());
  }

}
