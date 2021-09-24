/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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
import java.util.UUID;
import java.util.function.Function;

public class SegmentTrackingClient implements TrackingClient {

  private static final String SEGMENT_WRITE_KEY = "7UDdp5K55CyiGgsauOr2pNNujGvmhaeu";
  private static final String AIRBYTE_VERSION_KEY = "airbyte_version";
  private static final String AIRBYTE_ROLE = "airbyte_role";

  // Analytics is threadsafe.
  private final Analytics analytics;
  private final Function<UUID, TrackingIdentity> identityFetcher;
  private final Deployment deployment;
  private final String airbyteRole;

  @VisibleForTesting
  SegmentTrackingClient(final Function<UUID, TrackingIdentity> identityFetcher,
                        final Deployment deployment,
                        final String airbyteRole,
                        final Analytics analytics) {
    this.identityFetcher = identityFetcher;
    this.deployment = deployment;
    this.analytics = analytics;
    this.airbyteRole = airbyteRole;
  }

  public SegmentTrackingClient(final Function<UUID, TrackingIdentity> identityFetcher,
                               final Deployment deployment,

                               final String airbyteRole) {
    this(identityFetcher, deployment, airbyteRole, Analytics.builder(SEGMENT_WRITE_KEY).build());
  }

  @Override
  public void identify(UUID workspaceId) {
    final TrackingIdentity trackingIdentity = identityFetcher.apply(workspaceId);
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
  public void alias(UUID workspaceId, String previousCustomerId) {
    analytics.enqueue(AliasMessage.builder(previousCustomerId).userId(identityFetcher.apply(workspaceId).getCustomerId().toString()));
  }

  @Override
  public void track(UUID workspaceId, String action) {
    track(workspaceId, action, Collections.emptyMap());
  }

  @Override
  public void track(UUID workspaceId, String action, Map<String, Object> metadata) {
    final Map<String, Object> mapCopy = new HashMap<>(metadata);
    final TrackingIdentity trackingIdentity = identityFetcher.apply(workspaceId);
    mapCopy.put(AIRBYTE_VERSION_KEY, trackingIdentity.getAirbyteVersion());
    if (!metadata.isEmpty()) {
      trackingIdentity.getEmail().ifPresent(email -> mapCopy.put("email", email));
    }
    analytics.enqueue(TrackMessage.builder(action)
        .userId(trackingIdentity.getCustomerId().toString())
        .properties(mapCopy));
  }

}
