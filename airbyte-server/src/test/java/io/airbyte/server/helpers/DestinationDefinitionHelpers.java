/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.helpers;

import io.airbyte.config.ActorDefinition;
import java.util.UUID;

public class DestinationDefinitionHelpers {

  public static ActorDefinition generateDestination() {
    return new ActorDefinition()
        .withId(UUID.randomUUID())
        .withName("db2")
        .withDockerRepository("thebestrepo")
        .withDockerImageTag("thelatesttag")
        .withDocumentationUrl("https://wikipedia.org");
  }

}
