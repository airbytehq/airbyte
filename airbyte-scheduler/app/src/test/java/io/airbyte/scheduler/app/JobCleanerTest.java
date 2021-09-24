/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.app;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.config.WorkspaceRetentionConfig;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobStatus;
import io.airbyte.scheduler.persistence.JobPersistence;
import java.io.File;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

class JobCleanerTest {

  @TempDir
  Path folder;

  @Test
  public void testNotDeletingFilesInMinimum() throws IOException {
    createFile(folder.resolve("1"), "A", 1, 10);

    final JobPersistence jobPersistence = mock(JobPersistence.class);

    final JobCleaner jobCleaner = new JobCleaner(
        new WorkspaceRetentionConfig(20, 30, 0),
        folder,
        jobPersistence);

    final Set<String> before = listFiles(folder);
    jobCleaner.run();
    final Set<String> after = listFiles(folder);

    assertFalse(before.isEmpty());
    assertEquals(before, after);
  }

  @Test
  public void testDeletingOldFiles() throws IOException {
    createFile(folder.resolve("1"), "A", 1, 100);

    final JobPersistence jobPersistence = mock(JobPersistence.class);

    final JobCleaner jobCleaner = new JobCleaner(
        new WorkspaceRetentionConfig(20, 30, 0),
        folder,
        jobPersistence);

    final Set<String> before = listFiles(folder);
    jobCleaner.run();
    final Set<String> after = listFiles(folder);

    final Set<String> expected = Set.of("");

    assertFalse(before.isEmpty());
    assertEquals(expected, after);
  }

  @Test
  public void testDeletingLargeFiles() throws IOException {
    createFile(folder.resolve("1"), "A", 1, 10);
    createFile(folder.resolve("1"), "B", 1, 10);
    createFile(folder.resolve("1"), "C", 1, 10);
    createFile(folder.resolve("2"), "D", 1, 18);
    createFile(folder.resolve("2"), "E", 1, 19);
    createFile(folder.resolve("2"), "F", 1, 20);

    final JobPersistence jobPersistence = mock(JobPersistence.class);

    final JobCleaner jobCleaner = new JobCleaner(
        new WorkspaceRetentionConfig(1, 30, 4),
        folder,
        jobPersistence);

    jobCleaner.run();
    final Set<String> after = listFiles(folder);
    final Set<String> expected = Set.of("", "/1", "/1/A", "/1/B", "/1/C", "/2", "/2/D");

    assertEquals(expected, after);
  }

  @Test
  public void testNotDeletingRunning() throws IOException {
    createFile(folder.resolve("1"), "A", 1, 10);
    createFile(folder.resolve("1"), "B", 1, 10);
    createFile(folder.resolve("1"), "C", 1, 10);
    createFile(folder.resolve("2"), "D", 1, 18);
    createFile(folder.resolve("2"), "E", 1, 19);
    createFile(folder.resolve("2"), "F", 1, 20);

    final JobPersistence jobPersistence = mock(JobPersistence.class);
    Job job2 = mock(Job.class);
    when(job2.getId()).thenReturn(2L);
    when(jobPersistence.listJobsWithStatus(JobStatus.RUNNING)).thenReturn(List.of(job2));

    final JobCleaner jobCleaner = new JobCleaner(
        new WorkspaceRetentionConfig(1, 30, 0),
        folder,
        jobPersistence);

    jobCleaner.run();
    final Set<String> after = listFiles(folder);
    final Set<String> expected = Set.of("", "/2", "/2/D", "/2/E", "/2/F");

    assertEquals(expected, after);
  }

  private void createFile(Path subdirectory, String filename, int sizeMb, int daysAgo) throws IOException {
    long lastModified = JobCleaner.getDateFromDaysAgo(daysAgo).getTime();
    File subdirFile = subdirectory.toFile();
    if (!subdirFile.exists()) {
      subdirFile.mkdir();
      subdirFile.setLastModified(lastModified);
    }

    File file = subdirectory.resolve(filename).toFile();
    file.createNewFile();

    RandomAccessFile raf = new RandomAccessFile(file, "rw");
    raf.setLength(sizeMb * 1024 * 1024);
    raf.close();

    file.setLastModified(lastModified);
  }

  private Set<String> listFiles(Path dir) throws IOException {
    return Files.walk(dir).map(Path::toString).map(x -> x.replace(folder.toString(), "")).collect(Collectors.toSet());
  }

}
