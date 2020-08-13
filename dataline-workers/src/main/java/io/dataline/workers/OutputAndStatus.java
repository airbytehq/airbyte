package io.dataline.workers;

import java.util.Optional;

public class OutputAndStatus<OutputType> {
  public final Optional<OutputType> output;
  public final JobStatus status;

  public OutputAndStatus(JobStatus status, OutputType output) {
    this.output = Optional.of(output);
    this.status = status;
  }

  public OutputAndStatus(JobStatus status) {
    this.status = status;
    this.output = Optional.empty();
  }
}
