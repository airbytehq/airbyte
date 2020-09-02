/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.scheduler;

import io.dataline.config.Schedule;
import io.dataline.config.StandardSync;
import io.dataline.config.StandardSyncSchedule;
import io.dataline.config.persistence.ConfigPersistence;
import java.io.IOException;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import org.apache.commons.dbcp2.BasicDataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class JobScheduler implements Runnable {

  private static final Logger LOGGER = LoggerFactory.getLogger(JobScheduler.class);

  private final BasicDataSource connectionPool;
  private final SchedulerPersistence schedulerPersistence;
  private final ConfigPersistence configPersistence;

  public JobScheduler(BasicDataSource connectionPool,
                      SchedulerPersistence schedulerPersistence,
                      ConfigPersistence configPersistence) {
    this.connectionPool = connectionPool;
    this.schedulerPersistence = schedulerPersistence;
    this.configPersistence = configPersistence;
  }

  @Override
  public void run() {
    try {
      LOGGER.info("Running job-scheduler...");

      scheduleSyncJobs();

    } catch (Throwable e) {
      LOGGER.error("Job Scheduler Error", e);
    }
  }

  private void scheduleSyncJobs() throws IOException {
    for (StandardSync connection : getAllActiveConnections()) {
      Optional<Job> lastJob =
          JobUtils.getLastSyncJobForConnectionId(connectionPool, connection.getConnectionId());

      if (lastJob.isEmpty()) {
        // pull configuration from connection.
        JobUtils.createSyncJobFromConnectionId(
            schedulerPersistence, configPersistence, connection.getConnectionId());
      } else {
        final Job job = lastJob.get();
        handleJob(connection.getConnectionId(), job);
      }
    }
  }

  private void handleJob(UUID connectionId, Job previousJob) {
    switch (previousJob.getStatus()) {
      case CANCELLED:
      case COMPLETED:
        final StandardSyncSchedule standardSyncSchedule =
            ConfigFetchers.getStandardSyncSchedule(configPersistence, connectionId);

        if (standardSyncSchedule.getManual()) {
          break;
        }

        long nextRunStart =
            previousJob.getUpdatedAt() + getIntervalInSeconds(standardSyncSchedule.getSchedule());
        if (nextRunStart < Instant.now().getEpochSecond()) {
          JobUtils.createSyncJobFromConnectionId(
              schedulerPersistence, configPersistence, connectionId);
        }
        break;
      // todo (cgardens) - add max retry concept
      case FAILED:
        JobUtils.createSyncJobFromConnectionId(
            schedulerPersistence, configPersistence, connectionId);
        break;
      case PENDING:
      case RUNNING:
        break;
    }
  }

  // todo: Assert in test to catch at build time
  private static Long getSecondsInUnit(Schedule.TimeUnit timeUnitEnum) {
    switch (timeUnitEnum) {
      case MINUTES:
        return TimeUnit.MINUTES.toSeconds(1);
      case HOURS:
        return TimeUnit.HOURS.toSeconds(1);
      case DAYS:
        return TimeUnit.DAYS.toSeconds(1);
      case WEEKS:
        return TimeUnit.DAYS.toSeconds(1) * 7;
      case MONTHS:
        return TimeUnit.DAYS.toSeconds(1) * 30;
      default:
        throw new RuntimeException("Unhandled TimeUnitEnum: " + timeUnitEnum);
    }
  }

  private static Long getIntervalInSeconds(Schedule schedule) {
    return getSecondsInUnit(schedule.getTimeUnit()) * schedule.getUnits();
  }

  private List<StandardSync> getAllActiveConnections() {
    return ConfigFetchers.getStandardSyncs(configPersistence);
  }

}
