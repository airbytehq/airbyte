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

package io.airbyte.integrations.base;

import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Minimal abstract class intended to handle the case where a destination commits record messages as
 * it receives them. In these cases, the destination can simply emit the the state message
 * immediately.
 */
public abstract class ImmediateStateAirbyteMessageConsumer extends FailureTrackingAirbyteMessageConsumer implements AirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(ImmediateStateAirbyteMessageConsumer.class);
  private final Consumer<AirbyteMessage> outputRecordCollector;

  public ImmediateStateAirbyteMessageConsumer(Consumer<AirbyteMessage> outputRecordCollector) {
    this.outputRecordCollector = outputRecordCollector;
  }

  protected abstract void acceptTracked(AirbyteMessage msg) throws Exception;

  @Override
  public void accept(AirbyteMessage message) throws Exception {
    if (message.getType() == Type.STATE) {
      outputRecordCollector.accept(message);
    }
    super.accept(message);
  }

}
