package io.dataline.conduit.workers.singer;

import java.nio.file.Paths;

public enum SingerTarget implements ISingerTapOrTarget {
  LOCAL_FILE("", ""),
  BIG_QUERY("", ""),
  POSTGRES("", "");

  private final String pythonVirtualEnvName;
  private final String executableName;

  SingerTarget(String pythonVirtualEnvName, String executableName) {
    this.pythonVirtualEnvName = pythonVirtualEnvName;
    this.executableName = executableName;
  }

  @Override
  public String getPythonVirtualEnvName() {
    return pythonVirtualEnvName;
  }

  @Override
  public String getExecutableName() {
    return executableName;
  }
}
