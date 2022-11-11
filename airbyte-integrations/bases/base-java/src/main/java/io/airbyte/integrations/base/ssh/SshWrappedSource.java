/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.ssh;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.base.Source;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SshWrappedSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(SshWrappedSource.class);
  private final Source delegate;
  private final List<String> hostKey;
  private final List<String> portKey;

  public SshWrappedSource(final Source delegate, final List<String> hostKey, final List<String> portKey) {
    this.delegate = delegate;
    this.hostKey = hostKey;
    this.portKey = portKey;
  }

  @Override
  public ConnectorSpecification spec() throws Exception {
    return SshHelpers.injectSshIntoSpec(delegate.spec());
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) throws Exception {
    return SshTunnel.sshWrap(config, hostKey, portKey, delegate::check);
  }

  @Override
  public AirbyteCatalog discover(final JsonNode config) throws Exception {
    return SshTunnel.sshWrap(config, hostKey, portKey, delegate::discover);
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(final JsonNode config, final ConfiguredAirbyteCatalog catalog, final JsonNode state)
      throws Exception {
    final SshTunnel tunnel = SshTunnel.getInstance(config, hostKey, portKey);
    final AutoCloseableIterator<AirbyteMessage> delegateRead;
    try {
      delegateRead = delegate.read(tunnel.getConfigInTunnel(), catalog, state);
    } catch (final Exception e) {
      LOGGER.error("Exception occurred while getting the delegate read iterator, closing SSH tunnel", e);
      tunnel.close();
      throw e;
    }
    return AutoCloseableIterators.appendOnClose(delegateRead, tunnel::close);
  }

}
