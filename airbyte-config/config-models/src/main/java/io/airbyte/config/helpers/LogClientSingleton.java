/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.helpers;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.io.IOs;
import io.airbyte.config.Configs;
import io.airbyte.config.Configs.WorkerEnvironment;
import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Collections;
import java.util.List;
import org.apache.commons.lang3.NotImplementedException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

/**
 * Airbyte's logging layer entrypoint. Handles logs written to local disk as well as logs written to
 * cloud storages.
 * <p>
 * Although the configuration is passed in as {@link Configs}, it is transformed to
 * {@link LogConfigs} within this class. Beyond this class, all configuration consumption is via the
 * {@link LogConfigs} interface via the {@link CloudLogs} interface.
 */
@SuppressWarnings({"PMD.AvoidThrowingRawExceptionTypes", "PMD.AvoidSynchronizedAtMethodLevel"})
public class LogClientSingleton {

  private static final Logger LOGGER = LoggerFactory.getLogger(LogClientSingleton.class);
  private static LogClientSingleton instance;

  @VisibleForTesting
  final static int LOG_TAIL_SIZE = 1000000;
  @VisibleForTesting
  CloudLogs logClient;

  // Any changes to the following values must also be propagated to the log4j2.xml in main/resources.
  public static final String WORKSPACE_MDC_KEY = "workspace_app_root";
  public static final String CLOUD_WORKSPACE_MDC_KEY = "cloud_workspace_app_root";

  public static final String JOB_LOG_PATH_MDC_KEY = "job_log_path";
  public static final String CLOUD_JOB_LOG_PATH_MDC_KEY = "cloud_job_log_path";

  // S3/Minio
  public static final String S3_LOG_BUCKET = "S3_LOG_BUCKET";
  public static final String S3_LOG_BUCKET_REGION = "S3_LOG_BUCKET_REGION";
  public static final String AWS_ACCESS_KEY_ID = "AWS_ACCESS_KEY_ID";
  public static final String AWS_SECRET_ACCESS_KEY = "AWS_SECRET_ACCESS_KEY";
  public static final String S3_MINIO_ENDPOINT = "S3_MINIO_ENDPOINT";

  // GCS
  public static final String GCS_LOG_BUCKET = "GCS_LOG_BUCKET";
  public static final String GOOGLE_APPLICATION_CREDENTIALS = "GOOGLE_APPLICATION_CREDENTIALS";

  public static final int DEFAULT_PAGE_SIZE = 1000;
  public static final String LOG_FILENAME = "logs.log";
  public static final String APP_LOGGING_CLOUD_PREFIX = "app-logging";
  public static final String JOB_LOGGING_CLOUD_PREFIX = "job-logging";

  public static synchronized LogClientSingleton getInstance() {
    if (instance == null) {
      instance = new LogClientSingleton();
    }
    return instance;
  }

  public Path getServerLogsRoot(final Path workspaceRoot) {
    return workspaceRoot.resolve("server/logs");
  }

  public Path getSchedulerLogsRoot(final Path workspaceRoot) {
    return workspaceRoot.resolve("scheduler/logs");
  }

  public File getServerLogFile(final Path workspaceRoot, final WorkerEnvironment workerEnvironment, final LogConfigs logConfigs) {
    if (shouldUseLocalLogs(workerEnvironment)) {
      return getServerLogsRoot(workspaceRoot).resolve(LOG_FILENAME).toFile();
    }
    final var cloudLogPath = sanitisePath(APP_LOGGING_CLOUD_PREFIX, getServerLogsRoot(workspaceRoot));
    try {
      createCloudClientIfNull(logConfigs);
      return logClient.downloadCloudLog(logConfigs, cloudLogPath);
    } catch (final IOException e) {
      throw new RuntimeException("Error retrieving log file: " + cloudLogPath + " from S3", e);
    }
  }

  public File getSchedulerLogFile(final Path workspaceRoot, final WorkerEnvironment workerEnvironment, final LogConfigs logConfigs) {
    if (shouldUseLocalLogs(workerEnvironment)) {
      return getSchedulerLogsRoot(workspaceRoot).resolve(LOG_FILENAME).toFile();
    }

    final var cloudLogPath = APP_LOGGING_CLOUD_PREFIX + getSchedulerLogsRoot(workspaceRoot);
    try {
      createCloudClientIfNull(logConfigs);
      return logClient.downloadCloudLog(logConfigs, cloudLogPath);
    } catch (final IOException e) {
      throw new RuntimeException("Error retrieving log file: " + cloudLogPath + " from S3", e);
    }
  }

  public List<String> getJobLogFile(final WorkerEnvironment workerEnvironment, final LogConfigs logConfigs, final Path logPath) throws IOException {
    if (logPath == null || logPath.equals(Path.of(""))) {
      return Collections.emptyList();
    }

    if (shouldUseLocalLogs(workerEnvironment)) {
      return IOs.getTail(LOG_TAIL_SIZE, logPath);
    }

    final var cloudLogPath = sanitisePath(JOB_LOGGING_CLOUD_PREFIX, logPath);
    createCloudClientIfNull(logConfigs);
    return logClient.tailCloudLog(logConfigs, cloudLogPath, LOG_TAIL_SIZE);
  }

  /**
   * Primarily to clean up logs after testing. Only valid for Kube logs.
   */
  @VisibleForTesting
  public void deleteLogs(final WorkerEnvironment workerEnvironment, final LogConfigs logConfigs, final String logPath) {
    if (logPath == null || logPath.equals("")) {
      return;
    }

    if (shouldUseLocalLogs(workerEnvironment)) {
      throw new NotImplementedException("Local log deletes not supported.");
    }
    final var cloudLogPath = sanitisePath(JOB_LOGGING_CLOUD_PREFIX, Path.of(logPath));
    createCloudClientIfNull(logConfigs);
    logClient.deleteLogs(logConfigs, cloudLogPath);
  }

  public void setJobMdc(final WorkerEnvironment workerEnvironment, final LogConfigs logConfigs, final Path path) {
    if (shouldUseLocalLogs(workerEnvironment)) {
      LOGGER.debug("Setting docker job mdc");
      final String resolvedPath = path.resolve(LogClientSingleton.LOG_FILENAME).toString();
      MDC.put(LogClientSingleton.JOB_LOG_PATH_MDC_KEY, resolvedPath);
    } else {
      LOGGER.debug("Setting kube job mdc");
      createCloudClientIfNull(logConfigs);
      MDC.put(LogClientSingleton.CLOUD_JOB_LOG_PATH_MDC_KEY, path.resolve(LogClientSingleton.LOG_FILENAME).toString());
    }
  }

  public void setWorkspaceMdc(final WorkerEnvironment workerEnvironment, final LogConfigs logConfigs, final Path path) {
    if (shouldUseLocalLogs(workerEnvironment)) {
      LOGGER.debug("Setting docker workspace mdc");
      MDC.put(LogClientSingleton.WORKSPACE_MDC_KEY, path.toString());
    } else {
      LOGGER.debug("Setting kube workspace mdc");
      createCloudClientIfNull(logConfigs);
      MDC.put(LogClientSingleton.CLOUD_WORKSPACE_MDC_KEY, path.toString());
    }
  }

  // This method should cease to exist here and become a property on the enum instead
  // TODO handle this as part of refactor https://github.com/airbytehq/airbyte/issues/7545
  private static boolean shouldUseLocalLogs(final WorkerEnvironment workerEnvironment) {
    return workerEnvironment.equals(WorkerEnvironment.DOCKER);
  }

  private void createCloudClientIfNull(final LogConfigs configs) {
    if (logClient == null) {
      logClient = CloudLogs.createCloudLogClient(configs);
    }
  }

  /**
   * Convenience wrapper for making sure paths are slash-separated.
   */
  private static String sanitisePath(final String prefix, final Path path) {
    return Paths.get(prefix, path.toString()).toString();
  }

}
