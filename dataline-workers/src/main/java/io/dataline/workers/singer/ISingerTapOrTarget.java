package io.dataline.workers.singer;

interface ISingerTapOrTarget {
    String getPythonVirtualEnvName();
    String getExecutableName();
}
