/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.normalization;

import com.google.common.collect.ImmutableMap;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.normalization.DefaultNormalizationRunner.DestinationType;
import io.airbyte.workers.process.ProcessFactory;
import java.util.Map;
import org.apache.commons.lang3.tuple.ImmutablePair;

public class NormalizationRunnerFactory {

  public static final String BASE_NORMALIZATION_IMAGE_NAME = "yuanrui/normalization";
  public static final String NORMALIZATION_VERSION = "0.2.22";

  static final Map<String, ImmutablePair<String, DefaultNormalizationRunner.DestinationType>> NORMALIZATION_MAPPING =
      ImmutableMap.<String, ImmutablePair<String, DefaultNormalizationRunner.DestinationType>>builder()
          // map destination connectors (alphabetically) to their expected normalization settings
          .put("yuanrui2014/destination-bigquery",
              ImmutablePair.of(BASE_NORMALIZATION_IMAGE_NAME, DefaultNormalizationRunner.DestinationType.BIGQUERY))
          .put("yuanrui2014/destination-bigquery-denormalized",
              ImmutablePair.of(BASE_NORMALIZATION_IMAGE_NAME, DefaultNormalizationRunner.DestinationType.BIGQUERY))
          .put("yuanrui2014/destination-clickhouse", ImmutablePair.of("yuanrui2014/normalization-clickhouse", DestinationType.CLICKHOUSE))
          .put("yuanrui2014/destination-clickhouse-strict-encrypt",
              ImmutablePair.of("yuanrui2014/normalization-clickhouse", DestinationType.CLICKHOUSE))
          .put("yuanrui2014/destination-mssql", ImmutablePair.of("yuanrui2014/normalization-mssql", DestinationType.MSSQL))
          .put("yuanrui2014/destination-mssql-strict-encrypt", ImmutablePair.of("yuanrui2014/normalization-mssql", DestinationType.MSSQL))
          .put("yuanrui2014/destination-mysql", ImmutablePair.of("yuanrui2014/normalization-mysql", DestinationType.MYSQL))
          .put("yuanrui2014/destination-mysql-strict-encrypt", ImmutablePair.of("yuanrui2014/normalization-mysql", DestinationType.MYSQL))
          .put("yuanrui2014/destination-oracle", ImmutablePair.of("yuanrui2014/normalization-oracle", DestinationType.ORACLE))
          .put("yuanrui2014/destination-oracle-strict-encrypt", ImmutablePair.of("yuanrui2014/normalization-oracle", DestinationType.ORACLE))
          .put("yuanrui2014/destination-postgres", ImmutablePair.of(BASE_NORMALIZATION_IMAGE_NAME, DestinationType.POSTGRES))
          .put("yuanrui2014/destination-postgres-strict-encrypt", ImmutablePair.of(BASE_NORMALIZATION_IMAGE_NAME, DestinationType.POSTGRES))
          .put("yuanrui2014/destination-redshift", ImmutablePair.of("yuanrui2014/normalization-redshift", DestinationType.REDSHIFT))
          .put("yuanrui2014/destination-snowflake", ImmutablePair.of("yuanrui2014/normalization-snowflake", DestinationType.SNOWFLAKE))
          .put("yuanrui2014/destination-tidb", ImmutablePair.of("yuanrui2014/normalization-tidb", DestinationType.TIDB))
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
