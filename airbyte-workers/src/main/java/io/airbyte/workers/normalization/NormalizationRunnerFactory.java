/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.normalization;

import com.google.common.collect.ImmutableMap;
import io.airbyte.workers.process.ProcessFactory;
import java.util.Map;

public class NormalizationRunnerFactory {

  static final Map<String, DefaultNormalizationRunner.DestinationType> NORMALIZATION_MAPPING =
      ImmutableMap.<String, DefaultNormalizationRunner.DestinationType>builder()
          .put("airbyte/destination-bigquery", DefaultNormalizationRunner.DestinationType.BIGQUERY)
          .put("airbyte/destination-postgres", DefaultNormalizationRunner.DestinationType.POSTGRES)
          .put("airbyte/destination-postgres-strict-encrypt", DefaultNormalizationRunner.DestinationType.POSTGRES)
          .put("airbyte/destination-redshift", DefaultNormalizationRunner.DestinationType.REDSHIFT)
          .put("airbyte/destination-snowflake", DefaultNormalizationRunner.DestinationType.SNOWFLAKE)
          .put("airbyte/destination-mysql", DefaultNormalizationRunner.DestinationType.MYSQL)
          .build();

  public static NormalizationRunner create(final String imageName, final ProcessFactory processFactory) {

    final String imageNameWithoutTag = imageName.split(":")[0];

    if (NORMALIZATION_MAPPING.containsKey(imageNameWithoutTag)) {
      return new DefaultNormalizationRunner(NORMALIZATION_MAPPING.get(imageNameWithoutTag), processFactory);
    } else {
      throw new IllegalStateException(
          String.format("Requested normalization for %s, but it is not included in the normalization mapping.", imageName));
    }
  }

}
