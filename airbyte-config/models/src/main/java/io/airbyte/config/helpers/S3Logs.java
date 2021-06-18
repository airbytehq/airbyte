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

import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Lists;
import io.airbyte.commons.string.Strings;
import io.airbyte.config.Configs;
import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.model.ListObjectsV2Request;

public class S3Logs implements CloudLogs {

  private static final Logger LOGGER = LoggerFactory.getLogger(S3Logs.class);

  private static S3Client S3;

  private static void checkValidCredentials(Configs configs) {
    configs.getAwsAccessKey();
    configs.getAwsSecretAccessKey();
    configs.getS3LogBucketRegion();
    configs.getS3LogBucket();
  }

  @Override
  public File downloadCloudLog(Configs configs, String logPath) throws IOException {
    return getFile(configs, logPath, 1000);
  }

  @VisibleForTesting
  File getFile(Configs configs, String logPath, int maxKeysPerPage) throws IOException {
    LOGGER.info("Retrieving logs from S3 path: {}", logPath);
    createS3ClientIfNotExist(configs);

    var s3Bucket = configs.getS3LogBucket();
    var randomName = Strings.addRandomSuffix("logs", "-", 5);
    var tmpOutputFile = new File("/tmp/" + randomName);
    var os = new FileOutputStream(tmpOutputFile);

    LOGGER.info("Start S3 list request.");
    var listObjReq = ListObjectsV2Request.builder().bucket(s3Bucket)
        .prefix(logPath).maxKeys(maxKeysPerPage).build();
    LOGGER.info("Start getting S3 objects.");
    // Objects are returned in lexicographical order.
    for (var page : S3.listObjectsV2Paginator(listObjReq)) {
      for (var objMetadata : page.contents()) {
        var getObjReq = GetObjectRequest.builder()
            .key(objMetadata.key())
            .bucket(s3Bucket)
            .build();
        var data = S3.getObjectAsBytes(getObjReq).asByteArray();
        os.write(data);
      }
    }
    os.close();

    LOGGER.info("Done retrieving S3 logs: {}.", logPath);
    return tmpOutputFile;
  }

  @Override
  public List<String> tailCloudLog(Configs configs, String logPath, int numLines) throws IOException {
    LOGGER.info("Tailing logs from S3 path: {}", logPath);
    createS3ClientIfNotExist(configs);

    var s3Bucket = configs.getS3LogBucket();
    LOGGER.info("Start making S3 list request.");
    ArrayList<String> ascendingTimestampKeys = getAscendingObjectKeys(logPath, s3Bucket);
    var descendingTimestampKeys = Lists.reverse(ascendingTimestampKeys);

    var lines = new ArrayList<String>();
    int linesRead = 0;

    LOGGER.info("Start getting S3 objects.");
    while (linesRead <= numLines && !descendingTimestampKeys.isEmpty()) {
      var poppedKey = descendingTimestampKeys.remove(0);
      List<String> currFileLinesReversed = Lists.reverse(getCurrFile(s3Bucket, poppedKey));
      for (var line : currFileLinesReversed) {
        if (linesRead == numLines) {
          break;
        }
        lines.add(0, line);
        linesRead++;
      }
    }

    LOGGER.info("Done retrieving S3 logs: {}.", logPath);
    return lines;
  }

  private void createS3ClientIfNotExist(Configs configs) {
    if (S3 == null) {
      checkValidCredentials(configs);
      var s3Region = configs.getS3LogBucketRegion();
      S3 = S3Client.builder().region(Region.of(s3Region)).build();
    }
  }

  private ArrayList<String> getAscendingObjectKeys(String logPath, String s3Bucket) {
    var listObjReq = ListObjectsV2Request.builder().bucket(s3Bucket).prefix(logPath).build();
    var ascendingTimestampObjs = new ArrayList<String>();

    // Objects are returned in lexicographical order.
    for (var page : S3.listObjectsV2Paginator(listObjReq)) {
      for (var objMetadata : page.contents()) {
        ascendingTimestampObjs.add(objMetadata.key());
      }
    }
    return ascendingTimestampObjs;
  }

  private static ArrayList<String> getCurrFile(String s3Bucket, String poppedKey) throws IOException {
    var getObjReq = GetObjectRequest.builder()
        .key(poppedKey)
        .bucket(s3Bucket)
        .build();

    var data = S3.getObjectAsBytes(getObjReq).asByteArray();
    var is = new ByteArrayInputStream(data);
    var currentFileLines = new ArrayList<String>();
    try (var reader = new BufferedReader(new InputStreamReader(is))) {
      String temp;
      while ((temp = reader.readLine()) != null) {
        currentFileLines.add(temp);
      }
    }
    return currentFileLines;
  }

}
