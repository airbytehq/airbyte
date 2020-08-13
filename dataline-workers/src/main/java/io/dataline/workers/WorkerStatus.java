package io.dataline.workers;

public enum WorkerStatus {
  /** Manually cancelled by the user */
  CANCELLED,
  /**
   * The worker irrecoverably failed due to an unexpected issue. This is NOT the same as a failure
   * in the "intended" process of the worker. For example, if a connection test worker failed
   * because the singer binaries were not in the expected location, the worker will be in FAILED
   * status. But if the worker succeeded, but the connection test itself was not positive due to bad
   * credentials, the worker is not considered FAILED. So, think of this status like an HTTP 500.
   */
  FAILED,
  /** Underlying process ran to completion. */
  COMPLETED;
}
