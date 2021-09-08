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
import io.airbyte.commons.io.IOs;
import io.airbyte.config.Configs;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.EnvConfigs;
import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import org.apache.commons.lang3.NotImplementedException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

/**
 * Airbyte's logging layer entrypoint. Handles logs written to local disk as well as logs written to
 * cloud storages.
 *
 * Although the configuration is passed in as {@link Configs}, it is transformed to
 * {@link LogConfigs} within this class. Beyond this class, all configuration consumption is via the
 * {@link LogConfigs} interface via the {@link CloudLogs} interface.
 */
public class LogClientSingleton {

  private static final Logger LOGGER = LoggerFactory.getLogger(LogClientSingleton.class);

  private static final int LOG_TAIL_SIZE = 1000000;
  private static CloudLogs logClient;

  // Any changes to the following values must also be propagated to the log4j2.xml in main/resources.
  public static String WORKSPACE_MDC_KEY = "workspace_app_root";
  public static String CLOUD_WORKSPACE_MDC_KEY = "cloud_workspace_app_root";

  public static String JOB_LOG_PATH_MDC_KEY = "job_log_path";
  public static String CLOUD_JOB_LOG_PATH_MDC_KEY = "cloud_job_log_path";

  // S3/Minio
  public static String S3_LOG_BUCKET = "S3_LOG_BUCKET";
  public static String S3_LOG_BUCKET_REGION = "S3_LOG_BUCKET_REGION";
  public static String AWS_ACCESS_KEY_ID = "AWS_ACCESS_KEY_ID";
  public static String AWS_SECRET_ACCESS_KEY = "AWS_SECRET_ACCESS_KEY";
  public static String S3_MINIO_ENDPOINT = "S3_MINIO_ENDPOINT";

  // GCS
  public static String GCP_STORAGE_BUCKET = "GCP_STORAGE_BUCKET";
  public static String GOOGLE_APPLICATION_CREDENTIALS = "GOOGLE_APPLICATION_CREDENTIALS";

  public static int DEFAULT_PAGE_SIZE = 1000;
  public static String LOG_FILENAME = "logs.log";
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
    if (shouldUseLocalLogs(configs)) {
      return logPathBase.resolve(LOG_FILENAME).toFile();
    }

    var logConfigs = new LogConfigDelegator(configs);
    createCloudClientIfNull(logConfigs);
    var cloudLogPath = APP_LOGGING_CLOUD_PREFIX + logPathBase;
    try {
      return logClient.downloadCloudLog(logConfigs, cloudLogPath);
    } catch (IOException e) {
      throw new RuntimeException("Error retrieving log file: " + cloudLogPath + " from S3", e);
    }
  }

  public static File getSchedulerLogFile(Configs configs) {
    var logPathBase = getSchedulerLogsRoot(configs);
    if (shouldUseLocalLogs(configs)) {
      return logPathBase.resolve(LOG_FILENAME).toFile();
    }

    var logConfigs = new LogConfigDelegator(configs);
    createCloudClientIfNull(logConfigs);
    var cloudLogPath = APP_LOGGING_CLOUD_PREFIX + logPathBase;
    try {
      return logClient.downloadCloudLog(logConfigs, cloudLogPath);
    } catch (IOException e) {
      throw new RuntimeException("Error retrieving log file: " + cloudLogPath + " from S3", e);
    }
  }

  public static List<String> getJobLogFile(Configs configs, Path logPath) throws IOException {
    if (shouldUseLocalLogs(configs)) {
      return IOs.getTail(LOG_TAIL_SIZE, logPath);
    }

    var logConfigs = new LogConfigDelegator(configs);
    createCloudClientIfNull(logConfigs);
    var cloudLogPath = JOB_LOGGING_CLOUD_PREFIX + logPath;
    return logClient.tailCloudLog(logConfigs, cloudLogPath, LOG_TAIL_SIZE);
  }

  /**
   * Primarily to clean up logs after testing. Only valid for Kube logs.
   */
  @VisibleForTesting
  public static void deleteLogs(Configs configs, String logPath) {
    if (shouldUseLocalLogs(configs)) {
      throw new NotImplementedException("Local log deletes not supported.");
    }
    var logConfigs = new LogConfigDelegator(configs);
    createCloudClientIfNull(logConfigs);
    var cloudLogPath = JOB_LOGGING_CLOUD_PREFIX + logPath;
    logClient.deleteLogs(logConfigs, cloudLogPath);
  }

  public static void setJobMdc(Path path) {
    if (shouldUseLocalLogs(new EnvConfigs())) {
      LOGGER.info("Setting docker job mdc");
      MDC.put(LogClientSingleton.JOB_LOG_PATH_MDC_KEY, path.resolve(LogClientSingleton.LOG_FILENAME).toString());
    } else {
      LOGGER.info("Setting kube job mdc");
      MDC.put(LogClientSingleton.CLOUD_JOB_LOG_PATH_MDC_KEY, path.resolve(LogClientSingleton.LOG_FILENAME).toString());
    }
  }

  public static void setWorkspaceMdc(Path path) {
    if (shouldUseLocalLogs(new EnvConfigs())) {
      LOGGER.info("Setting docker workspace mdc");
      MDC.put(LogClientSingleton.WORKSPACE_MDC_KEY, path.toString());
    } else {
      LOGGER.info("Setting kube workspace mdc");
      MDC.put(LogClientSingleton.CLOUD_WORKSPACE_MDC_KEY, path.toString());
    }
  }

  private static boolean shouldUseLocalLogs(Configs configs) {
    return configs.getWorkerEnvironment().equals(WorkerEnvironment.DOCKER) || CloudLogs.hasEmptyConfigs(new LogConfigDelegator(configs));
  }

  private static void createCloudClientIfNull(LogConfigs configs) {
    if (logClient == null) {
      logClient = CloudLogs.createCloudLogClient(configs);
    }
  }

}
