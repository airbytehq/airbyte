package io.dataline.workers;

public class CheckConnectionOutput {
  private final JobStatus status;

  public CheckConnectionOutput(JobStatus status) {
    this.status = status;
  }

  public JobStatus getStatus() {
    return status;
  }
}
