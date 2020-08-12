package io.dataline.config.persistence;

public class JsonValidationException extends Exception {
  public JsonValidationException(String message) {
    super(message);
  }

  public JsonValidationException(String message, Throwable cause) {
    super(message, cause);
  }
}
