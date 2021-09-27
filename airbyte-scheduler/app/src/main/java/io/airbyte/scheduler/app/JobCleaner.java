/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.app;

import com.google.common.collect.Sets;
import io.airbyte.config.WorkspaceRetentionConfig;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobStatus;
import io.airbyte.scheduler.persistence.JobPersistence;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.BasicFileAttributes;
import java.nio.file.attribute.FileTime;
import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.util.Date;
import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;
import org.apache.commons.io.FileUtils;
import org.apache.commons.io.filefilter.AgeFileFilter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * The job cleaner is responsible for limiting the retention of files in the workspace root. It does
 * this in two ways. 1. It cleans out all files and directories that are older than the maximum
 * retention date. 2. It cleans out the oldest files before the minimum retention date until it is
 * within the max workspace size.
 */
public class JobCleaner implements Runnable {

  private static final Logger LOGGER = LoggerFactory.getLogger(JobCleaner.class);

  private final Path workspaceRoot;
  private final JobPersistence jobPersistence;

  private final WorkspaceRetentionConfig config;

  public JobCleaner(WorkspaceRetentionConfig config,
                    Path workspaceRoot,
                    JobPersistence jobPersistence) {
    this.config = config;
    this.workspaceRoot = workspaceRoot;
    this.jobPersistence = jobPersistence;
  }

  @Override
  public void run() {
    try {
      deleteOldFiles();
      deleteOnSize();
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  private void deleteOldFiles() throws IOException {
    final Date oldestAllowed = getDateFromDaysAgo(config.getMaxDays());

    Files.walk(workspaceRoot)
        .map(Path::toFile)
        .filter(f -> new AgeFileFilter(oldestAllowed).accept(f))
        .forEach(file -> {
          LOGGER.info("Deleting old file: " + file.toString());
          FileUtils.deleteQuietly(file);

          File parentDir = file.getParentFile();
          if (parentDir.isDirectory() && parentDir.listFiles().length == 0) {
            FileUtils.deleteQuietly(parentDir);
          }
        });
  }

  private void deleteOnSize() throws IOException {
    Set<String> nonTerminalJobIds = new HashSet<>();
    Sets.SetView<JobStatus> nonTerminalStatuses = Sets.difference(Set.of(JobStatus.values()), JobStatus.TERMINAL_STATUSES);

    for (JobStatus nonTerminalStatus : nonTerminalStatuses) {
      Set<String> jobIds = jobPersistence.listJobsWithStatus(nonTerminalStatus)
          .stream()
          .map(Job::getId)
          .map(String::valueOf)
          .collect(Collectors.toSet());

      nonTerminalJobIds.addAll(jobIds);
    }

    final Date youngestAllowed = getDateFromDaysAgo(config.getMinDays());

    final long workspaceBytes = FileUtils.sizeOfDirectory(workspaceRoot.toFile());
    AtomicLong deletedBytes = new AtomicLong(0);
    final AgeFileFilter ageFilter = new AgeFileFilter(youngestAllowed);
    Files.walk(workspaceRoot)
        .map(Path::toFile)
        .filter(f -> {
          Path relativePath = workspaceRoot.relativize(f.toPath());

          // if the directory is ID/something instead of just ID, get just the ID
          if (relativePath.getParent() != null) {
            relativePath = workspaceRoot.relativize(f.toPath()).getParent();
          }

          if (!relativePath.toString().equals("")) {
            return !nonTerminalJobIds.contains(relativePath.toString());
          } else {
            return true;
          }
        })
        .filter(ageFilter::accept)
        .sorted((o1, o2) -> {
          FileTime ft1 = getFileTime(o1);
          FileTime ft2 = getFileTime(o2);
          return ft1.compareTo(ft2);
        })
        .forEach(fileToDelete -> {
          if (workspaceBytes - deletedBytes.get() > config.getMaxSizeMb() * 1024 * 1024) {
            long sizeToDelete = fileToDelete.length();
            deletedBytes.addAndGet(sizeToDelete);
            LOGGER.info("Deleting: " + fileToDelete.toString());
            FileUtils.deleteQuietly(fileToDelete);

            File parentDir = fileToDelete.getParentFile();
            if (parentDir.isDirectory() && parentDir.listFiles().length == 0) {
              FileUtils.deleteQuietly(parentDir);
            }
          }
        });
  }

  protected static Date getDateFromDaysAgo(long daysAgo) {
    return Date.from(LocalDateTime.now().minusDays(daysAgo).toInstant(OffsetDateTime.now().getOffset()));
  }

  private static FileTime getFileTime(File file) {
    try {
      return Files.readAttributes(file.toPath(), BasicFileAttributes.class).creationTime();
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

}
