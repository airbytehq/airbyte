/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.analytics;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Strings;
import com.segment.analytics.Analytics;
import com.segment.analytics.messages.AliasMessage;
import com.segment.analytics.messages.IdentifyMessage;
import com.segment.analytics.messages.TrackMessage;
import io.airbyte.config.StandardWorkspace;
import java.time.Instant;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.function.Function;
import javax.annotation.Nullable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class is a wrapper around the Segment backend Java SDK.
 * <p>
 * In general, the Segment SDK events have two pieces to them, a top-level userId field and a map of
 * properties.
 * <p>
 * As of 2021/11/03, the top level userId field is standardised on the
 * {@link StandardWorkspace#getCustomerId()} field. This field is a random UUID generated when a
 * workspace model is created. This standardisation is through OSS Airbyte and Cloud Airbyte. This
 * join key now underpins Airbyte OSS Segment tracking. Although the id is meaningless and the name
 * confusing, it is not worth performing a migration at this time. Interested parties can look at
 * https://github.com/airbytehq/airbyte/issues/7456 for more context.
 * <p>
 * Consumers utilising this class must understand that the top-level userId field is subject to this
 * constraint.
 * <p>
 * See the following document for details on tracked events. Please update this document if tracked
 * events change.
 * https://docs.google.com/spreadsheets/d/1lGLmLIhiSPt_-oaEf3CpK-IxXnCO0NRHurvmWldoA2w/edit#gid=1567609168
 */
public class SegmentTrackingClient implements TrackingClient {

  private static final Logger LOGGER = LoggerFactory.getLogger(SegmentTrackingClient.class);

  public static final String CUSTOMER_ID_KEY = "user_id";
  private static final String SEGMENT_WRITE_KEY = "7UDdp5K55CyiGgsauOr2pNNujGvmhaeu";
  private static final String AIRBYTE_VERSION_KEY = "airbyte_version";
  private static final String AIRBYTE_ROLE = "airbyte_role";
  private static final String AIRBYTE_TRACKED_AT = "tracked_at";

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
  public void identify(final UUID workspaceId) {
    final TrackingIdentity trackingIdentity = identityFetcher.apply(workspaceId);
    final Map<String, Object> identityMetadata = new HashMap<>();

    // deployment
    identityMetadata.put(AIRBYTE_VERSION_KEY, trackingIdentity.getAirbyteVersion().serialize());
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

    final String joinKey = trackingIdentity.getCustomerId().toString();
    analytics.enqueue(IdentifyMessage.builder()
        // user id is scoped by workspace. there is no cross-workspace tracking.
        .userId(joinKey)
        .traits(identityMetadata));
  }

  @Override
  public void alias(final UUID workspaceId, final String previousCustomerId) {
    final var joinKey = identityFetcher.apply(workspaceId).getCustomerId().toString();
    analytics.enqueue(AliasMessage.builder(previousCustomerId).userId(joinKey));
  }

  @Override
  public void track(@Nullable final UUID workspaceId, final String action) {
    track(workspaceId, action, Collections.emptyMap());
  }

  @Override
  public void track(@Nullable final UUID workspaceId, final String action, final Map<String, Object> metadata) {
    if (workspaceId == null) {
      LOGGER.error("Could not track action {} due to null workspaceId", action);
      return;
    }
    final Map<String, Object> mapCopy = new HashMap<>(metadata);
    final TrackingIdentity trackingIdentity = identityFetcher.apply(workspaceId);

    // Always add these traits.
    mapCopy.put(AIRBYTE_VERSION_KEY, trackingIdentity.getAirbyteVersion().serialize());
    mapCopy.put(CUSTOMER_ID_KEY, trackingIdentity.getCustomerId());
    mapCopy.put(AIRBYTE_TRACKED_AT, Instant.now().toString());
    if (!metadata.isEmpty()) {
      trackingIdentity.getEmail().ifPresent(email -> mapCopy.put("email", email));
    }

    final var joinKey = trackingIdentity.getCustomerId().toString();
    analytics.enqueue(TrackMessage.builder(action)
        .userId(joinKey)
        .properties(mapCopy));
  }

}
