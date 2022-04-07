/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import io.airbyte.commons.resources.MoreResources;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import javax.annotation.PostConstruct;
import javax.inject.Singleton;

@Singleton
public class OpenApiConfigHandler {

  private File TMP_FILE;

  @PostConstruct
  public void initialize() {
    try {
      TMP_FILE = File.createTempFile("airbyte", "openapiconfig");
      TMP_FILE.deleteOnExit();
      Files.writeString(TMP_FILE.toPath(), MoreResources.readResource("config.yaml"));
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  public File getFile() {
    return TMP_FILE;
  }

}
