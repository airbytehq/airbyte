/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.destination;

public enum ProtocolVersion {

  V0("v0"),
  V1("v1");

  private final String prefix;

  ProtocolVersion(String prefix) {
    this.prefix = prefix;
  }

  public String getPrefix() {
    return prefix;
  }

}
