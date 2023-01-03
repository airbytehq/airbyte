/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import org.junit.jupiter.api.Test;

class CloudTestingSourcesTest {

  @Test
  public void testSpec() throws Exception {
    final ConnectorSpecification actual = new CloudTestingSources().spec();
    final ConnectorSpecification expected = Jsons.deserialize(
        MoreResources.readResource("expected_spec.json"), ConnectorSpecification.class);

    assertEquals(expected, actual);
  }

}
