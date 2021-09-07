/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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

public class SshWrappedSource implements Source {

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
    return AutoCloseableIterators.appendOnClose(delegate.read(tunnel.getConfigInTunnel(), catalog, state), tunnel::close);
  }

}
