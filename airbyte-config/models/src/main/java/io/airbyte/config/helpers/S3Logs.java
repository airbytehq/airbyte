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

package io.airbyte.config.helpers;

import com.google.api.client.util.Preconditions;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Lists;
import io.airbyte.commons.string.Strings;
import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.Delete;
import software.amazon.awssdk.services.s3.model.DeleteObjectsRequest;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.model.ListObjectsV2Request;
import software.amazon.awssdk.services.s3.model.ObjectIdentifier;

public class S3Logs implements CloudLogs {

  private static final Logger LOGGER = LoggerFactory.getLogger(S3Logs.class);

  private static S3Client S3;

  private static void assertValidS3Configuration(final LogConfigs configs) {
    Preconditions.checkNotNull(configs.getAwsAccessKey());
    Preconditions.checkNotNull(configs.getAwsSecretAccessKey());
    Preconditions.checkNotNull(configs.getS3LogBucketRegion());
    Preconditions.checkNotNull(configs.getS3LogBucket());
  }

  @Override
  public File downloadCloudLog(final LogConfigs configs, final String logPath) throws IOException {
    return getFile(configs, logPath, LogClientSingleton.DEFAULT_PAGE_SIZE);
  }

  @VisibleForTesting
  static File getFile(final LogConfigs configs, final String logPath, final int pageSize) throws IOException {
    LOGGER.debug("Retrieving logs from S3 path: {}", logPath);
    createS3ClientIfNotExist(configs);

    final var s3Bucket = configs.getS3LogBucket();
    final var randomName = Strings.addRandomSuffix("logs", "-", 5);
    final var tmpOutputFile = new File("/tmp/" + randomName);
    final var os = new FileOutputStream(tmpOutputFile);

    LOGGER.debug("Start S3 list request.");
    final var listObjReq = ListObjectsV2Request.builder().bucket(s3Bucket)
        .prefix(logPath).maxKeys(pageSize).build();
    LOGGER.debug("Start getting S3 objects.");
    // Objects are returned in lexicographical order.
    for (final var page : S3.listObjectsV2Paginator(listObjReq)) {
      for (final var objMetadata : page.contents()) {
        final var getObjReq = GetObjectRequest.builder()
            .key(objMetadata.key())
            .bucket(s3Bucket)
            .build();
        final var data = S3.getObjectAsBytes(getObjReq).asByteArray();
        os.write(data);
      }
    }
    os.close();

    LOGGER.debug("Done retrieving S3 logs: {}.", logPath);
    return tmpOutputFile;
  }

  @Override
  public List<String> tailCloudLog(final LogConfigs configs, final String logPath, final int numLines) throws IOException {
    LOGGER.debug("Tailing logs from S3 path: {}", logPath);
    createS3ClientIfNotExist(configs);

    final var s3Bucket = configs.getS3LogBucket();
    LOGGER.debug("Start making S3 list request.");
    final ArrayList<String> ascendingTimestampKeys = getAscendingObjectKeys(logPath, s3Bucket);
    final var descendingTimestampKeys = Lists.reverse(ascendingTimestampKeys);

    final var lines = new ArrayList<String>();
    int linesRead = 0;

    LOGGER.debug("Start getting S3 objects.");
    while (linesRead <= numLines && !descendingTimestampKeys.isEmpty()) {
      final var poppedKey = descendingTimestampKeys.remove(0);
      final List<String> currFileLinesReversed = Lists.reverse(getCurrFile(s3Bucket, poppedKey));
      for (final var line : currFileLinesReversed) {
        if (linesRead == numLines) {
          break;
        }
        lines.add(0, line);
        linesRead++;
      }
    }

    LOGGER.debug("Done retrieving S3 logs: {}.", logPath);
    return lines;
  }

  @Override
  public void deleteLogs(final LogConfigs configs, final String logPath) {
    LOGGER.debug("Deleting logs from S3 path: {}", logPath);
    createS3ClientIfNotExist(configs);

    final var keys = getAscendingObjectKeys(logPath, configs.getS3LogBucket())
        .stream().map(key -> ObjectIdentifier.builder().key(key).build())
        .collect(Collectors.toList());
    final Delete del = Delete.builder()
        .objects(keys)
        .build();
    final DeleteObjectsRequest multiObjectDeleteRequest = DeleteObjectsRequest.builder()
        .bucket(configs.getS3LogBucket())
        .delete(del)
        .build();

    S3.deleteObjects(multiObjectDeleteRequest);
    LOGGER.debug("Multiple objects are deleted!");
  }

  private static void createS3ClientIfNotExist(final LogConfigs configs) {
    if (S3 == null) {
      assertValidS3Configuration(configs);
      final var s3Region = configs.getS3LogBucketRegion();
      final var builder = S3Client.builder().region(Region.of(s3Region));

      final var minioEndpoint = configs.getS3MinioEndpoint();
      if (!minioEndpoint.isBlank()) {
        try {
          final var minioUri = new URI(minioEndpoint);
          builder.endpointOverride(minioUri);
        } catch (final URISyntaxException e) {
          throw new RuntimeException("Error creating S3 log client to Minio", e);
        }
      }

      S3 = builder.build();
    }
  }

  private ArrayList<String> getAscendingObjectKeys(final String logPath, final String s3Bucket) {
    final var listObjReq = ListObjectsV2Request.builder().bucket(s3Bucket).prefix(logPath).build();
    final var ascendingTimestampObjs = new ArrayList<String>();

    // Objects are returned in lexicographical order.
    for (final var page : S3.listObjectsV2Paginator(listObjReq)) {
      for (final var objMetadata : page.contents()) {
        ascendingTimestampObjs.add(objMetadata.key());
      }
    }
    return ascendingTimestampObjs;
  }

  private static ArrayList<String> getCurrFile(final String s3Bucket, final String poppedKey) throws IOException {
    final var getObjReq = GetObjectRequest.builder()
        .key(poppedKey)
        .bucket(s3Bucket)
        .build();

    final var data = S3.getObjectAsBytes(getObjReq).asByteArray();
    final var is = new ByteArrayInputStream(data);
    final var currentFileLines = new ArrayList<String>();
    try (final var reader = new BufferedReader(new InputStreamReader(is))) {
      String temp;
      while ((temp = reader.readLine()) != null) {
        currentFileLines.add(temp);
      }
    }
    return currentFileLines;
  }

}
