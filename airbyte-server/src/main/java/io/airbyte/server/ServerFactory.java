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
