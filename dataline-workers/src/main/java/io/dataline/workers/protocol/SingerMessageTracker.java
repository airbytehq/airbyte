/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.workers.protocol;

import io.dataline.config.SingerMessage;
import io.dataline.config.State;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Consumer;

public class SingerMessageTracker implements Consumer<SingerMessage> {
  private final AtomicLong recordCount;
  private final AtomicReference<State> outputState;
  private final UUID connectionId;

  public SingerMessageTracker(UUID connectionId) {
    this.connectionId = connectionId;
    this.recordCount = new AtomicLong();
    this.outputState = new AtomicReference<>();
  }

  @Override
  public void accept(SingerMessage record) {
    if (record.getType().equals(SingerMessage.Type.RECORD)) {
      recordCount.incrementAndGet();
    }
    if (record.getType().equals(SingerMessage.Type.STATE)) {
      final State state = new State();
      state.setConnectionId(connectionId);
      state.setState(record);
      outputState.set(state);
    }
  }

  public long getRecordCount() {
    return recordCount.get();
  }

  public Optional<State> getOutputState() {
    return Optional.ofNullable(outputState.get());
  }
}
