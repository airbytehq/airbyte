/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.util;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.commons.io.IOs;
import java.io.File;
import java.io.IOException;
import java.util.Properties;
import org.junit.jupiter.api.Test;

class MorePropertiesTest {

  @Test
  void testEnvFileToProperties() throws IOException {
    final String envFileContents = "OPTION1=hello\n"
        + "OPTION2=2\n"
        + "OPTION3=\n";
    final File envFile = File.createTempFile("properties-test", ".env");
    IOs.writeFile(envFile.toPath(), envFileContents);

    final Properties actual = MoreProperties.envFileToProperties(envFile);
    final Properties expected = new Properties();
    expected.put("OPTION1", "hello");
    expected.put("OPTION2", "2");
    expected.put("OPTION3", "");

    assertEquals(expected, actual);
  }

}
