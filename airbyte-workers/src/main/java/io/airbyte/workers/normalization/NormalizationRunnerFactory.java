/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.normalization;

import com.google.common.collect.ImmutableMap;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.normalization.DefaultNormalizationRunner.DestinationType;
import io.airbyte.workers.process.ProcessFactory;
import java.util.Map;
import org.apache.commons.lang3.tuple.ImmutablePair;

public class NormalizationRunnerFactory {

  public static final String BASE_NORMALIZATION_IMAGE_NAME = "airbyte/normalization";
  public static final String NORMALIZATION_VERSION = "0.1.78";

  static final Map<String, ImmutablePair<String, DefaultNormalizationRunner.DestinationType>> NORMALIZATION_MAPPING =
      ImmutableMap.<String, ImmutablePair<String, DefaultNormalizationRunner.DestinationType>>builder()
          // map destination connectors (alphabetically) to their expected normalization settings
          .put("airbyte/destination-bigquery", ImmutablePair.of(BASE_NORMALIZATION_IMAGE_NAME, DefaultNormalizationRunner.DestinationType.BIGQUERY))
          .put("airbyte/destination-bigquery-denormalized",
              ImmutablePair.of(BASE_NORMALIZATION_IMAGE_NAME, DefaultNormalizationRunner.DestinationType.BIGQUERY))
          .put("airbyte/destination-clickhouse", ImmutablePair.of("airbyte/normalization-clickhouse", DestinationType.CLICKHOUSE))
          .put("airbyte/destination-clickhouse-strict-encrypt", ImmutablePair.of("airbyte/normalization-clickhouse", DestinationType.CLICKHOUSE))
          .put("airbyte/destination-mssql", ImmutablePair.of("airbyte/normalization-mssql", DestinationType.MSSQL))
          .put("airbyte/destination-mssql-strict-encrypt", ImmutablePair.of("airbyte/normalization-mssql", DestinationType.MSSQL))
          .put("airbyte/destination-mysql", ImmutablePair.of("airbyte/normalization-mysql", DestinationType.MYSQL))
          .put("airbyte/destination-mysql-strict-encrypt", ImmutablePair.of("airbyte/normalization-mysql", DestinationType.MYSQL))
          .put("airbyte/destination-oracle", ImmutablePair.of("airbyte/normalization-oracle", DestinationType.ORACLE))
          .put("airbyte/destination-oracle-strict-encrypt", ImmutablePair.of("airbyte/normalization-oracle", DestinationType.ORACLE))
          .put("airbyte/destination-postgres", ImmutablePair.of(BASE_NORMALIZATION_IMAGE_NAME, DestinationType.POSTGRES))
          .put("airbyte/destination-postgres-strict-encrypt", ImmutablePair.of(BASE_NORMALIZATION_IMAGE_NAME, DestinationType.POSTGRES))
          .put("airbyte/destination-redshift", ImmutablePair.of("airbyte/normalization-redshift", DestinationType.REDSHIFT))
          .put("airbyte/destination-snowflake", ImmutablePair.of("airbyte/normalization-snowflake", DestinationType.SNOWFLAKE))
          .build();

  public static NormalizationRunner create(final WorkerConfigs workerConfigs,
                                           final String connectorImageName,
                                           final ProcessFactory processFactory,
                                           final String normalizationVersion) {
    final var valuePair = getNormalizationInfoForConnector(connectorImageName);
    return new DefaultNormalizationRunner(
        workerConfigs,
        valuePair.getRight(),
        processFactory,
        String.format("%s:%s", valuePair.getLeft(), normalizationVersion));
  }

  public static ImmutablePair<String, DestinationType> getNormalizationInfoForConnector(final String connectorImageName) {
    final String imageNameWithoutTag = connectorImageName.contains(":") ? connectorImageName.split(":")[0] : connectorImageName;
    if (NORMALIZATION_MAPPING.containsKey(imageNameWithoutTag)) {
      return NORMALIZATION_MAPPING.get(imageNameWithoutTag);
    } else {
      throw new IllegalStateException(
          String.format("Requested normalization for %s, but it is not included in the normalization mappings.", connectorImageName));
    }
  }

}
