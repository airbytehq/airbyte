/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.migrate;

import java.nio.file.Path;

public enum ResourceType {

  CONFIG(Path.of("airbyte_config")),
  JOB(Path.of("airbyte_db"));

  private final Path directoryName;

  private ResourceType(Path directoryName) {
    this.directoryName = directoryName;
  }

  public Path getDirectoryName() {
    return directoryName;
  }

}
