/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.base.Integration;
import io.airbyte.protocol.models.v0.ConnectorSpecification;

public abstract class BaseConnector implements Integration {

  /**
   * By convention the spec is stored as a resource for java connectors. That resource is called
   * spec.json.
   *
   * @return specification.
   * @throws Exception - any exception.
   */
  @Override
  public ConnectorSpecification spec() throws Exception {
    // return a JsonSchema representation of the spec for the integration.
    final String resourceString = MoreResources.readResource("spec.json");
    return Jsons.deserialize(resourceString, ConnectorSpecification.class);
  }

}
