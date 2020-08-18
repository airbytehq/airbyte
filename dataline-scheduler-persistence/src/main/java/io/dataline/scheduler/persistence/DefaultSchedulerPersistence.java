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

package io.dataline.scheduler.persistence;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.dataline.config.JobConfig;
import io.dataline.config.JobOutput;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.db.DatabaseHelper;
import java.io.IOException;
import java.sql.SQLException;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.Optional;
import java.util.UUID;
import org.apache.commons.dbcp2.BasicDataSource;
import org.jooq.Record;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultSchedulerPersistence implements SchedulerPersistence {
  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultSchedulerPersistence.class);
  private final BasicDataSource connectionPool;

  public DefaultSchedulerPersistence(BasicDataSource connectionPool) {
    this.connectionPool = connectionPool;
  }

  public long createSourceCheckConnectionJob(
      UUID sourceImplementation, SourceConnectionImplementation sourceImplementationJson)
      throws IOException {
    final String scope = "sourceImplementation:" + sourceImplementation.toString();

    final JobConfig jobConfig = new JobConfig();
    jobConfig.setCheckConnection(sourceImplementationJson);

    return createPendingJob(scope, jobConfig);
  }

  // configJson is a oneOf checkConnection, discoverSchema, sync
  public long createPendingJob(String scope, JobConfig jobConfig) throws IOException {
    LOGGER.info("creating pending job for scope: " + scope);
    LocalDateTime now = LocalDateTime.ofInstant(Instant.now(), ZoneOffset.UTC);

    final ObjectMapper objectMapper = new ObjectMapper();
    final String configJson = objectMapper.writeValueAsString(jobConfig);

    final Record record;
    try {
      record =
          DatabaseHelper.query(
                  connectionPool,
                  ctx ->
                      ctx.fetch(
                          "INSERT INTO jobs(scope, created_at, updated_at, status, config, output, stdout_path, stderr_path) VALUES(?, ?, ?, CAST(? AS JOB_STATUS), CAST(? as JSONB), ?, ?, ?) RETURNING id",
                          scope,
                          now,
                          now,
                          "pending",
                          configJson,
                          null,
                          "", // todo: assign stdout
                          "") // todo: assign stderr
                  )
              .stream()
              .findFirst()
              .orElseThrow(() -> new RuntimeException("This should not happen"));
    } catch (SQLException e) {
      LOGGER.error("sql", e);
      throw new IOException(e);
    }
    return record.getValue("id", Long.class);
  }

  public Job getJob(long jobId) throws IOException {
    try {
      return DatabaseHelper.query(
          connectionPool,
          ctx -> {
            Record jobEntry =
                ctx.fetch("SELECT * FROM jobs WHERE id = ?", jobId).stream()
                    .findFirst()
                    .orElseThrow(
                        () -> new RuntimeException("Could not find job with id: " + jobId));

            final ObjectMapper objectMapper = new ObjectMapper();

            final JobConfig jobConfig;
            try {
              jobConfig =
                  objectMapper.readValue(jobEntry.get("config", String.class), JobConfig.class);
            } catch (IOException e) {
              throw new RuntimeException(e);
            }

            final JobOutput output;
            try {
              final String outputDb = jobEntry.get("output", String.class);
              if (outputDb == null) {
                output = null;
              } else {
                output = objectMapper.readValue(outputDb, JobOutput.class);
              }

            } catch (IOException e) {
              throw new RuntimeException(e);
            }

            return new Job(
                jobEntry.get("id", Long.class),
                jobEntry.get("scope", String.class),
                JobStatus.valueOf(jobEntry.get("status", String.class).toUpperCase()), // hack
                jobConfig,
                output,
                jobEntry.get("stdout_path", String.class),
                jobEntry.get("stderr_path", String.class),
                jobEntry.get("created_at", Long.class),
                Optional.ofNullable(jobEntry.get("started_at"))
                    .map(value -> Long.parseLong(value.toString()))
                    .orElse(null),
                jobEntry.get("updated_at", Long.class));
          });
    } catch (SQLException e) {
      throw new IOException(e);
    }
  }
}
