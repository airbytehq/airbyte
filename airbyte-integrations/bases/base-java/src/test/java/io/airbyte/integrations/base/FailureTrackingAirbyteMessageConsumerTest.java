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

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;

import io.airbyte.protocol.models.AirbyteMessage;
import org.junit.jupiter.api.Test;

class FailureTrackingAirbyteMessageConsumerTest {

  @Test
  void testStartNoFailure() throws Exception {
    final TestConsumer consumer = spy(new TestConsumer());
    consumer.start();
    consumer.close();

    verify(consumer).close(false);
  }

  @Test
  void testStartWithFailure() throws Exception {
    final TestConsumer consumer = spy(new TestConsumer());
    doThrow(new RuntimeException()).when(consumer).startTracked();

    // verify the exception still gets thrown.
    assertThrows(RuntimeException.class, consumer::start);
    consumer.close();

    verify(consumer).close(true);
  }

  @Test
  void testAcceptNoFailure() throws Exception {
    final TestConsumer consumer = spy(new TestConsumer());

    final AirbyteMessage msg = mock(AirbyteMessage.class);
    consumer.accept(msg);
    consumer.close();

    verify(consumer).close(false);
  }

  @Test
  void testAcceptWithFailure() throws Exception {
    final TestConsumer consumer = spy(new TestConsumer());
    final AirbyteMessage msg = mock(AirbyteMessage.class);
    doThrow(new RuntimeException()).when(consumer).acceptTracked(any());

    // verify the exception still gets thrown.
    assertThrows(RuntimeException.class, () -> consumer.accept(msg));
    consumer.close();

    verify(consumer).close(true);
  }

  static class TestConsumer extends FailureTrackingAirbyteMessageConsumer {

    @Override
    protected void startTracked() {

    }

    @Override
    protected void acceptTracked(AirbyteMessage s) {

    }

    @Override
    protected void close(boolean hasFailed) {

    }

  }

}
