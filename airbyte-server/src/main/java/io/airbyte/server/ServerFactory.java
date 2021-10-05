/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import io.airbyte.analytics.TrackingClient;
import io.airbyte.commons.io.FileTtlManager;
import io.airbyte.config.Configs;
import io.airbyte.config.persistence.ConfigPersistence;
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
                        ConfigPersistence seed,
                        Database configsDatabase,
                        Database jobsDatabase,
                        Configs configs,
                        TrackingClient trackingClient);

  class Api implements ServerFactory {

    @Override
    public ServerRunnable create(final SchedulerJobClient schedulerJobClient,
                                 final SpecCachingSynchronousSchedulerClient cachingSchedulerClient,
                                 final WorkflowServiceStubs temporalService,
                                 final ConfigRepository configRepository,
                                 final JobPersistence jobPersistence,
                                 final ConfigPersistence seed,
                                 final Database configsDatabase,
                                 final Database jobsDatabase,
                                 final Configs configs,
                                 final TrackingClient trackingClient) {
      // set static values for factory
      ConfigurationApiFactory.setValues(
          temporalService,
          configRepository,
          jobPersistence,
          seed,
          schedulerJobClient,
          cachingSchedulerClient,
          configs,
          new FileTtlManager(10, TimeUnit.MINUTES, 10),
          MDC.getCopyOfContextMap(),
          configsDatabase,
          jobsDatabase,
          trackingClient);

      // server configurations
      final Set<Class<?>> componentClasses = Set.of(ConfigurationApi.class);
      final Set<Object> components = Set.of(new CorsFilter(), new ConfigurationApiBinder());

      // construct server
      return new ServerApp(configs.getAirbyteVersion(), componentClasses, components);
    }

  }

}
