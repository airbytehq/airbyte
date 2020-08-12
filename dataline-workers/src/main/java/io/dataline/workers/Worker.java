package io.dataline.workers;

public interface Worker<OutputType> {
  /**
   * Blocking call to run the worker's workflow. Once this is complete, getStatus should return
   * either COMPLETE, FAILED, or CANCELLED.
   */
  OutputAndStatus<OutputType> run();

  void cancel();
}
