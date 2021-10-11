/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.normalization;

import com.google.common.collect.ImmutableMap;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.workers.normalization.DefaultNormalizationRunner.DestinationType;
import io.airbyte.workers.process.ProcessFactory;
import java.util.Map;

public class NormalizationRunnerFactory {

  public static final String BASE_NORMALIZATION_IMAGE_NAME = "airbyte/normalization";

  static final Map<String, String> NORMALIZATION_MAPPING =
      ImmutableMap.<String, String>builder()
          .put("airbyte/destination-bigquery", BASE_NORMALIZATION_IMAGE_NAME)
          .put("airbyte/destination-mssql", "airbyte/normalization-mssql")
          .put("airbyte/destination-mysql", "airbyte/normalization-mysql")
          .put("airbyte/destination-oracle", "airbyte/normalization-oracle")
          .put("airbyte/destination-postgres", BASE_NORMALIZATION_IMAGE_NAME)
          .put("airbyte/destination-postgres-strict-encrypt", BASE_NORMALIZATION_IMAGE_NAME)
          .put("airbyte/destination-redshift", BASE_NORMALIZATION_IMAGE_NAME)
          .put("airbyte/destination-snowflake", BASE_NORMALIZATION_IMAGE_NAME)
          .build();

  static final Map<String, DefaultNormalizationRunner.DestinationType> DESTINATION_TYPE_MAPPING =
      ImmutableMap.<String, DefaultNormalizationRunner.DestinationType>builder()
          .put("airbyte/destination-bigquery", DefaultNormalizationRunner.DestinationType.BIGQUERY)
          .put("airbyte/destination-mssql", DefaultNormalizationRunner.DestinationType.MSSQL)
          .put("airbyte/destination-mysql", DefaultNormalizationRunner.DestinationType.MYSQL)
          .put("airbyte/destination-oracle", DestinationType.ORACLE)
          .put("airbyte/destination-postgres", DefaultNormalizationRunner.DestinationType.POSTGRES)
          .put("airbyte/destination-postgres-strict-encrypt", DefaultNormalizationRunner.DestinationType.POSTGRES)
          .put("airbyte/destination-redshift", DefaultNormalizationRunner.DestinationType.REDSHIFT)
          .put("airbyte/destination-snowflake", DefaultNormalizationRunner.DestinationType.SNOWFLAKE)
          .build();

  public static NormalizationRunner create(final String imageName, final ProcessFactory processFactory) {
    final String imageNameWithoutTag = imageName.split(":")[0];
    if (DESTINATION_TYPE_MAPPING.containsKey(imageNameWithoutTag) && NORMALIZATION_MAPPING.containsKey(imageNameWithoutTag)) {
      final Configs configs = new EnvConfigs();
      return new DefaultNormalizationRunner(
          DESTINATION_TYPE_MAPPING.get(imageNameWithoutTag),
          processFactory,
          String.format("%s:%s", NORMALIZATION_MAPPING.get(imageNameWithoutTag), configs.getAirbyteVersion()));
    } else {
      throw new IllegalStateException(
          String.format("Requested normalization for %s, but it is not included in the normalization mappings.", imageName));
    }
  }

}
