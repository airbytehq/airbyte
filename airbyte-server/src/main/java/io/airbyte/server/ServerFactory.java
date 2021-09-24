/*
 * Copyright (c) 2020 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import io.airbyte.commons.io.FileTtlManager;
import io.airbyte.config.Configs;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.db.Database;
import io.airbyte.scheduler.client.SchedulerJobClient;
import io.airbyte.scheduler.client.SpecCachingSynchronousSchedulerClient;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.server.apis.ConfigurationApi;
import io.temporal.serviceclient.WorkflowServiceStubs;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import org.slf4j.MDC;

public interface ServerFactory {

  ServerRunnable create(SchedulerJobClient schedulerJobClient,
                        SpecCachingSynchronousSchedulerClient cachingSchedulerClient,
                        WorkflowServiceStubs temporalService,
                        ConfigRepository configRepository,
                        JobPersistence jobPersistence,
                        Database configsDatabase,
                        Database jobsDatabase,
                        Configs configs);

  class Api implements ServerFactory {

    @Override
    public ServerRunnable create(SchedulerJobClient schedulerJobClient,
                                 SpecCachingSynchronousSchedulerClient cachingSchedulerClient,
                                 WorkflowServiceStubs temporalService,
                                 ConfigRepository configRepository,
                                 JobPersistence jobPersistence,
                                 Database configsDatabase,
                                 Database jobsDatabase,
                                 Configs configs) {
      // set static values for factory
      ConfigurationApiFactory.setSchedulerJobClient(schedulerJobClient);
      ConfigurationApiFactory.setSynchronousSchedulerClient(cachingSchedulerClient);
      ConfigurationApiFactory.setTemporalService(temporalService);
      ConfigurationApiFactory.setConfigRepository(configRepository);
      ConfigurationApiFactory.setJobPersistence(jobPersistence);
      ConfigurationApiFactory.setConfigs(configs);
      ConfigurationApiFactory.setArchiveTtlManager(new FileTtlManager(10, TimeUnit.MINUTES, 10));
      ConfigurationApiFactory.setMdc(MDC.getCopyOfContextMap());
      ConfigurationApiFactory.setDatabases(configsDatabase, jobsDatabase);

      // server configurations
      final Set<Class<?>> componentClasses = Set.of(ConfigurationApi.class);
      final Set<Object> components = Set.of(new CorsFilter(), new ConfigurationApiBinder());

      // construct server
      return new ServerApp(configs.getAirbyteVersion(), componentClasses, components);
    }

  }

}
