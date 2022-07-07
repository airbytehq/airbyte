/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.helpers;

import com.google.api.gax.paging.Page;
import com.google.cloud.storage.Blob;
import com.google.cloud.storage.Blob.BlobSourceOption;
import com.google.cloud.storage.Storage;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Lists;
import io.airbyte.commons.string.Strings;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@SuppressWarnings({"PMD.AvoidFileStream", "PMD.ShortVariable", "PMD.CloseResource", "PMD.AvoidInstantiatingObjectsInLoops"})
public class GcsLogs implements CloudLogs {

  private static final Logger LOGGER = LoggerFactory.getLogger(GcsLogs.class);

  private static Storage gcs;
  private final Supplier<Storage> gcsClientFactory;

  public GcsLogs(final Supplier<Storage> gcsClientFactory) {
    this.gcsClientFactory = gcsClientFactory;
  }

  @Override
  public File downloadCloudLog(final LogConfigs configs, final String logPath) throws IOException {
    return getFile(configs, logPath, LogClientSingleton.DEFAULT_PAGE_SIZE);
  }

  private File getFile(final LogConfigs configs, final String logPath, final int pageSize) throws IOException {
    return getFile(getOrCreateGcsClient(), configs, logPath, pageSize);
  }

  @VisibleForTesting
  static File getFile(final Storage gcsClient, final LogConfigs configs, final String logPath, final int pageSize) throws IOException {
    LOGGER.debug("Retrieving logs from GCS path: {}", logPath);

    LOGGER.debug("Start GCS list request.");
    final Page<Blob> blobs = gcsClient.list(
        configs.getStorageConfigs().getGcsConfig().getBucketName(),
        Storage.BlobListOption.prefix(logPath),
        Storage.BlobListOption.pageSize(pageSize));

    final var randomName = Strings.addRandomSuffix("logs", "-", 5);
    final var tmpOutputFile = new File("/tmp/" + randomName);
    final var os = new FileOutputStream(tmpOutputFile);
    LOGGER.debug("Start getting GCS objects.");
    // Objects are returned in lexicographical order.
    for (final Blob blob : blobs.iterateAll()) {
      blob.downloadTo(os);
    }
    os.close();
    LOGGER.debug("Done retrieving GCS logs: {}.", logPath);
    return tmpOutputFile;
  }

  @Override
  public List<String> tailCloudLog(final LogConfigs configs, final String logPath, final int numLines) throws IOException {
    LOGGER.debug("Tailing logs from GCS path: {}", logPath);
    final Storage gcsClient = getOrCreateGcsClient();

    LOGGER.debug("Start GCS list request.");

    final Page<Blob> blobs = gcsClient.list(
        configs.getStorageConfigs().getGcsConfig().getBucketName(),
        Storage.BlobListOption.prefix(logPath));

    final var ascendingTimestampBlobs = new ArrayList<Blob>();
    for (final Blob blob : blobs.iterateAll()) {
      ascendingTimestampBlobs.add(blob);
    }
    final var descendingTimestampBlobs = Lists.reverse(ascendingTimestampBlobs);

    final var lines = new ArrayList<String>();
    int linesRead = 0;

    LOGGER.debug("Start getting GCS objects.");
    while (linesRead <= numLines && !descendingTimestampBlobs.isEmpty()) {
      final var poppedBlob = descendingTimestampBlobs.remove(0);
      try (final var inMemoryData = new ByteArrayOutputStream()) {
        poppedBlob.downloadTo(inMemoryData);
        final var currFileLines = inMemoryData.toString(StandardCharsets.UTF_8).split("\n");
        final List<String> currFileLinesReversed = Lists.reverse(List.of(currFileLines));
        for (final var line : currFileLinesReversed) {
          if (linesRead == numLines) {
            break;
          }
          lines.add(0, line);
          linesRead++;
        }
      }
    }

    LOGGER.debug("Done retrieving GCS logs: {}.", logPath);
    return lines;
  }

  @Override
  public void deleteLogs(final LogConfigs configs, final String logPath) {
    LOGGER.debug("Retrieving logs from GCS path: {}", logPath);
    final Storage gcsClient = getOrCreateGcsClient();

    LOGGER.debug("Start GCS list and delete request.");
    final Page<Blob> blobs = gcsClient.list(configs.getStorageConfigs().getGcsConfig().getBucketName(), Storage.BlobListOption.prefix(logPath));
    for (final Blob blob : blobs.iterateAll()) {
      blob.delete(BlobSourceOption.generationMatch());
    }
    LOGGER.debug("Finished all deletes.");
  }

  private Storage getOrCreateGcsClient() {
    if (gcs == null) {
      gcs = gcsClientFactory.get();
    }
    return gcs;
  }

}
