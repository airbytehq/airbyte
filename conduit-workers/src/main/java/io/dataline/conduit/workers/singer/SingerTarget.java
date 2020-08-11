package io.dataline.conduit.workers.singer;

import java.nio.file.Paths;

public enum SingerTarget {
  LOCAL_FILE("", ""),
  BIG_QUERY("", ""),
  POSTGRES("", "");

  private final String pythonVenvName;
  private final String executableName;

  SingerTarget(String pythonVenvName, String executableName) {
    this.pythonVenvName = pythonVenvName;
    this.executableName = executableName;
  }

  public String getExecutablePath() {
    return Paths.get(SingerConstants.SINGER_LIB_ROOT_PATH, pythonVenvName, "bin", executableName)
        .toAbsolutePath()
        .toString();
  }
}
