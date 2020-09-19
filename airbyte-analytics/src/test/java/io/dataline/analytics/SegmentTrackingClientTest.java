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
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;

import com.google.common.collect.ImmutableMap;
import com.segment.analytics.Analytics;
import com.segment.analytics.messages.IdentifyMessage;
import com.segment.analytics.messages.TrackMessage;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

class SegmentTrackingClientTest {

  private static final TrackingIdentity identity = new TrackingIdentity(UUID.randomUUID(), "a@dataline.io", false, false, true);

  private Analytics analytics;
  private SegmentTrackingClient segmentTrackingClient;

  @BeforeEach
  void setup() {
    analytics = mock(Analytics.class);
    segmentTrackingClient = new SegmentTrackingClient(() -> identity, analytics);
  }

  @SuppressWarnings("OptionalGetWithoutIsPresent")
  @Test
  void testIdentify() {
    // equals is not defined on MessageBuilder, so we need to use ArgumentCaptor to inspect each field
    // manually.
    ArgumentCaptor<IdentifyMessage.Builder> mockBuilder = ArgumentCaptor.forClass(IdentifyMessage.Builder.class);

    segmentTrackingClient.identify();

    verify(analytics).enqueue(mockBuilder.capture());
    final IdentifyMessage actual = mockBuilder.getValue().build();
    final Map<String, Object> expectedTraits = ImmutableMap.<String, Object>builder()
        .put("email", identity.getEmail().get())
        .put("anonymized", identity.isAnonymousDataCollection())
        .put("subscribed_newsletter", identity.isNews())
        .put("subscribed_security", identity.isSecurityUpdates())
        .build();
    assertEquals(identity.getCustomerId().toString(), actual.userId());
    assertEquals(expectedTraits, actual.traits());
  }

  @Test
  void testTrack() {
    ArgumentCaptor<TrackMessage.Builder> mockBuilder = ArgumentCaptor.forClass(TrackMessage.Builder.class);

    segmentTrackingClient.track("jump");

    verify(analytics).enqueue(mockBuilder.capture());
    TrackMessage actual = mockBuilder.getValue().build();
    assertEquals("jump", actual.event());
    assertEquals(identity.getCustomerId().toString(), actual.userId());
  }

  @Test
  void testTrackWithMetadata() {
    ArgumentCaptor<TrackMessage.Builder> mockBuilder = ArgumentCaptor.forClass(TrackMessage.Builder.class);
    final ImmutableMap<String, Object> metadata = ImmutableMap.of("height", "80 meters");

    segmentTrackingClient.track("jump", metadata);

    verify(analytics).enqueue(mockBuilder.capture());
    TrackMessage actual = mockBuilder.getValue().build();
    assertEquals("jump", actual.event());
    assertEquals(identity.getCustomerId().toString(), actual.userId());
    assertEquals(metadata, actual.properties());
  }

}
