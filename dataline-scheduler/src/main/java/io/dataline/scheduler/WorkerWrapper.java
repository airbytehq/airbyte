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
import io.dataline.api.model.Job;
import io.dataline.db.DatabaseHelper;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.Worker;
import java.sql.SQLException;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import org.apache.commons.dbcp2.BasicDataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class WorkerWrapper<T> implements Runnable {
  private static final Logger LOGGER = LoggerFactory.getLogger(WorkerWrapper.class);

  private final long jobId;
  private final Worker<T> worker;
  private final BasicDataSource connectionPool;

  public WorkerWrapper(long jobId, Worker<T> worker, BasicDataSource connectionPool) {
    this.jobId = jobId;
    this.worker = worker;
    this.connectionPool = connectionPool;
  }

  @Override
  public void run() {
    LOGGER.info("Executing worker wrapper...");
    try {
      setJobStatus(connectionPool, jobId, Job.StatusEnum.RUNNING);

      OutputAndStatus<T> outputAndStatus = worker.run();

      switch (outputAndStatus.getStatus()) {
        case FAILED:
          setJobStatus(connectionPool, jobId, Job.StatusEnum.FAILED);
          break;
        case SUCCESSFUL:
          setJobStatus(connectionPool, jobId, Job.StatusEnum.COMPLETED);
          break;
      }

      if (outputAndStatus.getOutput().isPresent()) {
        ObjectMapper objectMapper = new ObjectMapper();
        String json = objectMapper.writeValueAsString(outputAndStatus.getOutput().get());
        setJobOutput(connectionPool, jobId, json);
        LOGGER.info("Set job output for job " + jobId);
      } else {
        LOGGER.info("No output present for job " + jobId);
      }
    } catch (Exception e) {
      LOGGER.error("Worker Error", e);
      setJobStatus(connectionPool, jobId, Job.StatusEnum.FAILED);
    }
  }

  private static void setJobStatus(
      BasicDataSource connectionPool, long jobId, Job.StatusEnum status) {
    LOGGER.info("Setting job status to " + status + " for job " + jobId);
    LocalDateTime now = LocalDateTime.ofInstant(Instant.now(), ZoneOffset.UTC);

    try {
      DatabaseHelper.query(
          connectionPool,
          ctx ->
              ctx.execute(
                  "UPDATE jobs SET status = CAST(? as JOB_STATUS), updated_at = ? WHERE id = ?",
                  status.toString().toLowerCase(),
                  now,
                  jobId));
    } catch (SQLException e) {
      LOGGER.error("SQL Error", e);
      throw new RuntimeException(e);
    }
  }

  private static void setJobOutput(BasicDataSource connectionPool, long jobId, String outputJson) {
    LocalDateTime now = LocalDateTime.ofInstant(Instant.now(), ZoneOffset.UTC);

    try {
      DatabaseHelper.query(
          connectionPool,
          ctx ->
              ctx.execute(
                  "UPDATE jobs SET output = CAST(? as JSONB), updated_at = ? WHERE id = ?",
                  outputJson,
                  now,
                  jobId));
    } catch (SQLException e) {
      LOGGER.error("SQL Error", e);
      throw new RuntimeException(e);
    }
  }
}
