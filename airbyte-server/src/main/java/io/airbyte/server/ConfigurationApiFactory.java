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

package io.airbyte.server;

import io.airbyte.commons.io.FileTtlManager;
import io.airbyte.config.Configs;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.db.Database;
import io.airbyte.scheduler.client.CachingSynchronousSchedulerClient;
import io.airbyte.scheduler.client.SchedulerJobClient;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.server.apis.ConfigurationApi;
import io.temporal.serviceclient.WorkflowServiceStubs;
import java.util.Map;
import org.glassfish.hk2.api.Factory;
import org.slf4j.MDC;

public class ConfigurationApiFactory implements Factory<ConfigurationApi> {

  private static WorkflowServiceStubs temporalService;
  private static ConfigRepository configRepository;
  private static JobPersistence jobPersistence;
  private static SchedulerJobClient schedulerJobClient;
  private static CachingSynchronousSchedulerClient synchronousSchedulerClient;
  private static Configs configs;
  private static FileTtlManager archiveTtlManager;
  private static Map<String, String> mdc;
  private static Database configsDatabase;
  private static Database jobsDatabase;

  public static void setConfigRepository(final ConfigRepository configRepository) {
    ConfigurationApiFactory.configRepository = configRepository;
  }

  public static void setJobPersistence(final JobPersistence jobPersistence) {
    ConfigurationApiFactory.jobPersistence = jobPersistence;
  }

  public static void setSchedulerJobClient(final SchedulerJobClient schedulerJobClient) {
    ConfigurationApiFactory.schedulerJobClient = schedulerJobClient;
  }

  public static void setSynchronousSchedulerClient(final CachingSynchronousSchedulerClient synchronousSchedulerClient) {
    ConfigurationApiFactory.synchronousSchedulerClient = synchronousSchedulerClient;
  }

  public static void setConfigs(Configs configs) {
    ConfigurationApiFactory.configs = configs;
  }

  public static void setArchiveTtlManager(final FileTtlManager archiveTtlManager) {
    ConfigurationApiFactory.archiveTtlManager = archiveTtlManager;
  }

  public static void setMdc(Map<String, String> mdc) {
    ConfigurationApiFactory.mdc = mdc;
  }

  public static void setTemporalService(final WorkflowServiceStubs temporalService) {
    ConfigurationApiFactory.temporalService = temporalService;
  }

  public static void setDatabases(final Database configsDatabase, final Database jobsDatabase) {
    ConfigurationApiFactory.configsDatabase = configsDatabase;
    ConfigurationApiFactory.jobsDatabase = jobsDatabase;
  }

  @Override
  public ConfigurationApi provide() {
    MDC.setContextMap(mdc);

    return new ConfigurationApi(
        ConfigurationApiFactory.configRepository,
        ConfigurationApiFactory.jobPersistence,
        ConfigurationApiFactory.schedulerJobClient,
        ConfigurationApiFactory.synchronousSchedulerClient,
        ConfigurationApiFactory.configs,
        ConfigurationApiFactory.archiveTtlManager,
        ConfigurationApiFactory.temporalService,
        ConfigurationApiFactory.configsDatabase,
        ConfigurationApiFactory.jobsDatabase);
  }

  @Override
  public void dispose(ConfigurationApi service) {
    /* noop */
  }

}
