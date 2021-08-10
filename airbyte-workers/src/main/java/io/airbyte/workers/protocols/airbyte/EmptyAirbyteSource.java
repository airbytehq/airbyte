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

package io.airbyte.workers.protocols.airbyte;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StandardTapConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteStateMessage;
import java.nio.file.Path;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * This source will never emit any messages. It can be used in cases where that is helpful (hint:
 * reset connection jobs).
 */
public class EmptyAirbyteSource implements AirbyteSource {

  private final AtomicBoolean hasEmittedState;

  public EmptyAirbyteSource() {
    hasEmittedState = new AtomicBoolean();
  }

  @Override
  public void start(StandardTapConfig input, Path jobRoot) throws Exception {
    // no op.
  }

  // always finished. it has no data to send.
  @Override
  public boolean isFinished() {
    return hasEmittedState.get();
  }

  @Override
  public Optional<AirbyteMessage> attemptRead() {
    if (!hasEmittedState.get()) {
      hasEmittedState.compareAndSet(false, true);
      return Optional.of(new AirbyteMessage().withType(Type.STATE).withState(new AirbyteStateMessage().withData(Jsons.emptyObject())));
    } else {
      return Optional.empty();
    }
  }

  @Override
  public void close() throws Exception {
    // no op.
  }

  @Override
  public void cancel() throws Exception {
    // no op.
  }

}
