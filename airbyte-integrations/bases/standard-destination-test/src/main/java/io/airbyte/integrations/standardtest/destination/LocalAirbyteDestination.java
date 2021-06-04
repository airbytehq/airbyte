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

package io.airbyte.integrations.standardtest.destination;

import io.airbyte.config.StandardTargetConfig;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.workers.protocols.airbyte.AirbyteDestination;
import java.nio.file.Path;
import java.util.Optional;

// Simple class to host a Destination in-memory rather than spinning up a container for it.
// For debugging and testing purposes only; not recommended to use this for real code
public class LocalAirbyteDestination implements AirbyteDestination {

  private Destination dest;
  private AirbyteMessageConsumer consumer;
  private boolean isClosed = false;

  public LocalAirbyteDestination(Destination dest) {
    this.dest = dest;
  }

  @Override
  public void start(StandardTargetConfig targetConfig, Path jobRoot) throws Exception {
    consumer =
        dest.getConsumer(targetConfig.getDestinationConnectionConfiguration(), targetConfig.getCatalog(), Destination::defaultOutputRecordCollector);
    consumer.start();
  }

  @Override
  public void accept(AirbyteMessage message) throws Exception {
    consumer.accept(message);
  }

  @Override
  public void notifyEndOfStream() {
    // nothing to do here
  }

  @Override
  public void close() throws Exception {
    consumer.close();
    isClosed = true;
  }

  @Override
  public void cancel() {
    // nothing to do here
  }

  @Override
  public boolean isFinished() {
    return isClosed;
  }

  @Override
  public Optional<AirbyteMessage> attemptRead() {
    return Optional.empty();
  }

}
