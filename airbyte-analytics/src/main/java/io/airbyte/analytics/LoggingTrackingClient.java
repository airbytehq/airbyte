/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.analytics;

import io.airbyte.commons.version.AirbyteVersion;
import java.util.Collections;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Function;
import javax.annotation.Nullable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class LoggingTrackingClient implements TrackingClient {

  private static final Logger LOGGER = LoggerFactory.getLogger(LoggingTrackingClient.class);

  private final Function<UUID, TrackingIdentity> identityFetcher;

  public LoggingTrackingClient(final Function<UUID, TrackingIdentity> identityFetcher) {
    this.identityFetcher = identityFetcher;
  }

  @Override
  public void identify(final UUID workspaceId) {
    LOGGER.info("identify. userId: {}", identityFetcher.apply(workspaceId).getCustomerId());
  }

  @Override
  public void alias(final UUID workspaceId, final String previousCustomerId) {
    LOGGER.info("merge. userId: {} previousUserId: {}", identityFetcher.apply(workspaceId).getCustomerId(), previousCustomerId);
  }

  @Override
  public void track(@Nullable final UUID workspaceId, final String action) {
    track(workspaceId, action, Collections.emptyMap());
  }

  @Override
  public void track(@Nullable final UUID workspaceId, final String action, final Map<String, Object> metadata) {
    String version = null;
    UUID userId = null;
    if (workspaceId != null) {
      version = Optional.ofNullable(identityFetcher.apply(workspaceId).getAirbyteVersion()).map(AirbyteVersion::serialize).orElse(null);
      userId = identityFetcher.apply(workspaceId).getCustomerId();
    }
    LOGGER.info("track. version: {}, userId: {}, action: {}, metadata: {}",
        version,
        userId,
        action,
        metadata);
  }

}
