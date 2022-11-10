package io.airbyte.integrations.standardtest.destination;

public enum ProtocolVersion {

  DEFAULT(""),
  V0("v0/");

  private final String prefix;

  ProtocolVersion(String prefix) {
    this.prefix = prefix;
  }

  public String getPrefix() {
    return prefix;
  }
}
