package io.airbyte.integrations;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.base.Integration;
import io.airbyte.integrations.base.Source;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.io.IOException;

/**
 * By convention the spec is stored as a resource for java connectors. That resource is called spec.json.
 */
public abstract class DefaultSpecConnector implements Integration {
  @Override
  public ConnectorSpecification spec() throws IOException {
    // return a JsonSchema representation of the spec for the integration.
    final String resourceString = MoreResources.readResource("spec.json");
    return Jsons.deserialize(resourceString, ConnectorSpecification.class);
  }
}
