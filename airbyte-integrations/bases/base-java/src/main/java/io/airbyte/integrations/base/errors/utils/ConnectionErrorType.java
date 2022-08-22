/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.utils;

public enum ConnectionErrorType {

  INCORRECT_HOST_OR_PORT("Invalid credentials: incorrect host or port."),
  INCORRECT_HOST_OR_PORT_OR_DATABASE("Invalid credentials: incorrect host, port or database name."),
  INCORRECT_USERNAME_OR_PASSWORD_OR_DATABASE("Invalid credentials: username, password or database name."),
  INCORRECT_CLUSTER("Invalid credentials: incorrect cluster."),
  INCORRECT_ACCESS_PERMISSION("Invalid credentials: user access denied.");

  private final String value;

  ConnectionErrorType(String value) {
    this.value = value;
  }

  public String getValue() {
    return value;
  }

}
