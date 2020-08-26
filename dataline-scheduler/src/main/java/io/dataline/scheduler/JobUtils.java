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

import com.fasterxml.jackson.databind.ObjectMapper;
import io.dataline.config.DestinationConnectionImplementation;
import io.dataline.config.JobConfig;
import io.dataline.config.JobOutput;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.StandardSync;
import io.dataline.config.StandardSyncOutput;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.db.DatabaseHelper;
import org.apache.commons.dbcp2.BasicDataSource;
import org.jooq.Record;

import java.io.IOException;
import java.sql.SQLException;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.Optional;
import java.util.UUID;

public class JobUtils {
  public static long createSyncJobFromConnectionId(
      SchedulerPersistence schedulerPersistence,
      ConfigPersistence configPersistence,
      UUID connectionId) {
    final StandardSync standardSync;
    standardSync = ConfigFetchers.getStandardSync(configPersistence, connectionId);

    final SourceConnectionImplementation sourceConnectionImplementation =
        ConfigFetchers.getSourceConnectionImplementation(
            configPersistence, standardSync.getSourceImplementationId());
    final DestinationConnectionImplementation destinationConnectionImplementation =
        ConfigFetchers.getDestinationConnectionImplementation(
            configPersistence, standardSync.getDestinationImplementationId());

    try {
      return schedulerPersistence.createSyncJob(
          sourceConnectionImplementation, destinationConnectionImplementation, standardSync);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static Optional<Job> getLastSyncJobForConnectionId(
      BasicDataSource connectionPool, UUID connectionId) throws IOException {
    try {
      return DatabaseHelper.query(
          connectionPool,
          ctx -> {
            Optional<Record> jobEntryOptional =
                ctx
                    .fetch(
                        "SELECT * FROM jobs WHERE scope = ? AND CAST(status AS VARCHAR) <> ? ORDER BY created_at DESC LIMIT 1",
                        connectionId.toString(),
                        JobStatus.CANCELLED.toString().toLowerCase())
                    .stream()
                    .findFirst();

            if (jobEntryOptional.isPresent()) {
              Record jobEntry = jobEntryOptional.get();
              Job job = DefaultSchedulerPersistence.getJobFromRecord(jobEntry);
              return Optional.of(job);
            } else {
              return Optional.empty();
            }
          });
    } catch (SQLException throwables) {
      throw new IOException(throwables);
    }
  }
}
