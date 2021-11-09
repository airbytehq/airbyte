/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.normalization;

import com.google.common.collect.ImmutableMap;
import io.airbyte.workers.normalization.DefaultNormalizationRunner.DestinationType;
import io.airbyte.workers.process.ProcessFactory;
import java.util.Map;
import org.apache.commons.lang3.tuple.ImmutablePair;

public class NormalizationRunnerFactory {

  public static final String BASE_NORMALIZATION_IMAGE_NAME = "airbyte/normalization";
  public static final String NORMALIZATION_VERSION = "0.1.59";

  static final Map<String, ImmutablePair<String, DefaultNormalizationRunner.DestinationType>> NORMALIZATION_MAPPING =
      ImmutableMap.<String, ImmutablePair<String, DefaultNormalizationRunner.DestinationType>>builder()
          .put("airbyte/destination-bigquery", ImmutablePair.of(BASE_NORMALIZATION_IMAGE_NAME, DefaultNormalizationRunner.DestinationType.BIGQUERY))
          .put("airbyte/destination-mssql", ImmutablePair.of("airbyte/normalization-mssql", DestinationType.MSSQL))
          .put("airbyte/destination-mssql-strict-encrypt", ImmutablePair.of("airbyte/normalization-mssql", DestinationType.MSSQL))
          .put("airbyte/destination-mysql", ImmutablePair.of("airbyte/normalization-mysql", DestinationType.MYSQL))
          .put("airbyte/destination-mysql-strict-encrypt", ImmutablePair.of("airbyte/normalization-mysql", DestinationType.MYSQL))
          .put("airbyte/destination-oracle", ImmutablePair.of("airbyte/normalization-oracle", DestinationType.ORACLE))
          .put("airbyte/destination-oracle-strict-encrypt", ImmutablePair.of("airbyte/normalization-oracle", DestinationType.ORACLE))
          .put("airbyte/destination-postgres", ImmutablePair.of(BASE_NORMALIZATION_IMAGE_NAME, DestinationType.POSTGRES))
          .put("airbyte/destination-postgres-strict-encrypt", ImmutablePair.of(BASE_NORMALIZATION_IMAGE_NAME, DestinationType.POSTGRES))
          .put("airbyte/destination-redshift", ImmutablePair.of(BASE_NORMALIZATION_IMAGE_NAME, DestinationType.REDSHIFT))
          .put("airbyte/destination-snowflake", ImmutablePair.of(BASE_NORMALIZATION_IMAGE_NAME, DestinationType.SNOWFLAKE))
          .build();

  public static NormalizationRunner create(final String imageName, final ProcessFactory processFactory) {
    final String imageNameWithoutTag = imageName.split(":")[0];
    if (NORMALIZATION_MAPPING.containsKey(imageNameWithoutTag)) {
      final var valuePair = NORMALIZATION_MAPPING.get(imageNameWithoutTag);
      return new DefaultNormalizationRunner(
          valuePair.getRight(),
          processFactory,
          String.format("%s:%s", valuePair.getLeft(), NORMALIZATION_VERSION));
    } else {
      throw new IllegalStateException(
          String.format("Requested normalization for %s, but it is not included in the normalization mappings.", imageName));
    }
  }

}
