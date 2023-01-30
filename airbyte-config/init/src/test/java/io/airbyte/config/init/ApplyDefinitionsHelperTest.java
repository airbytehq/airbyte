/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoMoreInteractions;
import static org.mockito.Mockito.when;

import io.airbyte.commons.version.AirbyteProtocolVersionRange;
import io.airbyte.commons.version.Version;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

/**
 * Test suite for the {@link ApplyDefinitionsHelper} class.
 */
class ApplyDefinitionsHelperTest {

  private static final UUID SOURCE_DEF_ID1 = UUID.randomUUID();
  private static final UUID DEST_DEF_ID2 = UUID.randomUUID();
  private static final String CONNECT_NAME1 = "connector1";
  private static final String CONNECT_NAME2 = "connector2";
  private static final String DOCUMENTATION_URL = "https://wwww.example.com";
  private static final String DOCKER_REPOSITORY = "airbyte/connector";
  private static final String DOCKER_TAG = "0.1.0";
  private static final String PROTOCOL_VERSION_1 = "1.0.0";
  private static final String PROTOCOL_VERSION_2 = "2.0.0";
  public static final StandardSourceDefinition SOURCE_DEF1 = new StandardSourceDefinition()
      .withSourceDefinitionId(SOURCE_DEF_ID1)
      .withDockerRepository(DOCKER_REPOSITORY)
      .withDockerImageTag(DOCKER_TAG)
      .withName(CONNECT_NAME1)
      .withDocumentationUrl(DOCUMENTATION_URL)
      .withSpec(new ConnectorSpecification().withProtocolVersion(PROTOCOL_VERSION_1));
  public static final StandardSourceDefinition SOURCE_DEF2 = new StandardSourceDefinition()
      .withSourceDefinitionId(SOURCE_DEF_ID1)
      .withDockerRepository(DOCKER_REPOSITORY)
      .withDockerImageTag(DOCKER_TAG)
      .withName(CONNECT_NAME2)
      .withDocumentationUrl(DOCUMENTATION_URL)
      .withSpec(new ConnectorSpecification().withProtocolVersion(PROTOCOL_VERSION_2));

  public static final StandardDestinationDefinition DEST_DEF1 = new StandardDestinationDefinition()
      .withDestinationDefinitionId(DEST_DEF_ID2)
      .withDockerRepository(DOCKER_REPOSITORY)
      .withDockerImageTag(DOCKER_TAG)
      .withName(CONNECT_NAME1)
      .withDocumentationUrl(DOCUMENTATION_URL)
      .withSpec(new ConnectorSpecification().withProtocolVersion(PROTOCOL_VERSION_2));

  public static final StandardDestinationDefinition DEST_DEF2 = new StandardDestinationDefinition()
      .withDestinationDefinitionId(DEST_DEF_ID2)
      .withDockerRepository(DOCKER_REPOSITORY)
      .withDockerImageTag(DOCKER_TAG)
      .withName(CONNECT_NAME2)
      .withDocumentationUrl(DOCUMENTATION_URL)
      .withSpec(new ConnectorSpecification().withProtocolVersion(PROTOCOL_VERSION_1));

  private ConfigRepository configRepository;
  private DefinitionsProvider definitionsProvider;
  private JobPersistence jobPersistence;
  private ApplyDefinitionsHelper applyDefinitionsHelper;

  @BeforeEach
  void setup() throws IOException {
    configRepository = mock(ConfigRepository.class);
    definitionsProvider = mock(DefinitionsProvider.class);
    jobPersistence = mock(JobPersistence.class);

    applyDefinitionsHelper = new ApplyDefinitionsHelper(configRepository, Optional.of(definitionsProvider), jobPersistence);

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

  @ParameterizedTest
  @ValueSource(booleans = {false, true})
  void testDefinitionsFiltering(final boolean updateAll) throws JsonValidationException, IOException {
    when(jobPersistence.getCurrentProtocolVersionRange())
        .thenReturn(Optional.of(new AirbyteProtocolVersionRange(new Version("2.0.0"), new Version("3.0.0"))));

    when(definitionsProvider.getSourceDefinitions()).thenReturn(List.of(SOURCE_DEF1, SOURCE_DEF2));
    when(definitionsProvider.getDestinationDefinitions()).thenReturn(List.of(DEST_DEF1, DEST_DEF2));

    applyDefinitionsHelper.apply(updateAll);

    if (updateAll) {
      verify(configRepository).writeStandardSourceDefinition(SOURCE_DEF2);
      verify(configRepository).writeStandardDestinationDefinition(DEST_DEF1);
      verifyNoMoreInteractions(configRepository);
    } else {
      verify(configRepository).seedActorDefinitions(List.of(SOURCE_DEF2), List.of(DEST_DEF1));
    }
  }

  @Test
  void testMissingDefinitionsProvider() {
    final ApplyDefinitionsHelper helper = new ApplyDefinitionsHelper(configRepository, Optional.empty(), jobPersistence);
    assertDoesNotThrow(() -> helper.apply());
  }

}
