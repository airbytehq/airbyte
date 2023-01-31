/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

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
    Assertions.assertTrue(NormalizationActivityImpl.normalizationSupportsV1DataTypes(withNormalizationVersion("protocolv1")));
  }

  private IntegrationLauncherConfig withNormalizationVersion(final String version) {
    return new IntegrationLauncherConfig()
        .withNormalizationDockerImage("normalization:" + version);
  }

}
