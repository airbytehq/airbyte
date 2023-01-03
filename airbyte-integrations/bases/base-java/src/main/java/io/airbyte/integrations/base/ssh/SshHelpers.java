/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.ssh;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.io.IOException;

public class SshHelpers {

  public static ConnectorSpecification getSpecAndInjectSsh() throws IOException {
    final ConnectorSpecification originalSpec = Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);
    return injectSshIntoSpec(originalSpec);
  }

  public static ConnectorSpecification injectSshIntoSpec(final ConnectorSpecification connectorSpecification) throws IOException {
    final ConnectorSpecification originalSpec = Jsons.clone(connectorSpecification);
    final ObjectNode propNode = (ObjectNode) originalSpec.getConnectionSpecification().get("properties");
    propNode.set("tunnel_method", Jsons.deserialize(MoreResources.readResource("ssh-tunnel-spec.json")));
    return originalSpec;
  }

}
