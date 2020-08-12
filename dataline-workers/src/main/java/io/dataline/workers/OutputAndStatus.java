package io.dataline.workers;

public class OutputAndStatus<OutputType> {
  public final OutputType output;
  public final WorkerStatus status;

  public OutputAndStatus(OutputType output, WorkerStatus status) {
    this.output = output;
    this.status = status;
  }
}
