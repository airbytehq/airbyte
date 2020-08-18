package io.dataline.scheduler;

import com.google.gson.Gson;
import io.dataline.api.model.Job;
import io.dataline.db.DatabaseHelper;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.Worker;
import org.apache.commons.dbcp2.BasicDataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.SQLException;

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
    LOGGER.info("executing worker wrapper...");
    try {
      setJobStatus(connectionPool, jobId, Job.StatusEnum.RUNNING);

      OutputAndStatus<T> outputAndStatus = worker.run();

      switch (outputAndStatus.status) {
        case FAILED:
          setJobStatus(connectionPool, jobId, Job.StatusEnum.FAILED);
          break;
        case SUCCESSFUL:
          setJobStatus(connectionPool, jobId, Job.StatusEnum.COMPLETED);
          break;
      }

      if (outputAndStatus.output.isPresent()) {
        String json = new Gson().toJson(outputAndStatus.output.get());
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
    try {
      DatabaseHelper.query(
          connectionPool,
          ctx ->
              ctx.execute(
                  "UPDATE jobs SET status = CAST(? as JOB_STATUS) WHERE id = ?",
                  status.toString().toLowerCase(),
                  jobId));
    } catch (SQLException e) {
      LOGGER.error("SQL Error", e);
      throw new RuntimeException(e);
    }
  }

  private static void setJobOutput(BasicDataSource connectionPool, long jobId, String outputJson) {
    try {
      DatabaseHelper.query(
          connectionPool,
          ctx ->
              ctx.execute(
                  "UPDATE jobs SET output = CAST(? as JSONB) WHERE id = ?", outputJson, jobId));
    } catch (SQLException e) {
      LOGGER.error("SQL Error", e);
      throw new RuntimeException(e);
    }
  }
}
