package io.dataline.scheduler;

import java.nio.file.Paths;

public class JobLogs {
    public static String ROOT_PATH = "logs/jobs";

    public static String getLogDirectory(String scope) {
        return Paths.get(ROOT_PATH, scope).toString();
    }
}
