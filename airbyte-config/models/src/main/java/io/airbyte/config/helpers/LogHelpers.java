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
import io.airbyte.config.Configs.WorkerEnvironment;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.file.Path;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.model.ListObjectsV2Request;

public class LogHelpers {

  private static final Logger LOGGER = LoggerFactory.getLogger(LogHelpers.class);

  // Any changes to the following values must also be propagated to the log4j2.xml in main/resources.
  public static String WORKSPACE_MDC_KEY = "workspace_app_root";
  public static String LOG_FILENAME = "logs.log";
  public static String S3_LOG_BUCKET = "S3_LOG_BUCKET";
  public static String S3_LOG_BUCKET_REGION = "S3_LOG_BUCKET_REGION";
  public static String AWS_ACCESS_KEY_ID = "AWS_ACCESS_KEY_ID";
  public static String AWS_SECRET_ACCESS_KEY = "AWS_SECRET_ACCESS_KEY";

  public static String APP_LOGGING_CLOUD_PREFIX = "app-logging";
  public static String JOB_LOGGING_CLOUD_PREFIX = "job-logging";

  public static Path getServerLogsRoot(Configs configs) {
    return configs.getWorkspaceRoot().resolve("server/logs");
  }

  public static Path getSchedulerLogsRoot(Configs configs) {
    return configs.getWorkspaceRoot().resolve("scheduler/logs");
  }

  public static File getServerLogFile(Configs configs) {
    var logPathBase = getServerLogsRoot(configs);

    if (configs.getWorkerEnvironment().equals(WorkerEnvironment.DOCKER)) {
      var cloudLogPath = APP_LOGGING_CLOUD_PREFIX + logPathBase;
      return downloadCloudLog(configs, cloudLogPath);
    }

    return logPathBase.resolve(LOG_FILENAME).toFile();
  }

  public static File getSchedulerLogFile(Configs configs) {
    var logPathBase = getSchedulerLogsRoot(configs);

    if (configs.getWorkerEnvironment().equals(WorkerEnvironment.DOCKER)) {
      var cloudLogPath = APP_LOGGING_CLOUD_PREFIX + logPathBase;

      return downloadCloudLog(configs, cloudLogPath);
    }

    return logPathBase.resolve(LOG_FILENAME).toFile();
  }

  private static File downloadCloudLog(Configs configs, String logPath) {
    LOGGER.info("Retrieving logs from cloud path: {}", logPath);

    var s3Bucket = configs.getS3LogBucket();
    var s3Region = configs.getS3LogBucketRegion();

    var s3client = S3Client.builder().region(Region.of(s3Region)).build();

    // Name? Make sure this location can be written to.
    var randomName = Strings.addRandomSuffix("logs", "-", 5);
    var tmpOutputFile = new File("/tmp/" + randomName);
    try {
      var os = new FileOutputStream(tmpOutputFile);

      var listObjReq = ListObjectsV2Request.builder().bucket(s3Bucket).prefix(logPath).build();
      LOGGER.info("Done making cloud storage list request.");
      for (var page : s3client.listObjectsV2Paginator(listObjReq)) {
        for (var objMetadata : page.contents()) {
          var getObjReq = GetObjectRequest.builder()
              .key(objMetadata.key())
              .bucket(s3Bucket)
              .build();
          var data = s3client.getObjectAsBytes(getObjReq).asByteArray();
          os.write(data);
        }
      }
      os.close();
    } catch (IOException e) {
      throw new RuntimeException("Error retrieving log file: " + logPath + " from cloud", e);
    }
    LOGGER.info("Done retrieving logs from cloud.");
    return tmpOutputFile;
  }

  public static void main(String[] args) throws IOException {}

}
