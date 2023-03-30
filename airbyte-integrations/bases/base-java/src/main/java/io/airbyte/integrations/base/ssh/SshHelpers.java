/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.ssh;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.io.IOException;
import java.util.Optional;

public class SshHelpers {
  private static final String SSH_KEY_PATTERN = "-----BEGIN[ a-zA-Z0-9]+-----(.|\\n)*-----END[ a-zA-Z0-9]+-----";
  private static final String SSH_KEY_PATTERN_DESCRIPTOR = "PEM format";

  public static ConnectorSpecification getSpecAndInjectSsh() throws IOException {
    return getSpecAndInjectSsh(Optional.empty(), false);
  }

  public static ConnectorSpecification getSpecAndInjectSsh(final Optional<String> group, final boolean setSshKeyPatterns) throws IOException {
    final ConnectorSpecification originalSpec = Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);
    return injectSshIntoSpec(originalSpec, group, setSshKeyPatterns);
  }

  public static ConnectorSpecification injectSshIntoSpec(final ConnectorSpecification connectorSpecification) throws IOException {
    return injectSshIntoSpec(connectorSpecification, Optional.empty(), false);
  }

  public static ConnectorSpecification injectSshIntoSpec(final ConnectorSpecification connectorSpecification, final Optional<String> group, final boolean setSshKeyPatterns)
      throws IOException {
    final ConnectorSpecification originalSpec = Jsons.clone(connectorSpecification);
    final ObjectNode propNode = (ObjectNode) originalSpec.getConnectionSpecification().get("properties");
    final ObjectNode tunnelMethod = (ObjectNode) Jsons.deserialize(MoreResources.readResource("ssh-tunnel-spec.json"));
    if (group.isPresent()) {
      tunnelMethod.put("group", group.get());
    }
    if (setSshKeyPatterns) {
      tunnelMethod.get("oneOf").elements().forEachRemaining(node -> {
        final JsonNode properties = node.get("properties");
        if (properties.get("tunnel_method").get("const").asText().equals("SSH_KEY_AUTH")) {
          final ObjectNode sshKey = (ObjectNode) node.get("properties").get("ssh_key");
          sshKey.put("pattern", SSH_KEY_PATTERN);
          sshKey.put("pattern_descriptor", SSH_KEY_PATTERN_DESCRIPTOR);
        }
      });
    }
    propNode.set("tunnel_method", tunnelMethod);
    return originalSpec;
  }
}
