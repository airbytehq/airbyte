/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.util;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.Properties;

public class MoreProperties {

  /**
   * Read an .env file into a Properties object.
   *
   * @param envFile - .env file to read
   * @return properties object parsed from the contents of the .env
   * @throws IOException throws an exception if there are errors while reading the file.
   */
  public static Properties envFileToProperties(final File envFile) throws IOException {
    final Properties prop = new Properties();
    prop.load(new FileInputStream(envFile));
    return prop;
  }

}
