package io.dataline.workers;

public class InvalidCredentialsException extends Exception {
    public InvalidCredentialsException(String message){
        super(message);
    }
}
