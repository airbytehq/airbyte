package io.dataline.workers;

/**
 * Indicates whether the worker's underlying process was succesful. E.g this should return SUCCESSFUL if a connection check
 * succeeds, FAILED otherwise.
 */
public enum JobStatus {
  FAILED,
  SUCCESSFUL;
}
