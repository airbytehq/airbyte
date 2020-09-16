package io.dataline.workers;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class WorkerException extends Exception {

  public WorkerException(String message) {
    super(message);
  }
}
