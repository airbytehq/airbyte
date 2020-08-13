package io.dataline.workers.singer;

public enum SingerTap implements SingerConnector {
  // TODO
  S3_CSV("", ""),
  POSTGRES("", ""),
  STRIPE("", "");

  private final String getPythonVirtualEnvName;
  private final String executableName;

  SingerTap(String getPythonVirtualEnvName, String executableName) {
    this.getPythonVirtualEnvName = getPythonVirtualEnvName;
    this.executableName = executableName;
  }

  public String getPythonVirtualEnvName() {
    return getPythonVirtualEnvName;
  }

  public String getExecutableName() {
    return executableName;
  }
}
