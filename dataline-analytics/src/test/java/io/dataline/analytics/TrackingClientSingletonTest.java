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

package io.dataline.analytics;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.dataline.config.Configs;
import java.util.UUID;
import org.junit.jupiter.api.Test;

class TrackingClientSingletonTest {

  @Test
  void testCreateTrackingClientFromEnvLogging() {
    TrackingIdentitySupplier idSupplier = mock(TrackingIdentitySupplier.class);
    when(idSupplier.get()).thenReturn(new TrackingIdentity(UUID.randomUUID(), null));
    TrackingClientSingleton.set(Configs.TrackingStrategy.LOGGING, idSupplier);
    assertTrue(TrackingClientSingleton.get() instanceof LoggingTrackingClient);
  }

  @Test
  void testCreateTrackingClientFromEnvSegment() {
    TrackingIdentitySupplier idSupplier = mock(TrackingIdentitySupplier.class);
    when(idSupplier.get()).thenReturn(new TrackingIdentity(UUID.randomUUID(), null));
    TrackingClientSingleton.set(Configs.TrackingStrategy.SEGMENT, idSupplier);
    assertTrue(TrackingClientSingleton.get() instanceof SegmentTrackingClient);
  }

  @Test
  void testUsesExistingClient() {
    final TrackingClient trackingClient = mock(TrackingClient.class);
    TrackingClientSingleton.set(trackingClient);

    assertEquals(trackingClient, TrackingClientSingleton.get());
  }

}
