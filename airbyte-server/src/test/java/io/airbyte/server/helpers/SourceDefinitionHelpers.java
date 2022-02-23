/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.helpers;

import io.airbyte.config.StandardSourceDefinition;
import java.util.UUID;

public class SourceDefinitionHelpers {

  public static StandardSourceDefinition generateSource() {
    return new StandardSourceDefinition()
        .withSourceDefinitionId(UUID.randomUUID())
        .withName("marketo")
        .withDockerRepository("thebestrepo")
        .withDockerImageTag("thelatesttag")
        .withDocumentationUrl("https://wikipedia.org");
  }

}
