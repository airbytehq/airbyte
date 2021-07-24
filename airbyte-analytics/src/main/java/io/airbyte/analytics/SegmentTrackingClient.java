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

package io.airbyte.analytics;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Strings;
import com.segment.analytics.Analytics;
import com.segment.analytics.messages.AliasMessage;
import com.segment.analytics.messages.IdentifyMessage;
import com.segment.analytics.messages.TrackMessage;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Supplier;

public class SegmentTrackingClient implements TrackingClient {

  private static final String SEGMENT_WRITE_KEY = "7UDdp5K55CyiGgsauOr2pNNujGvmhaeu";
  private static final String AIRBYTE_VERSION_KEY = "airbyte_version";
  private static final String AIRBYTE_ROLE = "airbyte_role";

  // Analytics is threadsafe.
  private final Analytics analytics;
  private final Supplier<TrackingIdentity> identitySupplier;
  private final Deployment deployment;
  private final String airbyteRole;

  @VisibleForTesting
  SegmentTrackingClient(final Supplier<TrackingIdentity> identitySupplier,
                        final Deployment deployment,

                        final String airbyteRole,
                        final Analytics analytics) {
    this.identitySupplier = identitySupplier;
    this.deployment = deployment;
    this.analytics = analytics;
    this.airbyteRole = airbyteRole;
  }

  public SegmentTrackingClient(final Supplier<TrackingIdentity> identitySupplier,
                               final Deployment deployment,

                               final String airbyteRole) {
    this(identitySupplier, deployment, airbyteRole, Analytics.builder(SEGMENT_WRITE_KEY).build());
  }

  @Override
  public void identify() {
    final TrackingIdentity trackingIdentity = identitySupplier.get();
    final Map<String, Object> identityMetadata = new HashMap<>();

    // deployment
    identityMetadata.put(AIRBYTE_VERSION_KEY, trackingIdentity.getAirbyteVersion());
    identityMetadata.put("deployment_mode", deployment.getDeploymentMode());
    identityMetadata.put("deployment_env", deployment.getDeploymentEnv());
    identityMetadata.put("deployment_id", deployment.getDeploymentId());

    // workspace (includes info that in the future we would store in an organization)
    identityMetadata.put("anonymized", trackingIdentity.isAnonymousDataCollection());
    identityMetadata.put("subscribed_newsletter", trackingIdentity.isNews());
    identityMetadata.put("subscribed_security", trackingIdentity.isSecurityUpdates());
    trackingIdentity.getEmail().ifPresent(email -> identityMetadata.put("email", email));

    // other
    if (!Strings.isNullOrEmpty(airbyteRole)) {
      identityMetadata.put(AIRBYTE_ROLE, airbyteRole);
    }

    analytics.enqueue(IdentifyMessage.builder()
        // user id is scoped by workspace. there is no cross-workspace tracking.
        .userId(trackingIdentity.getCustomerId().toString())
        .traits(identityMetadata));
  }

  @Override
  public void alias(String previousCustomerId) {
    analytics.enqueue(AliasMessage.builder(previousCustomerId).userId(identitySupplier.get().getCustomerId().toString()));
  }

  @Override
  public void track(String action) {
    track(action, Collections.emptyMap());
  }

  @Override
  public void track(String action, Map<String, Object> metadata) {
    final Map<String, Object> mapCopy = new HashMap<>(metadata);
    final TrackingIdentity trackingIdentity = identitySupplier.get();
    mapCopy.put(AIRBYTE_VERSION_KEY, trackingIdentity.getAirbyteVersion());
    if (!metadata.isEmpty()) {
      trackingIdentity.getEmail().ifPresent(email -> mapCopy.put("email", email));
    }
    analytics.enqueue(TrackMessage.builder(action)
        .userId(trackingIdentity.getCustomerId().toString())
        .properties(mapCopy));
  }

}
