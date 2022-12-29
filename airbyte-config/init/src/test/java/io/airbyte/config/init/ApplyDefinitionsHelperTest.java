/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoMoreInteractions;
import static org.mockito.Mockito.when;

import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ApplyDefinitionsHelperTest {

  private static final UUID SOURCE_DEF_ID1 = UUID.randomUUID();
  private static final UUID DEST_DEF_ID2 = UUID.randomUUID();
  private static final String CONNECT_NAME1 = "connector1";
  private static final String CONNECT_NAME2 = "connector2";
  private static final String DOCUMENTATION_URL = "https://wwww.example.com";
  private static final String DOCKER_REPOSITORY = "airbyte/connector";
  private static final String DOCKER_TAG = "0.1.0";
  public static final StandardSourceDefinition SOURCE_DEF1 = new StandardSourceDefinition()
      .withSourceDefinitionId(SOURCE_DEF_ID1)
      .withDockerRepository(DOCKER_REPOSITORY)
      .withDockerImageTag(DOCKER_TAG)
      .withName(CONNECT_NAME1)
      .withDocumentationUrl(DOCUMENTATION_URL);
  public static final StandardSourceDefinition SOURCE_DEF2 = new StandardSourceDefinition()
      .withSourceDefinitionId(SOURCE_DEF_ID1)
      .withDockerRepository(DOCKER_REPOSITORY)
      .withDockerImageTag(DOCKER_TAG)
      .withName(CONNECT_NAME2)
      .withDocumentationUrl(DOCUMENTATION_URL);
  public static final StandardDestinationDefinition DEST_DEF1 = new StandardDestinationDefinition()
      .withDestinationDefinitionId(DEST_DEF_ID2)
      .withDockerRepository(DOCKER_REPOSITORY)
      .withDockerImageTag(DOCKER_TAG)
      .withName(CONNECT_NAME1)
      .withDocumentationUrl(DOCUMENTATION_URL);
  public static final StandardDestinationDefinition DEST_DEF2 = new StandardDestinationDefinition()
      .withDestinationDefinitionId(DEST_DEF_ID2)
      .withDockerRepository(DOCKER_REPOSITORY)
      .withDockerImageTag(DOCKER_TAG)
      .withName(CONNECT_NAME2)
      .withDocumentationUrl(DOCUMENTATION_URL);

  private ConfigRepository configRepository;
  private DefinitionsProvider definitionsProvider;
  private ApplyDefinitionsHelper applyDefinitionsHelper;

  @BeforeEach
  void setup() throws JsonValidationException, IOException {
    configRepository = mock(ConfigRepository.class);
    definitionsProvider = mock(DefinitionsProvider.class);

    applyDefinitionsHelper = new ApplyDefinitionsHelper(configRepository, definitionsProvider);

    // default calls to empty.
    when(configRepository.listStandardDestinationDefinitions(true)).thenReturn(Collections.emptyList());
    when(configRepository.listStandardSourceDefinitions(true)).thenReturn(Collections.emptyList());
    when(definitionsProvider.getDestinationDefinitions()).thenReturn(Collections.emptyList());
    when(definitionsProvider.getSourceDefinitions()).thenReturn(Collections.emptyList());
  }

  @Test
  void testUpdateAllAddRecord() throws JsonValidationException, IOException {
    when(definitionsProvider.getSourceDefinitions()).thenReturn(List.of(SOURCE_DEF1));
    when(definitionsProvider.getDestinationDefinitions()).thenReturn(List.of(DEST_DEF1));

    applyDefinitionsHelper.apply(true);

    verify(configRepository).writeStandardSourceDefinition(SOURCE_DEF1);
    verify(configRepository).writeStandardDestinationDefinition(DEST_DEF1);
    verify(definitionsProvider).getDestinationDefinitions();
    verify(definitionsProvider).getSourceDefinitions();
    verifyNoMoreInteractions(configRepository);
    verifyNoMoreInteractions(definitionsProvider);
  }

  @Test
  void testUpdateAllMutateRecord() throws JsonValidationException, IOException {
    when(configRepository.listStandardSourceDefinitions(true)).thenReturn(List.of(SOURCE_DEF2));
    when(configRepository.listStandardDestinationDefinitions(true)).thenReturn(List.of(DEST_DEF2));

    when(definitionsProvider.getSourceDefinitions()).thenReturn(List.of(SOURCE_DEF1));
    when(definitionsProvider.getDestinationDefinitions()).thenReturn(List.of(DEST_DEF1));

    applyDefinitionsHelper.apply(true);

    verify(configRepository).writeStandardSourceDefinition(SOURCE_DEF1);
    verify(configRepository).writeStandardDestinationDefinition(DEST_DEF1);
    verify(definitionsProvider).getDestinationDefinitions();
    verify(definitionsProvider).getSourceDefinitions();
    verifyNoMoreInteractions(configRepository);
    verifyNoMoreInteractions(definitionsProvider);
  }

  @Test
  void testUpdateAllNoDeleteRecord() throws JsonValidationException, IOException {
    when(configRepository.listStandardSourceDefinitions(true)).thenReturn(List.of(SOURCE_DEF1));
    when(configRepository.listStandardDestinationDefinitions(true)).thenReturn(List.of(DEST_DEF1));

    applyDefinitionsHelper.apply(true);

    verify(definitionsProvider).getDestinationDefinitions();
    verify(definitionsProvider).getSourceDefinitions();
    verifyNoMoreInteractions(configRepository);
    verifyNoMoreInteractions(definitionsProvider);
  }

  @Test
  void testApplyOSS() throws JsonValidationException, IOException {
    when(definitionsProvider.getSourceDefinitions()).thenReturn(List.of(SOURCE_DEF1));
    when(definitionsProvider.getDestinationDefinitions()).thenReturn(List.of(DEST_DEF1));

    applyDefinitionsHelper.apply();

    verify(configRepository).seedActorDefinitions(List.of(SOURCE_DEF1), List.of(DEST_DEF1));
    verify(definitionsProvider).getDestinationDefinitions();
    verify(definitionsProvider).getSourceDefinitions();
    verifyNoMoreInteractions(configRepository);
    verifyNoMoreInteractions(definitionsProvider);
  }

}
