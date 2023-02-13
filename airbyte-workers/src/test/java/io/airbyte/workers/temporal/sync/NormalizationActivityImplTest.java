/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class NormalizationActivityImplTest {

  @Test
  void checkNormalizationDataTypesSupportFromVersionString() {
    Assertions.assertFalse(NormalizationActivityImpl.normalizationSupportsV1DataTypes(withNormalizationVersion("0.2.5")));
    Assertions.assertFalse(NormalizationActivityImpl.normalizationSupportsV1DataTypes(withNormalizationVersion("0.1.1")));
    Assertions.assertTrue(NormalizationActivityImpl.normalizationSupportsV1DataTypes(withNormalizationVersion("0.3.0")));
    Assertions.assertFalse(NormalizationActivityImpl.normalizationSupportsV1DataTypes(withNormalizationVersion("0.4.1")));
    Assertions.assertFalse(NormalizationActivityImpl.normalizationSupportsV1DataTypes(withNormalizationVersion("dev")));
    Assertions.assertFalse(NormalizationActivityImpl.normalizationSupportsV1DataTypes(withNormalizationVersion("protocolv1")));
    Assertions.assertFalse(NormalizationActivityImpl.normalizationSupportsV1DataTypes(withNormalizationVersion("strict_comparison")));
  }

  @Test
  void checkNormalizationTagReplacement() {
    final FeatureFlags featureFlags = mock(FeatureFlags.class);
    when(featureFlags.strictComparisonNormalizationTag()).thenReturn("strict_comparison");

    final IntegrationLauncherConfig config = withNormalizationVersion("0.2.25");
    NormalizationActivityImpl.replaceNormalizationImageTag(config, "strict_comparison");
    assertEquals("normalization:strict_comparison", config.getNormalizationDockerImage());
  }

  private IntegrationLauncherConfig withNormalizationVersion(final String version) {
    return new IntegrationLauncherConfig()
        .withNormalizationDockerImage("normalization:" + version);
  }

}
