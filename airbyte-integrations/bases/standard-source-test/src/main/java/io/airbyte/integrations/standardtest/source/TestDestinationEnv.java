/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.source;

import java.nio.file.Path;

public class TestDestinationEnv {

  private final Path localRoot;

  public TestDestinationEnv(Path localRoot) {
    this.localRoot = localRoot;
  }

  public Path getLocalRoot() {
    return localRoot;
  }

}
