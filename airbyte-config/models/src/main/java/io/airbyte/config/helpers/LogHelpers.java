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

import io.airbyte.commons.io.IOs;
import io.airbyte.config.Configs;
import io.airbyte.config.Configs.WorkerEnvironment;
import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

public class LogHelpers {

  private static final Logger LOGGER = LoggerFactory.getLogger(LogHelpers.class);

  private static final int LOG_TAIL_SIZE = 1000000;
  private static final CloudLogs s3 = new S3Logs();

  // Any changes to the following values must also be propagated to the log4j2.xml in main/resources.
  public static String WORKSPACE_MDC_KEY = "workspace_app_root";
  public static String JOB_LOG_PATH_MDC_KEY = "job_log_path";

  public static String S3_LOG_BUCKET = "S3_LOG_BUCKET";
  public static String S3_LOG_BUCKET_REGION = "S3_LOG_BUCKET_REGION";
  public static String AWS_ACCESS_KEY_ID = "AWS_ACCESS_KEY_ID";
  public static String AWS_SECRET_ACCESS_KEY = "AWS_SECRET_ACCESS_KEY";
  public static String S3_MINIO_ENDPOINT = "S3_MINIO_ENDPOINT";

  public static String LOG_FILENAME = "logs.log";
  public static String APP_LOGGING_CLOUD_PREFIX = "app-logging";
  public static String JOB_LOGGING_CLOUD_PREFIX = "job-logging";

  public static boolean shouldUseLocalLogs(Configs configs) {
    return configs.getWorkerEnvironment().equals(WorkerEnvironment.DOCKER) || s3.hasEmptyConfigs(configs);
  }

  public static Path getServerLogsRoot(Configs configs) {
    return configs.getWorkspaceRoot().resolve("server/logs");
  }

  public static Path getSchedulerLogsRoot(Configs configs) {
    return configs.getWorkspaceRoot().resolve("scheduler/logs");
  }

  public static File getServerLogFile(Configs configs) {
    var logPathBase = getServerLogsRoot(configs);

    if (shouldUseLocalLogs(configs)) {
      return logPathBase.resolve(LOG_FILENAME).toFile();
    }
    var cloudLogPath = APP_LOGGING_CLOUD_PREFIX + logPathBase;
    try {
      return s3.downloadCloudLog(configs, cloudLogPath);
    } catch (IOException e) {
      throw new RuntimeException("Error retrieving log file: " + cloudLogPath + " from S3", e);
    }
  }

  public static File getSchedulerLogFile(Configs configs) {
    var logPathBase = getSchedulerLogsRoot(configs);

    if (shouldUseLocalLogs(configs)) {
      return logPathBase.resolve(LOG_FILENAME).toFile();
    }
    var cloudLogPath = APP_LOGGING_CLOUD_PREFIX + logPathBase;
    try {
      return s3.downloadCloudLog(configs, cloudLogPath);
    } catch (IOException e) {
      throw new RuntimeException("Error retrieving log file: " + cloudLogPath + " from S3", e);
    }
  }

  public static List<String> getJobLogFile(Configs configs, Path logPath) throws IOException {
    if (shouldUseLocalLogs(configs)) {
      return IOs.getTail(LOG_TAIL_SIZE, logPath);
    }

    var cloudLogPath = JOB_LOGGING_CLOUD_PREFIX + logPath;
    return s3.tailCloudLog(configs, cloudLogPath, LOG_TAIL_SIZE);
  }

  public static void setJobMdc(Path path) {
    MDC.put(LogHelpers.JOB_LOG_PATH_MDC_KEY, path.resolve(LogHelpers.LOG_FILENAME).toString());
  }

}
