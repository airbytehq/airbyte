/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.handlers;

import static org.junit.jupiter.api.Assertions.*;

import com.google.common.io.Files;
import java.io.IOException;
import java.nio.charset.Charset;
import java.util.List;
import org.junit.jupiter.api.Test;

class OpenApiConfigHandlerTest {

  @Test
  void testGetFile() throws IOException {
    final List<String> lines = Files.readLines(new OpenApiConfigHandler().getFile(), Charset.defaultCharset());
    assertTrue(lines.get(0).contains("openapi"));
  }

}
