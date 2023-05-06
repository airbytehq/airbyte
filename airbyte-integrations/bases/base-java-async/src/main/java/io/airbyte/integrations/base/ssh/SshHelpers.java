/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.ssh;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.io.IOException;
import java.util.Optional;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.testcontainers.containers.Container;

public class SshHelpers {

  public static ConnectorSpecification getSpecAndInjectSsh() throws IOException {
    return getSpecAndInjectSsh(Optional.empty());
  }

  public static ConnectorSpecification getSpecAndInjectSsh(final Optional<String> group) throws IOException {
    final ConnectorSpecification originalSpec = Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);
    return injectSshIntoSpec(originalSpec, group);
  }

  public static ConnectorSpecification injectSshIntoSpec(final ConnectorSpecification connectorSpecification) throws IOException {
    return injectSshIntoSpec(connectorSpecification, Optional.empty());
  }

  public static ConnectorSpecification injectSshIntoSpec(final ConnectorSpecification connectorSpecification, final Optional<String> group)
      throws IOException {
    final ConnectorSpecification originalSpec = Jsons.clone(connectorSpecification);
    final ObjectNode propNode = (ObjectNode) originalSpec.getConnectionSpecification().get("properties");
    final ObjectNode tunnelMethod = (ObjectNode) Jsons.deserialize(MoreResources.readResource("ssh-tunnel-spec.json"));
    if (group.isPresent()) {
      tunnelMethod.put("group", group.get());
    }
    propNode.set("tunnel_method", tunnelMethod);
    return originalSpec;
  }

  /**
   * Returns the inner docker network ip address and port of a container. This can be used to reach a
   * container from another container running on the same network
   *
   * @param container container
   * @return a pair of host and port
   */
  public static ImmutablePair<String, Integer> getInnerContainerAddress(final Container container) {
    return ImmutablePair.of(
        container.getContainerInfo().getNetworkSettings().getNetworks().entrySet().stream().findFirst().get().getValue().getIpAddress(),
        (Integer) container.getExposedPorts().stream().findFirst().get());
  }

  /**
   * Returns the outer docker network ip address and port of a container. This can be used to reach a
   * container from the host machine
   *
   * @param container container
   * @return a pair of host and port
   */
  public static ImmutablePair<String, Integer> getOuterContainerAddress(final Container container) {
    return ImmutablePair.of(container.getHost(),
        container.getFirstMappedPort());
  }

}
