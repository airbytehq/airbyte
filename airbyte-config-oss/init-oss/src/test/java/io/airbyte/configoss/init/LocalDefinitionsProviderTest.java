/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.configoss.init;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.configoss.StandardDestinationDefinition;
import io.airbyte.configoss.StandardSourceDefinition;
import java.io.IOException;
import java.net.URI;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

class LocalDefinitionsProviderTest {

  private static LocalDefinitionsProvider localDefinitionsProvider;

  @BeforeAll
  static void setup() throws IOException {
    localDefinitionsProvider = new LocalDefinitionsProvider();
  }

  @Test
  void testGetSourceDefinition() throws Exception {
    // source
    final UUID stripeSourceId = UUID.fromString("e094cb9a-26de-4645-8761-65c0c425d1de");
    final StandardSourceDefinition stripeSource = localDefinitionsProvider.getSourceDefinition(stripeSourceId);
    assertEquals(stripeSourceId, stripeSource.getSourceDefinitionId());
    assertEquals("Stripe", stripeSource.getName());
    assertEquals("airbyte/source-stripe", stripeSource.getDockerRepository());
    assertEquals("https://docs.airbyte.com/integrations/sources/stripe", stripeSource.getDocumentationUrl());
    assertEquals("stripe.svg", stripeSource.getIcon());
    assertEquals(URI.create("https://docs.airbyte.com/integrations/sources/stripe"), stripeSource.getSpec().getDocumentationUrl());
    assertEquals(false, stripeSource.getTombstone());
    assertEquals("0.2.0", stripeSource.getProtocolVersion());
  }

  @Test
  @SuppressWarnings({"PMD.AvoidDuplicateLiterals"})
  void testGetDestinationDefinition() throws Exception {
    final UUID s3DestinationId = UUID.fromString("4816b78f-1489-44c1-9060-4b19d5fa9362");
    final StandardDestinationDefinition s3Destination = localDefinitionsProvider
        .getDestinationDefinition(s3DestinationId);
    assertEquals(s3DestinationId, s3Destination.getDestinationDefinitionId());
    assertEquals("S3", s3Destination.getName());
    assertEquals("airbyte/destination-s3", s3Destination.getDockerRepository());
    assertEquals("https://docs.airbyte.com/integrations/destinations/s3", s3Destination.getDocumentationUrl());
    assertEquals(URI.create("https://docs.airbyte.com/integrations/destinations/s3"), s3Destination.getSpec().getDocumentationUrl());
    assertEquals(false, s3Destination.getTombstone());
    assertEquals("0.2.0", s3Destination.getProtocolVersion());
  }

  @Test
  void testGetInvalidDefinitionId() {
    final UUID invalidDefinitionId = UUID.fromString("1a7c360c-1289-4b96-a171-2ac1c86fb7ca");

    assertThrows(
        ConfigNotFoundException.class,
        () -> localDefinitionsProvider.getSourceDefinition(invalidDefinitionId));
    assertThrows(
        ConfigNotFoundException.class,
        () -> localDefinitionsProvider.getDestinationDefinition(invalidDefinitionId));
  }

  @Test
  void testGetSourceDefinitions() {
    final List<StandardSourceDefinition> sourceDefinitions = localDefinitionsProvider.getSourceDefinitions();
    assertFalse(sourceDefinitions.isEmpty());
    assertTrue(sourceDefinitions.stream().allMatch(sourceDef -> sourceDef.getProtocolVersion().length() > 0));
  }

  @Test
  void testGetDestinationDefinitions() {
    final List<StandardDestinationDefinition> destinationDefinitions = localDefinitionsProvider.getDestinationDefinitions();
    assertFalse(destinationDefinitions.isEmpty());
    assertTrue(destinationDefinitions.stream().allMatch(sourceDef -> sourceDef.getProtocolVersion().length() > 0));
  }

}
