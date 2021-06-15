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

import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import io.airbyte.config.Configs;
import io.airbyte.config.Configs.WorkerEnvironment;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.file.Path;
import java.util.stream.Collectors;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.model.ListObjectsRequest;

public class LogHelpers {

  // if you update these values, you must also update log4j2.xml
  public static String WORKSPACE_MDC_KEY = "workspace_app_root";
  public static String LOG_FILENAME = "logs.log";
  public static String S3_LOG_BUCKET = "S3_LOG_BUCKET";
  public static String S3_LOG_BUCKET_REGION = "S3_LOG_BUCKET_REGION";
  public static String S3_AWS_KEY = "S3_AWS_KEY";
  public static String S3_AWS_SECRET = "S3_AWS_SECRET";

  public static Path getServerLogsRoot(Configs configs) {
    return configs.getWorkspaceRoot().resolve("server/logs");
  }

  public static Path getSchedulerLogsRoot(Configs configs) {
    return configs.getWorkspaceRoot().resolve("scheduler/logs");
  }

  public static File getServerLogFile(Configs configs) {
    var logPath = getServerLogsRoot(configs).resolve(LOG_FILENAME);

    if (configs.getWorkerEnvironment().equals(WorkerEnvironment.KUBERNETES)) {
      var s3Bucket = configs.getS3LogBucket();
      var s3Region = configs.getS3LogBucketRegion();

      var credentials = new BasicAWSCredentials(
          configs.getS3AwsKey(),
          configs.getS3AwsSecret()
      );
      var s3client = AmazonS3ClientBuilder
          .standard()
          .withCredentials(new AWSStaticCredentialsProvider(credentials))
          .withRegion(Regions.fromName(s3Region))
          .build();

      // list all the files
      var summaries = s3client.listObjects(s3Bucket, logPath.toString()).getObjectSummaries();
      var sortedSummaries =
          summaries.stream()
              .sorted((o1, o2) -> o1.getLastModified().compareTo(o2.getLastModified()))
              .collect(Collectors.toList());

      // get all the files and combine them in order
    }

    return logPath.toFile();
  }

  public static File getSchedulerLogFile(Configs configs) {
    return getSchedulerLogsRoot(configs).resolve(LOG_FILENAME).toFile();
  }

  public static void main(String[] args) throws IOException {
    var s3Bucket = "davin-kube-logging-test-bucket";
    var s3Region = "us-west-2";

    var s3client = S3Client.builder().region(Region.of(s3Region)).build();

    // Name? Make sure this location can be written to.
    var tmpOutputFile = new File("/tmp/scheduler.log");
    var os = new FileOutputStream(tmpOutputFile);

    // TODO: Make sure we iterate through all the files here.
    var listObjReq = ListObjectsRequest.builder().bucket(s3Bucket).prefix("app-logging/tmp/workspace/scheduler/logs/").build();
    var summaries = s3client.listObjects(listObjReq).contents();
    for (var summary: summaries) {

      var getObjReq = GetObjectRequest.builder()
          .key(summary.key())
          .bucket(s3Bucket)
          .build();
      var data = s3client.getObjectAsBytes(getObjReq).asByteArray();
      os.write(data);
    }
    os.close();
  }
}
