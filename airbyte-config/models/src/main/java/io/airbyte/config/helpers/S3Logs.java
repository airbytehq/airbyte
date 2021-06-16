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

import io.airbyte.commons.string.Strings;
import io.airbyte.config.Configs;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
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
  public File downloadCloudLog(Configs configs, String logPath) {
    LOGGER.info("Retrieving logs from S3 path: {}", logPath);

    if (S3 == null) {
      checkValidCredentials(configs);
      var s3Region = configs.getS3LogBucketRegion();
      S3 = S3Client.builder().region(Region.of(s3Region)).build();
    }

    var s3Bucket = configs.getS3LogBucket();
    // Name? Make sure this location can be written to.
    var randomName = Strings.addRandomSuffix("logs", "-", 5);
    var tmpOutputFile = new File("/tmp/" + randomName);
    try {
      var os = new FileOutputStream(tmpOutputFile);

      var listObjReq = ListObjectsV2Request.builder().bucket(s3Bucket).prefix(logPath).build();
      LOGGER.info("Done making S3 list request.");
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
    } catch (IOException e) {
      throw new RuntimeException("Error retrieving log file: " + logPath + " from S3", e);
    }
    LOGGER.info("Done retrieving S3 logs: {}.", logPath);
    return tmpOutputFile;
  }

}
