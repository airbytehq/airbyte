/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.util;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.Properties;

public class MoreProperties {

  public static Properties envFileToProperties(final File file) throws IOException {
    final Properties prop = new Properties();
    prop.load(new FileInputStream(file));
    return prop;
  }

}
