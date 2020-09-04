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

import com.google.common.annotations.VisibleForTesting;
import io.dataline.config.Configs;
import io.dataline.config.EnvConfigs;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.DefaultConfigPersistence;
import java.nio.file.Path;

public class TrackingClientSingleton {

  private static TrackingClient trackingClient;

  public static TrackingClient get() {
    if (trackingClient == null) {
      setFromEnv();
    }
    return trackingClient;
  }

  public static void setFromEnv() {
    final Configs configs = new EnvConfigs();
    final Path configRoot = configs.getConfigRoot();
    final ConfigPersistence configPersistence = new DefaultConfigPersistence(configRoot);

    set(new EnvConfigs().getTrackingStrategy(), new TrackingIdentitySupplier(configPersistence));
  }

  public static void set(TrackingClient trackingClient) {
    TrackingClientSingleton.trackingClient = trackingClient;
  }

  @VisibleForTesting
  static void set(Configs.TrackingStrategy trackingStrategy, TrackingIdentitySupplier trackingIdentitySupplier) {
    final TrackingIdentity trackingIdentity = trackingIdentitySupplier.get();

    switch (trackingStrategy) {
      case SEGMENT:
        set(new SegmentTrackingClient(trackingIdentity));
        break;
      case LOGGING:
        set(new LoggingTrackingClient(trackingIdentity));
        break;
      default:
        throw new RuntimeException("unrecognized tracking strategy");
    }
  }

}
