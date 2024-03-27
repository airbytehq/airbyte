/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

public final class CDKConstants {

  private CDKConstants() {
    // restrict instantiation
  }

  public static final String VERSION = getVersion();

  private static String getVersion() {
    Properties prop = new Properties();

    try (InputStream inputStream = CDKConstants.class.getClassLoader().getResourceAsStream("version.properties")) {
      prop.load(inputStream);
      return prop.getProperty("version");
    } catch (IOException e) {
      throw new RuntimeException("Could not read version properties file", e);
    }
  }

}
