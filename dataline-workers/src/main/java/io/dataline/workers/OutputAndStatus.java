package io.dataline.workers;

public class OutputAndStatus<OutputType> {
  public final OutputType output;
  public final JobStatus status;

  public OutputAndStatus(OutputType output, JobStatus status) {
    this.output = output;
    this.status = status;
  }
}
