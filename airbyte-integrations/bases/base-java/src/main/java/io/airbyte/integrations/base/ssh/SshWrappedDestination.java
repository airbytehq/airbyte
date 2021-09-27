/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.ssh;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.util.List;
import java.util.function.Consumer;

/**
 * Decorates a Destination with an SSH Tunnel using the standard configuration that Airbyte uses for
 * configuring SSH.
 */
public class SshWrappedDestination implements Destination {

  private final Destination delegate;
  private final List<String> hostKey;
  private final List<String> portKey;

  public SshWrappedDestination(final Destination delegate,
                               final List<String> hostKey,
                               final List<String> portKey) {
    this.delegate = delegate;
    this.hostKey = hostKey;
    this.portKey = portKey;
  }

  @Override
  public ConnectorSpecification spec() throws Exception {
    // inject the standard ssh configuration into the spec.
    final ConnectorSpecification originalSpec = delegate.spec();
    final ObjectNode propNode = (ObjectNode) originalSpec.getConnectionSpecification().get("properties");
    propNode.set("tunnel_method", Jsons.deserialize(MoreResources.readResource("ssh-tunnel-spec.json")));
    return originalSpec;
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) throws Exception {
    return SshTunnel.sshWrap(config, hostKey, portKey, delegate::check);
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector)
      throws Exception {
    final SshTunnel tunnel = SshTunnel.getInstance(config, hostKey, portKey);
    return AirbyteMessageConsumer.appendOnClose(delegate.getConsumer(tunnel.getConfigInTunnel(), catalog, outputRecordCollector), tunnel::close);
  }

}
