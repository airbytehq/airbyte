package io.dataline.config.persistence;

public class ConfigNotFoundException extends Exception {
  public ConfigNotFoundException(String message) {
    super(message);
  }

  public ConfigNotFoundException(String message, Throwable cause) {
    super(message, cause);
  }
}
