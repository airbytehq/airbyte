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
import io.airbyte.config.Configs;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.PersistenceConstants;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.function.Supplier;

public class TrackingClientSingleton {

  private static final Object lock = new Object();
  private static TrackingClient trackingClient;

  public static TrackingClient get() {
    synchronized (lock) {
      if (trackingClient == null) {
        initialize();
      }
      return trackingClient;
    }
  }

  @VisibleForTesting
  static void initialize(TrackingClient trackingClient) {
    synchronized (lock) {
      TrackingClientSingleton.trackingClient = trackingClient;
    }
  }

  public static void initialize(final Configs.TrackingStrategy trackingStrategy,
                                final Deployment deployment,
                                final String airbyteRole,
                                final String airbyteVersion,
                                final ConfigRepository configRepository) {
    initialize(createTrackingClient(
        trackingStrategy,
        deployment,
        airbyteRole,
        () -> getTrackingIdentity(configRepository, airbyteVersion)));
  }

  // fallback on a logging client with an empty identity.
  private static void initialize() {
    initialize(new LoggingTrackingClient(TrackingIdentity::empty));
  }

  @VisibleForTesting
  static TrackingIdentity getTrackingIdentity(ConfigRepository configRepository, String airbyteVersion) {
    try {
      final StandardWorkspace workspace = configRepository.getStandardWorkspace(PersistenceConstants.DEFAULT_WORKSPACE_ID, true);
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
    } catch (ConfigNotFoundException e) {
      throw new RuntimeException("could not find workspace with id: " + PersistenceConstants.DEFAULT_WORKSPACE_ID, e);
    } catch (JsonValidationException | IOException e) {
      throw new RuntimeException(e);
    }
  }

  /**
   * Creates a tracking client that uses the appropriate strategy from an identity supplier.
   *
   * @param trackingStrategy - what type of tracker we want to use.
   * @param deployment - deployment tracking info. static because it should not change once the
   *        instance is running.
   * @param airbyteRole
   * @param trackingIdentitySupplier - how we get the identity of the user. we have a supplier,
   *        because we if the identity updates over time (which happens during initial setup), we
   *        always want the most recent info.
   * @return tracking client
   */
  @VisibleForTesting
  static TrackingClient createTrackingClient(final Configs.TrackingStrategy trackingStrategy,
                                             final Deployment deployment,
                                             final String airbyteRole,
                                             final Supplier<TrackingIdentity> trackingIdentitySupplier) {
    return switch (trackingStrategy) {
      case SEGMENT -> new SegmentTrackingClient(trackingIdentitySupplier, deployment, airbyteRole);
      case LOGGING -> new LoggingTrackingClient(trackingIdentitySupplier);
      default -> throw new IllegalStateException("unrecognized tracking strategy");
    };
  }

}
