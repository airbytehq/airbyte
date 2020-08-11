package io.dataline.conduit.commons.env;

import java.util.Objects;

public enum Env {
    TEST, PROD;

    public static final Env CURRENT_ENV = Env.valueOf(Objects.requireNonNullElse(System.getenv("ENV"),"test").toUpperCase());

    public static boolean isTest() {
        return CURRENT_ENV == Env.TEST;
    }

    public static boolean isProd() {
        return CURRENT_ENV == Env.PROD;
    }
}
