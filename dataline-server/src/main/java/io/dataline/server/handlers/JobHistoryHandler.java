package io.dataline.server.handlers;

import io.dataline.api.model.ConnectionIdRequestBody;
import io.dataline.api.model.JobIdRequestBody;
import io.dataline.api.model.JobInfoRead;
import io.dataline.api.model.JobRead;
import io.dataline.api.model.JobReadList;
import io.dataline.api.model.LogRead;
import io.dataline.scheduler.Job;
import io.dataline.scheduler.JobStatus;
import io.dataline.scheduler.SchedulerPersistence;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class JobHistoryHandler {
  private final SchedulerPersistence schedulerPersistence;

  public JobHistoryHandler(SchedulerPersistence schedulerPersistence) {
    this.schedulerPersistence = schedulerPersistence;
  }

  public JobReadList listJobsFor(ConnectionIdRequestBody connectionIdRequestBody) {
    String connectionId = connectionIdRequestBody.getConnectionId().toString();

    JobReadList jobReadList = new JobReadList();
    jobReadList.setJobs(new ArrayList<>());

    return jobReadList;
  }

  public JobInfoRead getJobInfo(JobIdRequestBody jobIdRequestBody) {
    try {
      Job job = schedulerPersistence.getJob(jobIdRequestBody.getId());

      LogRead logRead = new LogRead();
      logRead.setStdout(getTail(job.getStdoutPath()));
      logRead.setStderr(getTail(job.getStderrPath()));

      JobInfoRead jobInfo = new JobInfoRead();
      jobInfo.setJob(getJobRead(job));
      jobInfo.setLogs(logRead);

      return jobInfo;
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  private static List<String> getTail(String path) {
    // todo
    return new ArrayList<>();
  }

  // todo: add test assertion for completeness
  private static JobRead.StatusEnum convertStatus(JobStatus jobStatus) {
    switch (jobStatus) {
      case PENDING:
        return JobRead.StatusEnum.PENDING;
      case RUNNING:
        return JobRead.StatusEnum.RUNNING;
      case FAILED:
        return JobRead.StatusEnum.FAILED;
      case COMPLETED:
        return JobRead.StatusEnum.COMPLETED;
      case CANCELLED:
        return JobRead.StatusEnum.CANCELLED;
      default:
        throw new IllegalStateException("Unexpected value: " + jobStatus);
    }
  }

  private static JobRead getJobRead(Job job) {
    JobRead jobRead = new JobRead();

    jobRead.setId(job.getId());
    jobRead.setScope(job.getScope());
    jobRead.setCreatedAt(job.getCreatedAt());

    if (job.getStartedAt().isPresent()) {
      jobRead.setStartedAt(job.getStartedAt().get());
    }

    jobRead.setUpdatedAt(job.getUpdatedAt());
    jobRead.setStatus(convertStatus(job.getStatus()));

    return jobRead;
  }
}
