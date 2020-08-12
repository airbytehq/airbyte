package io.dataline.server.errors;

public class KnownException extends RuntimeException {
  private final int httpCode;

  public KnownException(int httpCode, String message) {
    super(message);
    this.httpCode = httpCode;
  }

  public KnownException(int httpCode, String message, Throwable cause) {
    super(message, cause);
    this.httpCode = httpCode;
  }

  public int getHttpCode() {
    return httpCode;
  }
}
