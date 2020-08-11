package io.dataline.conduit.workers.singer;

interface ISingerTapOrTarget {
    String getPythonVirtualEnvName();
    String getExecutableName();
}
