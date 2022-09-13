/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import java.util.UUID;
import org.junit.jupiter.api.Test;

public class JsonDefinitionsHelperTest {

  final private UUID uuid1 = UUID.randomUUID();
  final private String DEF_NAME = "marketo";
  final private String DOCKER_REPOSITORY = "airbyte/marketo";
  final private String DOCKER_TAG = "1.2.3";
  final private String DOCUMENTATION_URL = "https://airbyte.io/";

  @Test
  void testPatchSourceDefinition() {
    final StandardSourceDefinition sourceDefinition = new StandardSourceDefinition()
        .withSourceDefinitionId(uuid1)
        .withName(DEF_NAME)
        .withDockerRepository(DOCKER_REPOSITORY)
        .withDockerImageTag(DOCKER_TAG)
        .withDocumentationUrl(DOCUMENTATION_URL)
        .withPublic(true);

    assertNull(sourceDefinition.getTombstone());

    final StandardSourceDefinition patchedSourceDef = JsonDefinitionsHelper.patchSourceDefinition(sourceDefinition);

    final StandardSourceDefinition expectedSourceDef = new StandardSourceDefinition()
        .withSourceDefinitionId(uuid1)
        .withName(DEF_NAME)
        .withDockerRepository(DOCKER_REPOSITORY)
        .withDockerImageTag(DOCKER_TAG)
        .withDocumentationUrl(DOCUMENTATION_URL)
        .withTombstone(false)
        .withPublic(true);

    assertEquals(expectedSourceDef, patchedSourceDef);
  }

  @Test
  void testPatchDestinationDefinition() {
    final StandardDestinationDefinition destinationDefinition = new StandardDestinationDefinition()
        .withDestinationDefinitionId(uuid1)
        .withName(DEF_NAME)
        .withDockerRepository(DOCKER_REPOSITORY)
        .withDockerImageTag(DOCKER_TAG)
        .withDocumentationUrl(DOCUMENTATION_URL)
        .withPublic(true);

    assertNull(destinationDefinition.getTombstone());

    final StandardDestinationDefinition patchedDestinationDef = JsonDefinitionsHelper.patchDestinationDefinition(destinationDefinition);

    final StandardDestinationDefinition expectedDestinationDef = new StandardDestinationDefinition()
        .withDestinationDefinitionId(uuid1)
        .withName(DEF_NAME)
        .withDockerRepository(DOCKER_REPOSITORY)
        .withDockerImageTag(DOCKER_TAG)
        .withDocumentationUrl(DOCUMENTATION_URL)
        .withTombstone(false)
        .withPublic(true);

    assertEquals(expectedDestinationDef, patchedDestinationDef);
  }

}
