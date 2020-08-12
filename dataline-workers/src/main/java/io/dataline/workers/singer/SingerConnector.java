package io.dataline.workers.singer;

interface SingerConnector {
    String getPythonVirtualEnvName();
    String getExecutableName();
}
