/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.lang;

import com.google.common.annotations.VisibleForTesting;
import java.io.Closeable;
import java.util.Collection;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Registers a shutdown hook that calls the close method of the provided objects. If an object does
 * not support either the {@link AutoCloseable} or {@link Closeable} interface, it will be ignored.
 *
 * This is a temporary class that is being provided to ensure that resources created by each
 * application are properly closed on shutdown. This logic will no longer be necessary once an
 * application framework is introduced to the project that can provide object lifecycle management.
 */
public class CloseableShutdownHook {

  private static final Logger LOGGER = LoggerFactory.getLogger(CloseableShutdownHook.class);

  /**
   * Registers a runtime shutdown hook with the application for each provided closeable object.
   *
   * @param objects An array of objects to be closed on application shutdown.
   */
  public static void registerRuntimeShutdownHook(final Object... objects) {
    Runtime.getRuntime().addShutdownHook(buildShutdownHookThread(objects));
  }

  /**
   * Builds the {@link Thread} that will be registered as an application shutdown hook.
   *
   * @param objects An array of objects to be closed on application shutdown.
   * @return The application shutdown hook {@link Thread}.
   */
  @VisibleForTesting
  static Thread buildShutdownHookThread(final Object... objects) {
    final Collection<AutoCloseable> autoCloseables = Stream.of(objects)
        .filter(o -> o != null)
        .filter(o -> o instanceof AutoCloseable)
        .map(o -> AutoCloseable.class.cast(o))
        .collect(Collectors.toList());

    return new Thread(() -> {
      autoCloseables.forEach(CloseableShutdownHook::close);
    });
  }

  private static void close(final AutoCloseable autoCloseable) {
    try {
      autoCloseable.close();
    } catch (final Exception e) {
      LOGGER.error("Unable to close object {}.", autoCloseable.getClass().getName(), e);
    }
  }

}
