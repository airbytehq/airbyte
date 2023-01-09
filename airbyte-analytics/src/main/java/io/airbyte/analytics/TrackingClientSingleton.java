/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.analytics;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.UUID;
import java.util.function.Function;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TrackingClientSingleton {

  private static final Logger LOGGER = LoggerFactory.getLogger(LoggingTrackingClient.class);

  private static final Object lock = new Object();
  private static TrackingClient trackingClient;

  public static TrackingClient get() {
    synchronized (lock) {
      if (trackingClient == null) {
        LOGGER.warn("Attempting to fetch an initialized track client. Initializing a default one.");
        initialize();
      }
      return trackingClient;
    }
  }

  @VisibleForTesting
  static void initialize(final TrackingClient trackingClient) {
    synchronized (lock) {
      TrackingClientSingleton.trackingClient = trackingClient;
    }
  }

  public static void initialize(final Configs.TrackingStrategy trackingStrategy,
                                final Deployment deployment,
                                final String airbyteRole,
                                final AirbyteVersion airbyteVersion,
                                final ConfigRepository configRepository) {
    initialize(createTrackingClient(
        trackingStrategy,
        deployment,
        airbyteRole,
        (workspaceId) -> getTrackingIdentity(configRepository, airbyteVersion, workspaceId)));
  }

  // fallback on a logging client with an empty identity.
  private static void initialize() {
    initialize(new LoggingTrackingClient(workspaceId -> TrackingIdentity.empty()));
  }

  @VisibleForTesting
  static TrackingIdentity getTrackingIdentity(final ConfigRepository configRepository, final AirbyteVersion airbyteVersion, final UUID workspaceId) {
    try {
      final StandardWorkspace workspace = configRepository.getStandardWorkspaceNoSecrets(workspaceId, true);
      String email = null;
      if (workspace.getEmail() != null && workspace.getAnonymousDataCollection() != null && !workspace.getAnonymousDataCollection()) {
        email = workspace.getEmail();
      }
      return new TrackingIdentity(
          airbyteVersion,
          workspace.getCustomerId(),
          email,
          workspace.getAnonymousDataCollection(),
          workspace.getNews(),
          workspace.getSecurityUpdates());
    } catch (final ConfigNotFoundException e) {
      throw new RuntimeException("could not find workspace with id: " + workspaceId, e);
    } catch (final JsonValidationException | IOException e) {
      throw new RuntimeException(e);
    }
  }

  // todo (cgardens) - trackingIdentityFetcher should probably have some sort of caching where it is
  // only re-fetched on identify or alias.
  /**
   * Creates a tracking client that uses the appropriate strategy from an identity supplier.
   *
   * @param trackingStrategy - what type of tracker we want to use.
   * @param deployment - deployment tracking info. static because it should not change once the
   *        instance is running.
   * @param airbyteRole
   * @param trackingIdentityFetcher - how we get the identity of the user. we have a function that
   *        takes in workspaceId and returns the tracking identity. it does not have any caching as
   *        email or other fields on the identity can change over time.
   * @return tracking client
   */
  @VisibleForTesting
  static TrackingClient createTrackingClient(final Configs.TrackingStrategy trackingStrategy,
                                             final Deployment deployment,
                                             final String airbyteRole,
                                             final Function<UUID, TrackingIdentity> trackingIdentityFetcher) {
    return switch (trackingStrategy) {
      case SEGMENT -> new SegmentTrackingClient(trackingIdentityFetcher, deployment, airbyteRole);
      case LOGGING -> new LoggingTrackingClient(trackingIdentityFetcher);
      default -> throw new IllegalStateException("unrecognized tracking strategy");
    };
  }

}
