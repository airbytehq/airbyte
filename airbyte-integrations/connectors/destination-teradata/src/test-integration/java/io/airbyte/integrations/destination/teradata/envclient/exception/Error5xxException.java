package io.airbyte.integrations.destination.teradata.envclient.exception;

public class Error5xxException extends BaseException {

    public Error5xxException(int statusCode, String body, String reason) {
        super(statusCode, body, reason);
    }

    public Error5xxException(int statusCode, String body) {
        super(statusCode, body);
    }

}