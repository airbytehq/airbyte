/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.analytics;

import java.util.Collections;
import java.util.Map;
import java.util.UUID;
import java.util.function.Function;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class LoggingTrackingClient implements TrackingClient {

  private static final Logger LOGGER = LoggerFactory.getLogger(LoggingTrackingClient.class);

  private final Function<UUID, TrackingIdentity> identityFetcher;

  public LoggingTrackingClient(Function<UUID, TrackingIdentity> identityFetcher) {
    this.identityFetcher = identityFetcher;
  }

  @Override
  public void identify(UUID workspaceId) {
    LOGGER.info("identify. userId: {}", identityFetcher.apply(workspaceId).getCustomerId());
  }

  @Override
  public void alias(UUID workspaceId, String previousCustomerId) {
    LOGGER.info("merge. userId: {} previousUserId: {}", identityFetcher.apply(workspaceId).getCustomerId(), previousCustomerId);
  }

  @Override
  public void track(UUID workspaceId, String action) {
    track(workspaceId, action, Collections.emptyMap());
  }

  @Override
  public void track(UUID workspaceId, String action, Map<String, Object> metadata) {
    LOGGER.info("track. version: {}, userId: {}, action: {}, metadata: {}",
        identityFetcher.apply(workspaceId).getAirbyteVersion(),
        identityFetcher.apply(workspaceId).getCustomerId(),
        action,
        metadata);
  }

}
