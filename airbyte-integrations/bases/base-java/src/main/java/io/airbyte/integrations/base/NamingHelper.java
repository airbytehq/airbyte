package io.airbyte.integrations.base;

public class NamingHelper {
  public static String getRawTableName(String streamName) {
    return streamName + "_raw";
  }
}
