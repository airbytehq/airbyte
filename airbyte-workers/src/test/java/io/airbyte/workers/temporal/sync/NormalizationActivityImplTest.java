/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class NormalizationActivityImplTest {

  @Test
  void checkNormalizationDataTypesSupportFromVersionString() {
    Assertions.assertFalse(NormalizationActivityImpl.normalizationSupportsV1DataTypes(withNormalizationVersion("0.2.5")));
    Assertions.assertFalse(NormalizationActivityImpl.normalizationSupportsV1DataTypes(withNormalizationVersion("0.1.1")));
    Assertions.assertTrue(NormalizationActivityImpl.normalizationSupportsV1DataTypes(withNormalizationVersion("0.3.0")));
    Assertions.assertTrue(NormalizationActivityImpl.normalizationSupportsV1DataTypes(withNormalizationVersion("0.4.1")));
    Assertions.assertTrue(NormalizationActivityImpl.normalizationSupportsV1DataTypes(withNormalizationVersion("dev")));
    Assertions.assertFalse(NormalizationActivityImpl.normalizationSupportsV1DataTypes(withNormalizationVersion("protocolv1")));
  }

  @Test
  void checkNormalizationTagReplacement() {
    final IntegrationLauncherConfig config1 = withNormalizationVersion("0.2.25");
    NormalizationActivityImpl.activateStrictNormalizationComparisonIfPossible(config1);
    assertEquals("normalization:0.4.0", config1.getNormalizationDockerImage());

    final IntegrationLauncherConfig config2 = withNormalizationVersion("0.2.26");
    NormalizationActivityImpl.activateStrictNormalizationComparisonIfPossible(config2);
    assertEquals("normalization:0.2.26", config2.getNormalizationDockerImage());
  }

  private IntegrationLauncherConfig withNormalizationVersion(final String version) {
    return new IntegrationLauncherConfig()
        .withNormalizationDockerImage("normalization:" + version);
  }

}
