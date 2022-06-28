/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.specs;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DockerImageSpec;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SeedConnectorSpecGeneratorTest {

  private static final UUID DEF_ID1 = UUID.randomUUID();
  private static final UUID DEF_ID2 = UUID.randomUUID();
  private static final String CONNECTOR_NAME1 = "connector1";
  private static final String CONNECTOR_NAME2 = "connector2";
  private static final String DOCUMENTATION_URL = "https://wwww.example.com";
  private static final String DOCKER_REPOSITORY1 = "airbyte/connector1";
  private static final String DOCKER_REPOSITORY2 = "airbyte/connector2";
  private static final String DOCKER_TAG1 = "0.1.0";
  private static final String DOCKER_TAG2 = "0.2.0";
  private static final String BUCKET_NAME = "bucket";

  private SeedConnectorSpecGenerator seedConnectorSpecGenerator;
  private GcsBucketSpecFetcher bucketSpecFetcherMock;

  @BeforeEach
  void setup() {
    bucketSpecFetcherMock = mock(GcsBucketSpecFetcher.class);
    when(bucketSpecFetcherMock.getBucketName()).thenReturn(BUCKET_NAME);

    seedConnectorSpecGenerator = new SeedConnectorSpecGenerator(bucketSpecFetcherMock);
  }

  @Test
  void testMissingSpecIsFetched() {
    final StandardDestinationDefinition sourceDefinition1 = new StandardDestinationDefinition()
        .withDestinationDefinitionId(DEF_ID1)
        .withDockerRepository(DOCKER_REPOSITORY1)
        .withDockerImageTag(DOCKER_TAG1)
        .withName(CONNECTOR_NAME1)
        .withDocumentationUrl(DOCUMENTATION_URL);
    final ConnectorSpecification spec1 = new ConnectorSpecification().withConnectionSpecification(Jsons.jsonNode(ImmutableMap.of("foo1", "bar1")));
    final DockerImageSpec dockerImageSpec1 = new DockerImageSpec().withDockerImage(DOCKER_REPOSITORY1 + ":" + DOCKER_TAG1).withSpec(spec1);

    final StandardDestinationDefinition sourceDefinition2 = new StandardDestinationDefinition()
        .withDestinationDefinitionId(DEF_ID2)
        .withDockerRepository(DOCKER_REPOSITORY2)
        .withDockerImageTag(DOCKER_TAG2)
        .withName(CONNECTOR_NAME2)
        .withDocumentationUrl(DOCUMENTATION_URL);
    final ConnectorSpecification spec2 = new ConnectorSpecification().withConnectionSpecification(Jsons.jsonNode(ImmutableMap.of("foo2", "bar2")));
    final DockerImageSpec dockerImageSpec2 = new DockerImageSpec().withDockerImage(DOCKER_REPOSITORY2 + ":" + DOCKER_TAG2).withSpec(spec2);

    final JsonNode seedDefinitions = Jsons.jsonNode(Arrays.asList(sourceDefinition1, sourceDefinition2));
    final JsonNode seedSpecs = Jsons.jsonNode(List.of(dockerImageSpec1));

    when(bucketSpecFetcherMock.attemptFetch(DOCKER_REPOSITORY2 + ":" + DOCKER_TAG2)).thenReturn(Optional.of(spec2));

    final List<DockerImageSpec> actualSeedSpecs = seedConnectorSpecGenerator.fetchUpdatedSeedSpecs(seedDefinitions, seedSpecs);
    final List<DockerImageSpec> expectedSeedSpecs = Arrays.asList(dockerImageSpec1, dockerImageSpec2);

    assertEquals(expectedSeedSpecs, actualSeedSpecs);
  }

  @Test
  void testOutdatedSpecIsFetched() {
    final StandardDestinationDefinition sourceDefinition = new StandardDestinationDefinition()
        .withDestinationDefinitionId(DEF_ID1)
        .withDockerRepository(DOCKER_REPOSITORY1)
        .withDockerImageTag(DOCKER_TAG2)
        .withName(CONNECTOR_NAME1)
        .withDocumentationUrl(DOCUMENTATION_URL);
    final ConnectorSpecification outdatedSpec = new ConnectorSpecification().withConnectionSpecification(Jsons.jsonNode(ImmutableMap.of(
        "foo1",
        "bar1")));
    final DockerImageSpec outdatedDockerImageSpec = new DockerImageSpec().withDockerImage(DOCKER_REPOSITORY1 + ":" + DOCKER_TAG1)
        .withSpec(outdatedSpec);

    final JsonNode seedDefinitions = Jsons.jsonNode(List.of(sourceDefinition));
    final JsonNode seedSpecs = Jsons.jsonNode(List.of(outdatedDockerImageSpec));

    final ConnectorSpecification newSpec = new ConnectorSpecification().withConnectionSpecification(Jsons.jsonNode(ImmutableMap.of("foo2", "bar2")));
    final DockerImageSpec newDockerImageSpec = new DockerImageSpec().withDockerImage(DOCKER_REPOSITORY1 + ":" + DOCKER_TAG2).withSpec(newSpec);

    when(bucketSpecFetcherMock.attemptFetch(DOCKER_REPOSITORY1 + ":" + DOCKER_TAG2)).thenReturn(Optional.of(newSpec));

    final List<DockerImageSpec> actualSeedSpecs = seedConnectorSpecGenerator.fetchUpdatedSeedSpecs(seedDefinitions, seedSpecs);
    final List<DockerImageSpec> expectedSeedSpecs = List.of(newDockerImageSpec);

    assertEquals(expectedSeedSpecs, actualSeedSpecs);
  }

  @Test
  void testExtraneousSpecIsRemoved() {
    final StandardDestinationDefinition sourceDefinition = new StandardDestinationDefinition()
        .withDestinationDefinitionId(DEF_ID1)
        .withDockerRepository(DOCKER_REPOSITORY1)
        .withDockerImageTag(DOCKER_TAG1)
        .withName(CONNECTOR_NAME1)
        .withDocumentationUrl(DOCUMENTATION_URL);
    final ConnectorSpecification spec1 = new ConnectorSpecification().withConnectionSpecification(Jsons.jsonNode(ImmutableMap.of("foo1", "bar1")));
    final DockerImageSpec dockerImageSpec1 = new DockerImageSpec().withDockerImage(DOCKER_REPOSITORY1 + ":" + DOCKER_TAG1).withSpec(spec1);

    final ConnectorSpecification spec2 = new ConnectorSpecification().withConnectionSpecification(Jsons.jsonNode(ImmutableMap.of("foo2", "bar2")));
    final DockerImageSpec dockerImageSpec2 = new DockerImageSpec().withDockerImage(DOCKER_REPOSITORY2 + ":" + DOCKER_TAG2).withSpec(spec2);

    final JsonNode seedDefinitions = Jsons.jsonNode(List.of(sourceDefinition));
    final JsonNode seedSpecs = Jsons.jsonNode(Arrays.asList(dockerImageSpec1, dockerImageSpec2));

    final List<DockerImageSpec> actualSeedSpecs = seedConnectorSpecGenerator.fetchUpdatedSeedSpecs(seedDefinitions, seedSpecs);
    final List<DockerImageSpec> expectedSeedSpecs = List.of(dockerImageSpec1);

    assertEquals(expectedSeedSpecs, actualSeedSpecs);
  }

  @Test
  void testNoFetchIsPerformedIfAllSpecsUpToDate() {
    final StandardDestinationDefinition sourceDefinition = new StandardDestinationDefinition()
        .withDestinationDefinitionId(DEF_ID1)
        .withDockerRepository(DOCKER_REPOSITORY1)
        .withDockerImageTag(DOCKER_TAG1)
        .withName(CONNECTOR_NAME1)
        .withDocumentationUrl(DOCUMENTATION_URL);
    final ConnectorSpecification spec = new ConnectorSpecification().withConnectionSpecification(Jsons.jsonNode(ImmutableMap.of("foo", "bar")));
    final DockerImageSpec dockerImageSpec = new DockerImageSpec().withDockerImage(DOCKER_REPOSITORY1 + ":" + DOCKER_TAG1).withSpec(spec);

    final JsonNode seedDefinitions = Jsons.jsonNode(List.of(sourceDefinition));
    final JsonNode seedSpecs = Jsons.jsonNode(List.of(dockerImageSpec));

    final List<DockerImageSpec> actualSeedSpecs = seedConnectorSpecGenerator.fetchUpdatedSeedSpecs(seedDefinitions, seedSpecs);
    final List<DockerImageSpec> expectedSeedSpecs = List.of(dockerImageSpec);

    assertEquals(expectedSeedSpecs, actualSeedSpecs);
    verify(bucketSpecFetcherMock, never()).attemptFetch(any());
  }

}
