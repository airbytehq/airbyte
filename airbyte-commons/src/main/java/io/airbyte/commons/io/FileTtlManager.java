/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.io;

import com.google.common.base.Preconditions;
import com.google.common.cache.Cache;
import com.google.common.cache.CacheBuilder;
import com.google.common.cache.RemovalNotification;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.time.Instant;
import java.util.concurrent.TimeUnit;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * The goal of this class is to remove files given a ttl. It does so WITHOUT adding any background
 * threads. The tradeoff it makes is that it only removes files that have reached their TTL (or if
 * the cache is full) whenever a new file is added to the manager. This is a good choice when trying
 * to avoid file size growing monotonically over long stretches of time.
 */
public class FileTtlManager {

  private static final Logger LOGGER = LoggerFactory.getLogger(FileTtlManager.class);

  private final Cache<Path, Instant> cache;
  private final long expirationDuration;
  private final TimeUnit expirationTimeUnit;

  public FileTtlManager(final long expirationDuration, final TimeUnit expirationTimeUnit, final long maxSize) {
    this.expirationDuration = expirationDuration;
    this.expirationTimeUnit = expirationTimeUnit;
    cache = CacheBuilder.newBuilder()
        .expireAfterWrite(expirationDuration, expirationTimeUnit)
        .maximumSize(maxSize)
        .removalListener((RemovalNotification<Path, Instant> removalNotification) -> {
          try {
            Files.deleteIfExists(removalNotification.getKey());
          } catch (final IOException e) {
            throw new RuntimeException("Failed to delete file at end of ttl: " + removalNotification.getKey(), e);
          }
        })
        .build();
  }

  public void register(final Path path) {
    Preconditions.checkNotNull(path);
    Preconditions.checkArgument(path.toFile().isFile()); // only accept files.

    // add to cache so that it will be deleted when expiration time is reached.
    cache.put(path, Instant.now());
    // also add schedule deletion when jvm ends (in case jvm ends before expiration is reached).
    path.toFile().deleteOnExit();
    reportCacheStatus();
  }

  private void reportCacheStatus() {
    final Instant now = Instant.now();
    final StringBuilder sb = new StringBuilder(String.format("Files with ttls (total files: %s):\n", cache.size()));

    cache.asMap().forEach((path, registeredAt) -> {
      try {
        final Duration timeElapsed = Duration.between(registeredAt, now);
        final Duration diffBetweenTotalLifeTimeAndTimeElapsed = Duration.of(expirationDuration, expirationTimeUnit.toChronoUnit()).minus(timeElapsed);
        final long minutesRemaining = Math.max(diffBetweenTotalLifeTimeAndTimeElapsed.toMinutes(), 0L);

        sb.append(String.format("File name: %s, Size (MB) %s, TTL %s\n", path, FileUtils.byteCountToDisplaySize(Files.size(path)), minutesRemaining));
      } catch (final IOException e) {
        throw new RuntimeException(e);
      }
    });
    sb.append("---\n");
    LOGGER.info(sb.toString());
  }

}
