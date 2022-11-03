/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Decorates a Destination with an SSH Tunnel using the standard configuration that Airbyte uses for
 * configuring SSH.
 */
public class SshWrappedDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(SshWrappedDestination.class);

  private final Destination delegate;
  private final List<String> hostKey;
  private final List<String> portKey;
  private final String endPointKey;

  public SshWrappedDestination(final Destination delegate,
                               final List<String> hostKey,
                               final List<String> portKey) {
    this.delegate = delegate;
    this.hostKey = hostKey;
    this.portKey = portKey;
    this.endPointKey = null;
  }

  public SshWrappedDestination(final Destination delegate,
                               final String endPointKey) {
    this.delegate = delegate;
    this.endPointKey = endPointKey;
    this.portKey = null;
    this.hostKey = null;
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
    return (endPointKey != null) ? SshTunnel.sshWrap(config, endPointKey, delegate::check)
        : SshTunnel.sshWrap(config, hostKey, portKey, delegate::check);
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector)
      throws Exception {
    final SshTunnel tunnel = (endPointKey != null) ? SshTunnel.getInstance(config, endPointKey) : SshTunnel.getInstance(config, hostKey, portKey);

    final AirbyteMessageConsumer delegateConsumer;
    try {
      delegateConsumer = delegate.getConsumer(tunnel.getConfigInTunnel(), catalog, outputRecordCollector);
    } catch (final Exception e) {
      LOGGER.error("Exception occurred while getting the delegate consumer, closing SSH tunnel", e);
      tunnel.close();
      throw e;
    }
    return AirbyteMessageConsumer.appendOnClose(delegateConsumer, tunnel::close);
  }

}
