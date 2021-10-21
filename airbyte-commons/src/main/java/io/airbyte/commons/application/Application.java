package io.airbyte.commons.application;

public interface Application {

  default String getApplicationName() {
    // This value should only be used in the U-Test, it is an empty string instead of airbyte-test in order to avoid displaying airbyte-test in prod
    return "";
  }
}
