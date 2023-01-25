/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.helpers;

import io.airbyte.config.StandardDestinationDefinition;
import java.util.UUID;

public class DestinationDefinitionHelpers {

  public static StandardDestinationDefinition generateDestination() {
    return new StandardDestinationDefinition()
        .withDestinationDefinitionId(UUID.randomUUID())
        .withName("db2")
        .withDockerRepository("thebestrepo")
        .withDockerImageTag("thelatesttag")
        .withDocumentationUrl("https://wikipedia.org");
  }

}
