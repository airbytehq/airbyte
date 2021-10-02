/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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
import java.util.Collections;
import java.util.List;
import org.apache.commons.lang3.NotImplementedException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

// todo (cgardens) - make this an actual singleton so we can write tests and mock the components.
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

  @VisibleForTesting
  static final int LOG_TAIL_SIZE = 1000000;
  @VisibleForTesting
  static CloudLogs logClient;

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

  public static Path getServerLogsRoot(final Configs configs) {
    return configs.getWorkspaceRoot().resolve("server/logs");
  }

  public static Path getSchedulerLogsRoot(final Configs configs) {
    return configs.getWorkspaceRoot().resolve("scheduler/logs");
  }

  public static File getServerLogFile(final Configs configs) {
    final var logPathBase = getServerLogsRoot(configs);
    if (shouldUseLocalLogs(configs)) {
      return logPathBase.resolve(LOG_FILENAME).toFile();
    }

    final var logConfigs = new LogConfigDelegator(configs);
    final var cloudLogPath = APP_LOGGING_CLOUD_PREFIX + logPathBase;
    try {
      return logClient.downloadCloudLog(logConfigs, cloudLogPath);
    } catch (final IOException e) {
      throw new RuntimeException("Error retrieving log file: " + cloudLogPath + " from S3", e);
    }
  }

  public static File getSchedulerLogFile(final Configs configs) {
    final var logPathBase = getSchedulerLogsRoot(configs);
    if (shouldUseLocalLogs(configs)) {
      return logPathBase.resolve(LOG_FILENAME).toFile();
    }

    final var logConfigs = new LogConfigDelegator(configs);
    final var cloudLogPath = APP_LOGGING_CLOUD_PREFIX + logPathBase;
    try {
      return logClient.downloadCloudLog(logConfigs, cloudLogPath);
    } catch (final IOException e) {
      throw new RuntimeException("Error retrieving log file: " + cloudLogPath + " from S3", e);
    }
  }

  public static List<String> getJobLogFile(final Configs configs, final Path logPath) throws IOException {
    if (logPath == null || logPath.equals(Path.of(""))) {
      return Collections.emptyList();
    }

    if (shouldUseLocalLogs(configs)) {
      return IOs.getTail(LOG_TAIL_SIZE, logPath);
    }

    final var logConfigs = new LogConfigDelegator(configs);
    final var cloudLogPath = JOB_LOGGING_CLOUD_PREFIX + logPath;
    return logClient.tailCloudLog(logConfigs, cloudLogPath, LOG_TAIL_SIZE);
  }

  /**
   * Primarily to clean up logs after testing. Only valid for Kube logs.
   */
  @VisibleForTesting
  public static void deleteLogs(final Configs configs, final String logPath) {
    if (logPath == null || logPath.equals(Path.of(""))) {
      return;
    }

    if (shouldUseLocalLogs(configs)) {
      throw new NotImplementedException("Local log deletes not supported.");
    }
    final var logConfigs = new LogConfigDelegator(configs);
    final var cloudLogPath = JOB_LOGGING_CLOUD_PREFIX + logPath;
    logClient.deleteLogs(logConfigs, cloudLogPath);
  }

  public static void setJobMdc(final Path path) {
    final var configs = new EnvConfigs();
    if (shouldUseLocalLogs(configs)) {
      LOGGER.debug("Setting docker job mdc");
      MDC.put(LogClientSingleton.JOB_LOG_PATH_MDC_KEY, path.resolve(LogClientSingleton.LOG_FILENAME).toString());
    } else {
      LOGGER.debug("Setting kube job mdc");
      final var logConfigs = new LogConfigDelegator(configs);
      createCloudClientIfNull(logConfigs);
      MDC.put(LogClientSingleton.CLOUD_JOB_LOG_PATH_MDC_KEY, path.resolve(LogClientSingleton.LOG_FILENAME).toString());
    }
  }

  public static void setWorkspaceMdc(final Path path) {
    final var configs = new EnvConfigs();
    if (shouldUseLocalLogs(configs)) {
      LOGGER.debug("Setting docker workspace mdc");
      MDC.put(LogClientSingleton.WORKSPACE_MDC_KEY, path.toString());
    } else {
      LOGGER.debug("Setting kube workspace mdc");
      final var logConfigs = new LogConfigDelegator(configs);
      createCloudClientIfNull(logConfigs);
      MDC.put(LogClientSingleton.CLOUD_WORKSPACE_MDC_KEY, path.toString());
    }
  }

  private static boolean shouldUseLocalLogs(final Configs configs) {
    return configs.getWorkerEnvironment().equals(WorkerEnvironment.DOCKER);
  }

  private static void createCloudClientIfNull(final LogConfigs configs) {
    if (logClient == null) {
      logClient = CloudLogs.createCloudLogClient(configs);
    }
  }

}
