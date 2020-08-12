package io.dataline.workers;

public interface Worker<OutputType> {
  WorkerStatus getStatus();

  /**
   * Blocking call to run the worker's workflow. Once this is complete, getStatus should return
   * either COMPLETE, FAILED, or CANCELLED.
   */
  WorkerOutputAndStatus<OutputType> run();

  void cancel();
}
