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

import com.google.common.collect.ImmutableMap;
import com.segment.analytics.Analytics;
import com.segment.analytics.messages.IdentifyMessage;
import com.segment.analytics.messages.TrackMessage;
import java.util.Collections;
import java.util.Map;

public class SegmentTrackingClient implements TrackingClient {

  private static final String SEGMENT_WRITE_KEY = "7UDdp5K55CyiGgsauOr2pNNujGvmhaeu";

  private final Analytics analytics;
  private final TrackingIdentity identity;

  public SegmentTrackingClient(TrackingIdentity identity) {
    // Analytics is threadsafe.
    this.analytics = Analytics.builder(SEGMENT_WRITE_KEY).build();
    this.identity = identity;
  }

  @Override
  public void identify() {
    final ImmutableMap.Builder<String, Object> identityMetadataBuilder = ImmutableMap.builder();
    identity.getEmail().ifPresent(email -> identityMetadataBuilder.put("email", email));

    analytics.enqueue(IdentifyMessage.builder()
        .userId(identity.getCustomerId().toString())
        .traits(identityMetadataBuilder.build()));
  }

  @Override
  public void track(String action) {
    track(action, Collections.emptyMap());
  }

  @Override
  public void track(String action, Map<String, Object> metadata) {
    analytics.enqueue(TrackMessage.builder(action)
        .userId(identity.getCustomerId().toString())
        .properties(metadata));
  }

}
