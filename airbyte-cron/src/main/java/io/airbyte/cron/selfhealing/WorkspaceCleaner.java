/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cron.selfhealing;

import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.micronaut.scheduling.annotation.Scheduled;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.util.Date;
import java.util.concurrent.atomic.AtomicInteger;
import javax.inject.Singleton;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.FileUtils;
import org.apache.commons.io.filefilter.AgeFileFilter;

@Singleton
@Slf4j
public class WorkspaceCleaner {

  private final Path workspaceRoot;
  private final long maxAgeFilesInDays;

  WorkspaceCleaner() {
    // TODO Configs should get injected through micronaut
    final Configs configs = new EnvConfigs();

    this.workspaceRoot = configs.getWorkspaceRoot();
    // We align max file age on temporal for history consistency
    // It might make sense configure this independently in the future
    this.maxAgeFilesInDays = configs.getTemporalRetentionInDays();
  }

  /*
   * Delete files older than maxAgeFilesInDays from the workspace
   *
   * NOTE: this is currently only intended to work for docker
   */
  @Scheduled(fixedRate = "1d")
  public void deleteOldFiles() throws IOException {
    final Date oldestAllowed = getDateFromDaysAgo(maxAgeFilesInDays);
    log.info("Deleting files older than {} days ({})", maxAgeFilesInDays, oldestAllowed);

    final AtomicInteger counter = new AtomicInteger(0);
    Files.walk(workspaceRoot)
        .map(Path::toFile)
        .filter(f -> new AgeFileFilter(oldestAllowed).accept(f))
        .forEach(file -> {
          log.debug("Deleting file: " + file.toString());
          FileUtils.deleteQuietly(file);
          counter.incrementAndGet();
          final File parentDir = file.getParentFile();
          if (parentDir.isDirectory() && parentDir.listFiles().length == 0) {
            FileUtils.deleteQuietly(parentDir);
          }
        });
    log.info("deleted {} files", counter.get());
  }

  private static Date getDateFromDaysAgo(final long daysAgo) {
    return Date.from(LocalDateTime.now().minusDays(daysAgo).toInstant(OffsetDateTime.now().getOffset()));
  }

}
