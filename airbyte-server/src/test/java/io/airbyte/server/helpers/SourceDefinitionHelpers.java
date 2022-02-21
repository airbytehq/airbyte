/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.helpers;

import io.airbyte.config.ActorDefinition;
import java.util.UUID;

public class SourceDefinitionHelpers {

  public static ActorDefinition generateSourceDefinition() {
    return new ActorDefinition()
        .withId(UUID.randomUUID())
        .withName("marketo")
        .withDockerRepository("thebestrepo")
        .withDockerImageTag("thelatesttag")
        .withDocumentationUrl("https://wikipedia.org");
  }

}
