/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.helpers;

import com.google.api.client.util.Preconditions;
import com.google.api.gax.paging.Page;
import com.google.cloud.storage.Blob;
import com.google.cloud.storage.Blob.BlobSourceOption;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageOptions;
import com.google.common.collect.Lists;
import io.airbyte.commons.string.Strings;
import io.airbyte.config.EnvConfigs;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class GcsLogs implements CloudLogs {

  private static final Logger LOGGER = LoggerFactory.getLogger(GcsLogs.class);

  private static Storage GCS;

  @Override
  public File downloadCloudLog(LogConfigs configs, String logPath) throws IOException {
    return getFile(configs, logPath, LogClientSingleton.DEFAULT_PAGE_SIZE);
  }

  static File getFile(LogConfigs configs, String logPath, int pageSize) throws IOException {
    LOGGER.debug("Retrieving logs from GCS path: {}", logPath);
    createGcsClientIfNotExists(configs);

    LOGGER.debug("Start GCS list request.");
    Page<Blob> blobs = GCS.list(
        configs.getGcpStorageBucket(),
        Storage.BlobListOption.prefix(logPath),
        Storage.BlobListOption.pageSize(pageSize));

    var randomName = Strings.addRandomSuffix("logs", "-", 5);
    var tmpOutputFile = new File("/tmp/" + randomName);
    var os = new FileOutputStream(tmpOutputFile);
    LOGGER.debug("Start getting GCS objects.");
    // Objects are returned in lexicographical order.
    for (Blob blob : blobs.iterateAll()) {
      blob.downloadTo(os);
    }
    os.close();
    LOGGER.debug("Done retrieving GCS logs: {}.", logPath);
    return tmpOutputFile;
  }

  @Override
  public List<String> tailCloudLog(LogConfigs configs, String logPath, int numLines) throws IOException {
    LOGGER.debug("Tailing logs from GCS path: {}", logPath);
    createGcsClientIfNotExists(configs);

    LOGGER.debug("Start GCS list request.");
    Page<Blob> blobs = GCS.list(
        configs.getGcpStorageBucket(),
        Storage.BlobListOption.prefix(logPath));

    var ascendingTimestampBlobs = new ArrayList<Blob>();
    for (Blob blob : blobs.iterateAll()) {
      ascendingTimestampBlobs.add(blob);
    }
    var descendingTimestampBlobs = Lists.reverse(ascendingTimestampBlobs);

    var lines = new ArrayList<String>();
    int linesRead = 0;

    LOGGER.debug("Start getting GCS objects.");
    while (linesRead <= numLines && !descendingTimestampBlobs.isEmpty()) {
      var poppedBlob = descendingTimestampBlobs.remove(0);
      try (var inMemoryData = new ByteArrayOutputStream()) {
        poppedBlob.downloadTo(inMemoryData);
        var currFileLines = inMemoryData.toString().split("\n");
        List<String> currFileLinesReversed = Lists.reverse(List.of(currFileLines));
        for (var line : currFileLinesReversed) {
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
  public void deleteLogs(LogConfigs configs, String logPath) {
    LOGGER.debug("Retrieving logs from GCS path: {}", logPath);
    createGcsClientIfNotExists(configs);

    LOGGER.debug("Start GCS list and delete request.");
    Page<Blob> blobs = GCS.list(configs.getGcpStorageBucket(), Storage.BlobListOption.prefix(logPath));
    for (Blob blob : blobs.iterateAll()) {
      blob.delete(BlobSourceOption.generationMatch());
    }
    LOGGER.debug("Finished all deletes.");
  }

  private static void createGcsClientIfNotExists(LogConfigs configs) {
    if (GCS == null) {
      Preconditions.checkNotNull(configs.getGcpStorageBucket());
      Preconditions.checkNotNull(configs.getGoogleApplicationCredentials());

      GCS = StorageOptions.getDefaultInstance().getService();
    }
  }

  public static void main(String[] args) throws IOException {
    Storage storage = StorageOptions.getDefaultInstance().getService();
    var bucket = "davin-kube-logging-test";
    Page<Blob> blobs =
        storage.list(
            bucket,
            Storage.BlobListOption.prefix("app-logging/workspace/server/logs"),
            Storage.BlobListOption.pageSize(1));

    var randomName = Strings.addRandomSuffix("logs", "-", 5);
    var tmpOutputFile = new File("/tmp/" + randomName);
    var os = new FileOutputStream(tmpOutputFile);
    for (Blob blob : blobs.iterateAll()) {
      System.out.println(blob.getName());
      blob.downloadTo(os);
    }
    os.close();
    var data = new GcsLogs().tailCloudLog(new LogConfigDelegator(new EnvConfigs()), "tail", 6);
    System.out.println(data);
  }

}
